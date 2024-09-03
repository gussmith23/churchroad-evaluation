import json
import os
from pathlib import Path
from typing import List, Union
import util
import vivado
import pandas
import yosys
import numpy as np


def _collect_json_to_csv(
    filepaths: List[Union[str, Path]], output_filepath: Union[str, Path]
):
    Path(output_filepath).parent.mkdir(parents=True, exist_ok=True)
    pandas.DataFrame.from_records(
        filter(
            lambda x: x is not None,
            map(lambda f: json.load(open(f)) if os.path.exists(f) else None, filepaths),
        )
    ).to_csv(output_filepath, index=False)


def task_compile_benchmarks():
    manifest = util.get_manifest()
    output_dir = util.output_dir()

    json_filepaths = []

    for benchmark in manifest["benchmarks"]:
        filepath = util.churchroad_evaluation_dir() / benchmark["filepath"]
        benchmark_name = filepath.stem
        benchmark_extra_summary_fields = {"tool": "vivado", "name": benchmark_name}
        benchmark_synth_options = ""

        if "synth_options" in benchmark.keys() and benchmark["synth_options"] is not None:
            benchmark_synth_options = benchmark["synth_options"]
        if "features" in benchmark.keys() and benchmark["features"] is not None:
            benchmark_features = benchmark["features"]
            for feature in benchmark_features:
                benchmark_extra_summary_fields[feature] = benchmark_features[feature]

        # Vivado compilation.
        vivado_output_dirpath = util.output_dir() / benchmark_name / "vivado"
        (task, (json_filepath, _, _, _)) = (
            vivado.make_xilinx_ultrascale_plus_vivado_synthesis_task_opt(
                name=f"{benchmark_name}:compile:vivado",
                input_filepath=filepath,
                output_dirpath=vivado_output_dirpath,
                module_name=benchmark_name,
                synth_options=benchmark_synth_options,
                attempts=manifest["vivado_num_attempts"],
                part_name=manifest["vivado_pynq_part_name"],
                extra_summary_fields=benchmark_extra_summary_fields,
            )
        )
        yield task
        json_filepaths.append(json_filepath)

        # Yosys compilation.
        yosys_output_dirpath = util.output_dir() / benchmark_name / "yosys"
        (task, (json_filepath, _, _)) = yosys.make_xilinx_yosys_synthesis_task(
            name=f"{benchmark_name}:compile:yosys",
            input_filepath=filepath,
            output_dirpath=yosys_output_dirpath,
            module_name=benchmark_name,
            family=manifest["yosys_pynq_family"],
            extra_summary_fields={"tool": "yosys", "name": benchmark_name},
        )
        yield task
        json_filepaths.append(json_filepath)

    output_csv_path = output_dir / manifest["output_csv_filepath"]
    yield {
        "name": "collect_data",
        # To generate the CSV with incomplete data, you can comment out the following line.
        # "file_dep": collected_data_output_filepaths,
        "targets": [output_csv_path],
        "actions": [
            (
                _collect_json_to_csv,
                [],
                {
                    "filepaths": json_filepaths,
                    "output_filepath": output_csv_path,
                },
            )
        ],
        "file_dep": json_filepaths,
    }
