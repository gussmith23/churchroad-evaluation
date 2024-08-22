import util
import vivado
import yosys


def task_compile_benchmarks():
    manifest = util.get_manifest()

    json_filepaths = []

    for benchmark in manifest["benchmarks"]:
        filepath = util.churchroad_evaluation_dir() / benchmark["filepath"]
        benchmark_name = filepath.stem

        # Vivado compilation.
        vivado_output_dirpath = util.output_dir() / benchmark_name / "vivado"
        (task, (json_filepath, _, _, _)) = (
            vivado.make_xilinx_ultrascale_plus_vivado_synthesis_task_opt(
                name=f"{benchmark_name}:compile:vivado",
                input_filepath=filepath,
                output_dirpath=vivado_output_dirpath,
                module_name=benchmark_name,
                attempts=manifest["vivado_num_attempts"],
                part_name=manifest["pynq_part_name"],
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
        )
        yield task
        json_filepaths.append(json_filepath)
