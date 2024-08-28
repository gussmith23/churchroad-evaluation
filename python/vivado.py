"""Utilities for running Vivado."""

import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from time import time
from typing import Any, Dict, Optional, Tuple, Union
from util import count_resources_in_verilog_src
import yaml


def xilinx_ultrascale_plus_vivado_synthesis(
    instr_src_file: Union[str, Path],
    synth_opt_place_route_output_filepath: Union[str, Path],
    module_name: str,
    tcl_script_filepath: Union[str, Path],
    log_path: Union[str, Path],
    summary_filepath: Union[str, Path],
    part_name: str,
    directive: str = "default",
    flags: str = '',
    synth_design: bool = True,
    opt_design: bool = True,
    synth_design_rtl_flags: bool = False,
    clock_info: Optional[Tuple[str, float, Tuple[float, float]]] = None,
    place_directive: str = "default",
    route_directive: str = "default",
    extra_summary_fields: Dict[str, Any] = {},
    max_threads: int = 1,
    attempts: int = 1,
):
    """Synthesize with Xilinx Vivado.

    NOTE: We could use fud to do this; fud will allow you to provide a tcl and
    xdc file, and will parse out the results for you (which I still have to do.)

    Args:
        tcl_script_filepath: Output filepath where .tcl script will be written.
        directive: What to pass to the -directive arg of Vivado's synth_design
          command.
        synth_design: Whether or not to run Vivado's synth_design
          command.
        opt_design: Whether or not to run Vivado's opt_design command.
        synth_design_rtl_flags: Whether or not to pass the -rtl and all
          -rtl_skip_* flags to synth_design.
        summary_filepath: Output JSON summary filepath.
        clock_info: Clock name and period in nanoseconds. When provided, a
          constraint file will be created and loaded using the given clock
          information.
        extra_summary_fields: Extra fields to add to the summary JSON.
        attempts: Number of times to attempt running Vivado synthesis, in the
          case where Vivado fails (which occurs ~once per evaluation run).
        part_name: The part name to use for synthesis.
    """
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    synth_opt_place_route_output_filepath = Path(synth_opt_place_route_output_filepath)
    synth_opt_place_route_output_filepath.parent.mkdir(parents=True, exist_ok=True)
    tcl_script_filepath = Path(tcl_script_filepath)
    tcl_script_filepath.parent.mkdir(parents=True, exist_ok=True)
    xdc_filepath = tcl_script_filepath.with_suffix(".xdc")

    with open(xdc_filepath, "w") as f:
        if clock_info:
            clock_name, clock_period, (rising_edge, falling_edge) = clock_info
            # We use 7 because that's what the Calyx team used for their eval.
            # We could try to refine the clock period per design. Rachit's notes:
            #
            set_clock_command = f"create_clock -period {clock_period} -name {clock_name} -waveform {{{rising_edge} {falling_edge}}} [get_ports {clock_name}]"
        else:
            set_clock_command = "# No clock provided; not creating a clock."
        f.write(set_clock_command)

    # Generate and write the TCL script.
    with open(tcl_script_filepath, "w") as f:
        synth_design_command = (
            f"synth_design -mode out_of_context -directive {directive} {flags}"
            + (
                " -rtl -rtl_skip_mlo -rtl_skip_ip -rtl_skip_constraints"
                if synth_design_rtl_flags
                else ""
            )
        )

        f.write(
            f"""
set sv_source_file {str(instr_src_file)}
set modname {module_name}
set synth_opt_place_route_output_filepath {synth_opt_place_route_output_filepath}

# Part number chosen at Luis's suggestion. Can be changed to another UltraScale+
# part.
set_part {part_name}

# Set number of threads.
set_param general.maxThreads {max_threads}

read_verilog -sv ${{sv_source_file}}
set_property top ${{modname}} [current_fileset]
{synth_design_command if synth_design else f"# {synth_design_command}"}
read_xdc -mode out_of_context {xdc_filepath}
{"opt_design" if opt_design else "# opt_design"}
place_design -directive {place_directive}
# route_design causes problems when run inside the Docker container. Originally,
# I used -release_memory, because I thought the issue was memory related. This
# fixed the issue, but only because (as I later discovered) -release_memory
# doesn't actually run routing! So we need to see if the crash still occurs, 
# and if it does, we need another way around it.
route_design -directive {route_directive}
write_verilog -force ${{synth_opt_place_route_output_filepath}}
report_timing_summary
report_utilization
"""
        )

    def _run_vivado():
        # Synthesis with Vivado.
        with open(log_path, "w") as logfile:
            logging.info("Running Vivado synthesis/place/route on %s", instr_src_file)

            # Setting this environment variable prevents an error when running
            # Vivado route_design inside a Docker container. See:
            # https://community.flexera.com/t5/InstallAnywhere-Forum/Issues-when-running-Xilinx-tools-or-Other-vendor-tools-in-docker/m-p/245820#M10647
            env = os.environ.copy()
            ld_preload_previous_value = env["LD_PRELOAD"] if "LD_PRELOAD" in env else ""
            env["LD_PRELOAD"] = (
                f"/lib/x86_64-linux-gnu/libudev.so.1:{ld_preload_previous_value}"
            )

            start_time = time()
            completed_process = subprocess.run(
                [
                    "vivado",
                    # -stack 2000 is a way to sometimes prevent mysterious Vivado
                    # crashes...
                    "-stack",
                    "2000",
                    "-mode",
                    "batch",
                    "-source",
                    tcl_script_filepath,
                ],
                check=False,
                stdout=logfile,
                stderr=logfile,
                env=env,
            )
            end_time = time()
        return (completed_process, end_time - start_time)

    completed_process, elapsed_time = _run_vivado()
    attempts_remaining = attempts - 1
    # If Vivado failed, try again.
    while completed_process.returncode != 0 and attempts_remaining > 0:
        logging.error(
            "Vivado synthesis failed with return code %d. Attempts remaining: %d. Trying again...",
            completed_process.returncode,
            attempts_remaining,
        )
        completed_process, elapsed_time = _run_vivado()
        attempts_remaining = attempts_remaining - 1

    completed_process.check_returncode()

    summary = count_resources_in_verilog_src(
        verilog_src=synth_opt_place_route_output_filepath.read_text(),
        module_name=module_name,
    )

    assert "time_s" not in summary
    summary["time_s"] = elapsed_time

    for key in extra_summary_fields:
        assert key not in summary
        summary[key] = extra_summary_fields[key]

    json.dump(
        summary,
        fp=open(summary_filepath, "w"),
    )


