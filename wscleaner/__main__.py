#!/usr/bin/env python3
"""wscleaner

Delete runfolders in a root directory on the condition that it has uploaded to DNA Nexus.

Methods:
    cli_parser(): Parses command line arguments
    main(): Process input directory or API keys
"""
import os
from pathlib import Path
import datetime
import argparse
import logging
import pkg_resources
import dxpy
from wscleaner import mokaguys_logger
from wscleaner.wscleaner import RunFolderManager

# Timestamp used for naming log files with datetime
TIMESTAMP = str(f"{datetime.datetime.now():%Y%m%d_%H%M%S}")
PROJECT_DIR = str(Path(__file__).absolute().parent.parent)  # Project working directory
# Root of folder containing apps (2 levels up from this file)
DOCUMENT_ROOT = "/".join(PROJECT_DIR.split("/")[:-2])
RUNFOLDERS = "/media/data3/share"
LOGDIR = os.path.join(RUNFOLDERS, "automate_demultiplexing_logfiles", "wscleaner_logs")
LOGFILE = os.path.join(
    LOGDIR, f"{TIMESTAMP}_wscleaner.log"
)  # Path for the application logfile
AUTH_FILE = os.path.join(DOCUMENT_ROOT, ".dnanexus_auth_token")
print(LOGFILE)

def cli_parser():
    """Parses command line arguments.
    Args: None. The argparse.ArgumentParser auto-collects arguments from sys.args
    Returns: Argument parser object with a 'root' attribute if root directory given.
        Otherwise, --set-key and --print-key exit after actions are performed.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--auth",
        help="A text file containing the DNANexus authentication token",
        type=str,
        default=AUTH_FILE,
        required=False,
    )
    parser.add_argument(
        "--dry-run",
        help="Perform a dry run without deleting files",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--runfolders_dir",
        help="A directory containing runfolders to process",
        required=True,
    )
    parser.add_argument(
        "--min-age",
        help="The age (days) a runfolder must be to be deleted",
        type=int,
        default=14,
    )
    parser.add_argument(
        "--logfile-count",
        help="The number of logfiles a runfolder must have in /Logfiles",
        type=int,
        default=5,
    )
    # Get version from setup.py as version CLI response
    version_number = pkg_resources.require("wscleaner")[0].version
    parser.add_argument(
        "--version",
        help="Print version",
        action="version",
        version=f"wscleaner v{version_number}",
    )
    args = parser.parse_args()
    return args


def main():
    # Parse CLI arguments. Some arguments will exit the program intentionally. See docstring for detail.
    args = cli_parser()

    # Setup logging for module. Submodules inherit log handlers and filters
    mokaguys_logger.log_setup(LOGFILE)
    logger = logging.getLogger(__name__)
    logger.info(f"START")

    # Setup dxpy authentication token read from command line file.
    with open(args.auth) as f:
        auth_token = f.read().rstrip()
    dxpy.set_security_context({"auth_token_type": "Bearer", "auth_token": auth_token})

    # Set root directory and search it for runfolders
    # If dry-run CLI flag is given, no directories are deleted by the runfolder manager.
    RFM = RunFolderManager(RUNFOLDERS, dry_run=args.dry_run)
    logger.info(f"Runfolder directory {RUNFOLDERS}")
    logger.info(f"Identifying local runfolders to consider deleting")
    local_runfolders = RFM.find_runfolders(min_age=args.min_age)
    logger.debug(
        f"Found local runfolders to consider deleting: {[rf.name for rf in local_runfolders]}"
    )

    for runfolder in local_runfolders:
        logger.info(f"Processing {runfolder.name}")
        # Delete runfolder if it meets the backup criteria
        # runfolder.dx_project is evaluated first as following criteria checks depend on it
        if runfolder.dx_project:
            fastqs_uploaded = RFM.check_fastqs(runfolder)
            logfiles_uploaded = RFM.check_logfiles(runfolder, args.logfile_count)
            if fastqs_uploaded and logfiles_uploaded:
                RFM.delete(runfolder)
            elif not fastqs_uploaded:
                logger.warning(f"{runfolder.name} - FASTQ MISMATCH")
            elif not logfiles_uploaded:
                logger.warning(f"{runfolder.name} - LOGFILE MISMATCH")
        else:
            logger.warning(f"{runfolder.name} - DX PROJECT MISMATCH")

    # Record runfolders removed by this iteration
    logger.info(f"Runfolders deleted in this instance: {RFM.deleted}")
    logger.info(f"END")
    # END
