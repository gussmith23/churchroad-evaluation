"""General utilities for the Churchroad evaluation."""

import json
import logging
from pathlib import Path
import re
import subprocess
from tempfile import NamedTemporaryFile
from typing import Dict, Union


def _parse_yosys_log(log_txt: str):
    matches = list(
        re.finditer(
            r"""
   Number of cells:.*$
.*

""",
            log_txt,
            flags=re.DOTALL | re.MULTILINE,
        )
    )
    assert len(matches) == 1
    span = matches[0].span()
    matches = list(
        re.finditer(
            r"^     (?P<name>\w+) +(?P<count>\d+)$",
            log_txt[span[0] : span[1]],
            flags=re.MULTILINE,
        )
    )
    resources = {match["name"]: int(match["count"]) for match in matches}

    return resources

def count_resources_in_verilog_src(
    verilog_src: str, module_name: str
) -> Dict[str, int]:
    with NamedTemporaryFile(mode="w") as f:
        with f.file as file_object:
            file_object.write(verilog_src)

        out = subprocess.run(
            [
                "yosys",
                "-p",
                f"read_verilog {f.name}; hierarchy -top {module_name}; stat",
            ],
            capture_output=True,
            text=True,
            check=True,
        ).stdout

    # print(out)
    return _parse_yosys_log(out)



def collect(
    iteration: int,
    identifier: str,
    architecture: str,
    tool: str,
    json_filepath: Union[Path, str],
    collected_data_filepath: Union[Path, str],
):
    collected_data_filepath = Path(collected_data_filepath)

    with open(json_filepath, "r") as f:
        data = json.load(f)

    assert "iteration" not in data
    data["iteration"] = iteration

    if "identifier" in data:
        logging.warn(f"Overwriting identifier in {data} with {identifier}")
    data["identifier"] = identifier

    assert "architecture" not in data
    data["architecture"] = architecture

    assert "tool" not in data
    data["tool"] = tool

    collected_data_filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(collected_data_filepath, "w") as f:
        json.dump(data, f)