def make_xilinx_ultrascale_plus_vivado_synthesis_task_opt(
    input_filepath: Union[str, Path],
    output_dirpath: Union[str, Path],
    module_name: str,
    part_name: str,
    flags: str = '',
    clock_info: Optional[Tuple[str, float]] = None,
    name: Optional[str] = None,
    directive: Optional[str] = None,
    fail_if_constraints_not_met: Optional[bool] = None,
    extra_summary_fields: Dict[str, Any] = {},
    attempts: Optional[int] = None,
):
    """Wrapper over Vivado synthesis function which creates a DoIt task.

    This task will run Vivado with optimizations.

    Returns:
        (task, (json_filepath, verilog_filepath, log_filepath, tcl_filepath)).
    """

    input_filepath = Path(input_filepath)
    output_dirpath = Path(output_dirpath)

    output_filepaths = {
        "synth_opt_place_route_output_filepath": output_dirpath / input_filepath.name,
        "log_filepath": output_dirpath / f"{input_filepath.stem}.log",
        "tcl_script_filepath": output_dirpath / f"{input_filepath.stem}.tcl",
        "summary_filepath": output_dirpath / f"{input_filepath.stem}_summary.json",
    }

    synth_args = {
        "instr_src_file": input_filepath,
        "synth_opt_place_route_output_filepath": output_filepaths[
            "synth_opt_place_route_output_filepath"
        ],
        "module_name": module_name,
        "log_path": output_filepaths["log_filepath"],
        "tcl_script_filepath": output_filepaths["tcl_script_filepath"],
        "opt_design": True,
        "synth_design": True,
        "flags": flags,
        "summary_filepath": output_filepaths["summary_filepath"],
        "extra_summary_fields": extra_summary_fields,
        "part_name": part_name,
    }

    if directive is not None:
        synth_args["directive"] = directive
    if clock_info is not None:
        synth_args["clock_info"] = clock_info
    if fail_if_constraints_not_met is not None:
        synth_args["fail_if_constraints_not_met"] = fail_if_constraints_not_met
    if attempts is not None:
        synth_args["attempts"] = attempts
    if flags:
        synth_args["flags"] = flags

    task = {
        "actions": [
            (
                xilinx_ultrascale_plus_vivado_synthesis,
                [],
                synth_args,
            )
        ],
        "file_dep": [input_filepath],
        "targets": list(output_filepaths.values()),
    }

    if name is not None:
        task["name"] = name

    return (
        task,
        (
            output_filepaths["summary_filepath"],
            output_filepaths["synth_opt_place_route_output_filepath"],
            output_filepaths["log_filepath"],
            output_filepaths["tcl_script_filepath"],
        ),
    )


def make_xilinx_ultrascale_plus_vivado_synthesis_task_noopt(
    input_filepath: Union[str, Path],
    output_dirpath: Union[str, Path],
    module_name: str,
    flags: str = None,
    clock_info: Optional[Tuple[str, float]] = None,
    attempts: Optional[int] = None,
):
    """Wrapper over Vivado synthesis function which creates a DoIt task.

    This task will run Vivado without optimizations, optimized for making
    synthesis fast."""

    input_filepath = Path(input_filepath)
    output_dirpath = Path(output_dirpath)
    synth_opt_place_route_output_filepath = output_dirpath / input_filepath.name
    time_filepath = output_dirpath / f"{input_filepath.stem}.time"
    log_filepath = output_dirpath / f"{input_filepath.stem}.log"
    tcl_script_filepath = output_dirpath / f"{input_filepath.stem}.tcl"
    json_filepath = output_dirpath / f"{input_filepath.stem}.json"

    synth_opts = {
        "instr_src_file": input_filepath,
        "synth_opt_place_route_output_filepath": synth_opt_place_route_output_filepath,
        "module_name": module_name,
        "time_filepath": time_filepath,
        "log_path": log_filepath,
        "tcl_script_filepath": tcl_script_filepath,
        "directive": "RuntimeOptimized",
        "place_directive": "RuntimeOptimized",
        "route_directive": "RuntimeOptimized",
        "flags": flags,
        "opt_design": False,
        "synth_design": True,
        "synth_design_rtl_flags": False,
        "clock_info": clock_info,
        "json_filepath": json_filepath,
    }

    if attempts is not None:
        synth_opts["attempts"] = attempts

    return {
        "actions": [
            (
                xilinx_ultrascale_plus_vivado_synthesis,
                [],
                synth_opts,
            )
        ],
        "file_dep": [input_filepath],
        "targets": [
            synth_opt_place_route_output_filepath,
            time_filepath,
            log_filepath,
            tcl_script_filepath,
            json_filepath,
        ],
    }
