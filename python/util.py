"""General utilities for the Churchroad evaluation."""

import json
import logging
import os
from pathlib import Path
import re
import subprocess
from tempfile import NamedTemporaryFile
from typing import Dict, Union
import yaml


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


CRE_OUTPUT_DIR_ENV_VAR = "CRE_OUTPUT_DIR"
CRE_MANIFEST_PATH_ENV_VAR = "CRE_MANIFEST_PATH"
CRE_ITERATIONS_ENV_VAR = "CRE_ITERATIONS"


def churchroad_evaluation_dir() -> Path:
    """Return the path to the Churchroad evaluation directory."""
    return Path(__file__).parent.parent.resolve()


def output_dir() -> Path:
    """Get directory where output should go.

    Note that this function loads the manifest, so calling it repeatedly will
    impact performance. Consider just saving the output of this function.

    Output directory is set (in order of precedence)
    1. from the CRE_OUTPUT_DIR environment variable, if set;
    2. from the manifest.
    """

    # Output directory is set by the CRE_OUTPUT_DIR environment variable, if
    # it's set. Otherwise, get it from the manifest.
    out = Path(
        os.environ[CRE_OUTPUT_DIR_ENV_VAR]
        if CRE_OUTPUT_DIR_ENV_VAR in os.environ
        else get_manifest()["output_dir"]
    )

    # If the path is relative, we assume it's relative to the Churchroad
    # evaluation directory.
    if not out.is_absolute():
        out = churchroad_evaluation_dir() / out

    out = out.resolve()

    return out


def _manifest_path() -> Path:
    """Get path to the manifest file.

    You should not need to call this function directly. Instead, use
    get_manifest().

    Manifest file is set (in order of precedence):

    1. from the CRE_MANIFEST_PATH environment variable, if set;
    2. from a default value.
    """
    return (
        Path(os.environ[CRE_MANIFEST_PATH_ENV_VAR])
        if CRE_MANIFEST_PATH_ENV_VAR in os.environ
        else churchroad_evaluation_dir() / "manifest.yml"
    )


def get_manifest() -> Dict:
    manifest = yaml.safe_load(_manifest_path().read_text())

    # Override values from environment variables. This section of the code
    # allows us to override any manifest values using environment variables. Add
    # lines like `manifest["key"] = os.environ["KEY"]` to add an override.
    if CRE_ITERATIONS_ENV_VAR in os.environ:
        manifest["iterations"] = int(os.environ[CRE_ITERATIONS_ENV_VAR])

    return manifest
