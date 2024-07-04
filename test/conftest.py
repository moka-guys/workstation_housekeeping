"""conftest.py

Config for pytest.
"""

import os
import pytest
from pathlib import Path

PROJECT_DIR = str(Path(__file__).absolute().parent.parent)  # Project working directory


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
def auth_token(request):
    """Create pytest fixture from command line argument for authentication token"""
    return request.config.getoption("--auth_token_file")


@pytest.fixture(scope="session")
def data_test_runfolders():
    """A fixture that returns a list of tuples containing (runfolder_name, fastq_list_file)."""
    return [
        (
            "999999_NB551068_1234_WSCLEANTST_TSTRUN01",
            os.path.join(PROJECT_DIR, "test/data/test_dir_1_fastqs.txt"),
        ),
        (
            "999999_NB551068_1234_WSCLEANTST_TSTRUN02",
            os.path.join(PROJECT_DIR, "test/data/test_dir_2_fastqs.txt"),
        ),
    ]


@pytest.fixture(scope="session", autouse=True)
def create_test_dirs(data_test_runfolders):
    """Create test data for testing.

    This is an autouse fixture with session scope, meaning it is run once per session
    """
    for runfolder_name, fastq_list_file in data_test_runfolders:
        # Create the runfolder directory as per Illumina spec
        runfolder_path = os.path.join(PROJECT_DIR, f"test/data/{runfolder_name}")
        fastqs_path = os.path.join(
            PROJECT_DIR, f"{runfolder_path}/Data/Intensities/BaseCalls"
        )
        Path(fastqs_path).mkdir(parents=True, exist_ok=True)
        # Generate empty fastqfiles in runfolder
        with open(fastq_list_file) as f:
            fastq_list = f.read().splitlines()
            for fastq_file in fastq_list:
                Path(fastqs_path, fastq_file).touch(mode=777, exist_ok=True)
        open(
            os.path.join(f"{runfolder_path}", "RTAComplete.txt"), "w"
        ).close()  # Create RTAComplete file
    yield  # Tests are run here
    for runfolder_name, fastq_list_file in data_test_runfolders:
        runfolder_path = os.path.join(PROJECT_DIR, f"test/data/{runfolder_name}")
        os.rmdir(runfolder_path)
