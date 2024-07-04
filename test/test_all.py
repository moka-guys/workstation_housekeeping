import pytest
import dxpy
from pathlib import Path
import argparse
import json
import sys
import shutil

from pkg_resources import resource_filename
from wscleaner.main import cli_parser
from wscleaner.lib import RunFolderManager, RunFolder


# AUTH: Set DNAnexus authentication for tests
def test_auth(auth_token):
    """Test that an authentication token is passed to pytest as a command line argument"""
    assert auth_token is not None


# FIXTURES: Define functions to use in downstream tests
@pytest.fixture
def rfm():
    """Return an instance of the runfolder manager with the test/data directory"""
    test_path = Path(str(Path(__file__).parent), "data")
    rfm = RunFolderManager(str(test_path))
    return rfm


@pytest.fixture
def rfm_dry():
    """Return an instance of the runfolder manager with the test/data directory"""
    test_path = Path(str(Path(__file__).parent), "data")
    rfm_dry = RunFolderManager(str(test_path), dry_run=True)
    return rfm_dry


class TestFolders:
    def test_runfolders_ready(self, data_test_runfolders, rfm):
        """Test that runfolders in the test directory pass checks for deletion. Est. 20 seconds."""
        for runfolder in rfm.find_runfolders(min_age=0):
            assert all(
                [
                    runfolder.dx_project,
                    rfm.check_fastqs(runfolder),
                    rfm.check_logfiles(runfolder),
                ]
            )

    def test_find_fastqs(self, data_test_runfolders):
        """Tests the correct number of fastqs are present in local and uploaded directories"""
        for runfolder_name, fastq_list_file in data_test_runfolders:
            rf = RunFolder(Path("test/data", runfolder_name))
            with open(fastq_list_file) as f:
                test_folder_fastqs = len(f.readlines())
            assert len(rf.find_fastqs()) == test_folder_fastqs
            assert len(rf.dx_project.find_fastqs()) == test_folder_fastqs

    def test_min_age(self, rfm):
        """test that the runfolder age function records age"""
        runfolders = rfm.find_runfolders(min_age=10)
        # Asser that this test runfolder was recently generated
        assert all([rf.age > 10 for rf in runfolders])


class TestRFM:
    def test_find_runfolders(self, data_test_runfolders, rfm):
        """test the runfolder manager directory finding function"""
        rfm_runfolders = rfm.find_runfolders(min_age=0)
        runfolder_names = [str(folder.path.name) for folder in rfm_runfolders]
        test_runfolder_names = [rf for rf, fastq_list_file in data_test_runfolders]
        runfolders_bools = [item in runfolder_names for item in test_runfolder_names]
        assert all(runfolders_bools)

    def test_validate(self, rfm):
        """test the runfoldermanager _validate function correctly reads the path"""
        assert rfm.root.name == Path(str(Path(__file__).parent), "data").name

    def test_delete(self, monkeypatch, rfm):
        """test that the runfolder manager delete call creates the log of deleted files.
        Here, the pytest monkeypatch fixture is used to overwrite the delete function and persist the test directories.
        """
        test_folder = rfm.find_runfolders(min_age=0)[0]
        monkeypatch.setattr(shutil, "rmtree", lambda x: "TEST_DELETED")
        rfm.delete(test_folder)
        assert test_folder.name in rfm.deleted

    def test_dry_run(self, rfm_dry):
        """test that the dry_run option does not cause the test directory to be deleted"""
        test_folder = rfm_dry.find_runfolders(min_age=0)[0]
        rfm_dry.delete(test_folder)
        assert test_folder.name not in rfm_dry.deleted
