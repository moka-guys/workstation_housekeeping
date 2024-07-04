"""conftest.py

Config for pytest.
"""

import os
import pytest
import shutil
import dxpy
from pathlib import Path

PROJECT_DIR = str(Path(__file__).absolute().parent.parent)  # Project working directory
DATA_DIR = os.path.join(PROJECT_DIR, "test/data/")

def pytest_addoption(parser):
    """Add command line options to pytest"""
    parser.addoption(
        "--auth_token_file",
        action="store",
        default=None,
        required=True,
        help="File containing DNANexus authentication key",
    )


@pytest.fixture
def auth_token_file(request):
    """Create pytest fixture to return auth token file from the command line arg"""
    return request.config.getoption("--auth_token_file")


@pytest.fixture(scope="session")
def data_test_runfolders():
    """A fixture that returns a list of tuples containing (runfolder_name, fastq_list_file)."""
    return [
        (
            "999999_NB551068_1234_WSCLEANT01",
            os.path.join(DATA_DIR, "test_dir_1_fastqs.txt"),
        ),
        (
            "999999_NB551068_1234_WSCLEANT02",
            os.path.join(DATA_DIR, "test_dir_2_fastqs.txt"),
        ),
    ]


@pytest.fixture(scope="function", autouse=True)
def create_test_dirs(data_test_runfolders, auth_token_file, request, monkeypatch):
    """Create test data for testing.

    This is an autouse fixture with session function, meaning it is run once per test
    """
    for runfolder_name, fastq_list_file in data_test_runfolders:
        # Create the runfolder directory as per Illumina spec
        runfolder_path = os.path.join(DATA_DIR, runfolder_name)
        fastqs_path = os.path.join(
            PROJECT_DIR, f"{runfolder_path}/Data/Intensities/BaseCalls"
        )
        Path(fastqs_path).mkdir(parents=True, exist_ok=True)
        # Create dummy logfile
        # open(upload_runfolder_logfile, 'w').close()
        # Generate empty fastqfiles in runfolder
        with open(fastq_list_file) as f:
            fastq_list = f.read().splitlines()
            for fastq_file in fastq_list:
                Path(fastqs_path, fastq_file).touch(mode=777, exist_ok=True)
        open(
            os.path.join(runfolder_path, "RTAComplete.txt"), "w"
        ).close()  # Create RTAComplete file
        open(
            f"{runfolder_path}_upload_runfolder.log", "w"
        ).close()  # Create dummy upload runfolder log file
        with open(auth_token_file) as f:  # Setup dxpy authentication token read from command line file
            auth_token = f.read().rstrip()
        dxpy.set_security_context({"auth_token_type": "Bearer", "auth_token": auth_token})

    yield  # Where the testing happens
    # TEARDOWN - cleanup after each test
    for runfolder_name, fastq_list_file in data_test_runfolders:
        runfolder_path = os.path.join(PROJECT_DIR, f"test/data/{runfolder_name}")
        shutil.rmtree(runfolder_path)

