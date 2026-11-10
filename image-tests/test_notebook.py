#!/usr/bin/env python3
import nbformat
import os
from nbclient import NotebookClient
from pathlib import Path


def run_notebook(notebook, kernel_name="python3"):
    """
    Executes all cells in a Jupyter notebook and saves the output back to the same file.

    It uses `nbclient` to execute the notebook and then calls `clean_notebook_metadata`
    to remove execution-specific information before saving.

    Args:
        notebook_path (str): The path to the notebook file to execute.
        timeout (int, optional): The maximum time in seconds to wait for
                                 a single cell to execute. Defaults to 600.

    Returns:
        bool: True if the notebook executed successfully, False otherwise.
    """
    notebook_path = os.path.join("image-tests", "notebooks", notebook)

    try:
        notebook = nbformat.read(notebook_path, as_version=4)
    except FileNotFoundError:
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
    except Exception:
        return False

    return True


def test_hawthorne_notebook_execution():
    assert run_notebook("Hawthorne_test.ipynb")


def test_all_hub_basic_notebook_execution():
    assert run_notebook("all_hub_basic_notebook.ipynb")


def test_lec01_executed_1_notebook_execution():
    assert run_notebook("lec01_executed_1.ipynb")


def test_cpp_kernel_notebook_execution():
    assert run_notebook("cpp_kernel_test.ipynb", kernel_name="xcpp17")


def test_gpt2_stack_notebook_execution():
    assert run_notebook("gpt2_stack_test.ipynb")


if __name__ == "__main__":
    test_hawthorne_notebook_execution()
    test_all_hub_basic_notebook_execution()
    test_lec01_executed_1_notebook_execution()
    test_cpp_kernel_notebook_execution()
