import json
import logging
from pathlib import Path
import subprocess
import sys
from time import time
from typing import Any, Dict, Optional, Tuple, Union

from . import util

 
def yosys_synthesis(
    input_filepath: Union[str, Path],
    module_name: str,
    output_filepath: str,
    synth_command: str,
    log_filepath: Union[str, Path],
    summary_filepath: Union[str, Path],
    extra_summary_fields: Dict[str, Any] = {},
):
    output_filepath.parent.mkdir(parents=True, exist_ok=True)
    log_filepath.parent.mkdir(parents=True, exist_ok=True)

    # Synthesis with Yosys.
    with open(log_filepath, "w") as logfile:
        logging.info("Running Yosys synthesis on %s", input_filepath)
        try:
            yosys_start_time = time()
            subprocess.run(
                [
                    "yosys",
                    "-d",
                    "-p",
                    f"""
                    read -sv {input_filepath}
                    hierarchy -top {module_name}
                    {synth_command}
                    stat
                    write_verilog {output_filepath}""",
                ],
                check=True,
                stdout=logfile,
                stderr=logfile,
            )
            yosys_end_time = time()
        except subprocess.CalledProcessError as e:
            print(f"Error log in {(str(logfile.name))}", file=sys.stderr)
            raise e

    # Generate summary
    summary = util.count_resources_in_verilog_src(output_filepath.read_text(), module_name)

    assert "time_s" not in summary
    summary["time_s"] = yosys_end_time - yosys_start_time

    for key in extra_summary_fields:
        assert key not in summary
        summary[key] = extra_summary_fields[key]

    with open(summary_filepath, "w") as f:
        json.dump(summary, f)


def make_lattice_ecp5_yosys_synthesis_task(
    input_filepath: Union[str, Path],
    output_dirpath: Union[str, Path],
    module_name: str,
    clock_info: Optional[Tuple[str, float]] = None,
    name: Optional[str] = None,
    extra_summary_fields: Dict[str, Any] = {},
):
    """Wrapper over Yosys synthesis function which creates a DoIt task."""
    # TODO(@gussmith23): Support clocks on Lattice.
    if clock_info is not None:
        logging.warn("clock_info not supported for Lattice yet.")

    output_dirpath = Path(output_dirpath)
    json_filepath = output_dirpath / f"{module_name}.json"
    output_filepath = output_dirpath / f"{module_name}.sv"
    log_filepath = output_dirpath / f"{module_name}.log"

    task = {
        "actions": [
            (
                yosys_synthesis,
                [],
                {
                    "summary_filepath": json_filepath,
                    "input_filepath": input_filepath,
                    "module_name": module_name,
                    "output_filepath": output_filepath,
                    "synth_command": "synth_ecp5",
                    "log_filepath": log_filepath,
                    "extra_summary_fields": extra_summary_fields,
                },
            )
        ],
        "file_dep": [input_filepath],
        "targets": [
            json_filepath,
            output_filepath,
            log_filepath,
        ],
    }

    if name is not None:
        task["name"] = name

    return (task, (json_filepath, output_filepath, log_filepath))


def make_xilinx_yosys_synthesis_task(
    input_filepath: Union[str, Path],
    output_dirpath: Union[str, Path],
    module_name: str,
    family: str,
    clock_info: Optional[Tuple[str, float]] = None,
    name: Optional[str] = None,
    extra_summary_fields: Dict[str, Any] = {},
):
    """Wrapper over Yosys synthesis function which creates a DoIt task."""
    # TODO(@gussmith23): Support clocks on Lattice.
    if clock_info is not None:
        logging.warn("clock_info not supported for Yosys.")

    output_dirpath = Path(output_dirpath)
    output_filepaths = {
        "json_filepath": output_dirpath / f"{module_name}.json",
        "output_filepath": output_dirpath / f"{module_name}.sv",
        "log_filepath": output_dirpath / f"{module_name}.log",
    }

    task = {
        "actions": [
            (
                yosys_synthesis,
                [],
                {
                    "summary_filepath": output_filepaths["json_filepath"],
                    "input_filepath": input_filepath,
                    "module_name": module_name,
                    "output_filepath": output_filepaths["output_filepath"],
                    "synth_command": f"synth_xilinx -family {family}",
                    "log_filepath": output_filepaths["log_filepath"],
                    "extra_summary_fields": extra_summary_fields,
                },
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
            output_filepaths["json_filepath"],
            output_filepaths["output_filepath"],
            output_filepaths["log_filepath"],
        ),
    )
