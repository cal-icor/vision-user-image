#!/usr/bin/env python3
import nbformat
import os
import sys
from nbclient import NotebookClient
from pathlib import Path


def echo_outputs(notebook, name):
    """
    Print a notebook's cell output to stdout.

    nbclient keeps output on the notebook object rather than writing it to the
    console, so anything a test notebook prints is invisible in CI unless we
    echo it ourselves. Errors are echoed too, which is the only diagnostic
    available when a notebook fails.
    """
    print(f"\n----- output from {name} -----", flush=True)
    for index, cell in enumerate(notebook.cells):
        if cell.cell_type != "code":
            continue
        for output in cell.get("outputs", []):
            kind = output.get("output_type")
            if kind == "stream":
                sys.stdout.write("".join(output.get("text", "")))
            elif kind == "error":
                print(f"[cell {index}] {output.get('ename')}: {output.get('evalue')}")
                print("\n".join(output.get("traceback", [])))
            elif kind in ("execute_result", "display_data"):
                text = output.get("data", {}).get("text/plain")
                if text:
                    sys.stdout.write("".join(text) + "\n")
    print(f"----- end {name} -----\n", flush=True)


def run_notebook(notebook, kernel_name="python3"):
    """
    Executes all cells in a Jupyter notebook and echoes its output.

    It uses `nbclient` to execute the notebook, then prints whatever the cells
    produced so the CI log carries it.

    Args:
        notebook (str): The name of the notebook file in image-tests/notebooks.
        kernel_name (str, optional): The kernel to execute with.

    Returns:
        bool: True if the notebook executed successfully, False otherwise.
    """
    name = notebook
    notebook_path = os.path.join("image-tests", "notebooks", name)

    try:
        notebook = nbformat.read(notebook_path, as_version=4)
    except FileNotFoundError:
        print(f"{name}: not found at {notebook_path}", flush=True)
        return False

    client = NotebookClient(
        notebook,
        timeout=600,
        kernel_name=kernel_name,
        # This resource is used to set the working directory for the notebook's kernel.
        # It ensures that relative paths within the notebook resolve correctly.
        resources={"metadata": {"path": str(Path(notebook_path).parent)}},
    )

    try:
        # Execute the notebook. This is the core step where all cells are run.
        notebook = client.execute()
    except Exception as exc:
        print(f"\n{name} FAILED: {type(exc).__name__}: {exc}", flush=True)
        echo_outputs(getattr(client, "nb", notebook), name)
        return False

    echo_outputs(notebook, name)
    return True


def test_hawthorne_notebook_execution():
    assert run_notebook("Hawthorne_test.ipynb")


def test_all_hub_basic_notebook_execution():
    assert run_notebook("all_hub_basic_notebook.ipynb")


def test_lec01_executed_1_notebook_execution():
    assert run_notebook("lec01_executed_1.ipynb")


def test_vision_stack_notebook_execution():
    assert run_notebook("vision_stack_test.ipynb")


if __name__ == "__main__":
    test_hawthorne_notebook_execution()
    test_all_hub_basic_notebook_execution()
    test_lec01_executed_1_notebook_execution()
    test_vision_stack_notebook_execution()
