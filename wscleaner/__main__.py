#!/usr/bin/env python3
"""wscleaner

Delete runfolders in a root directory on the condition that it has uploaded to DNA Nexus.

Methods:
    cli_parser(): Parses command line arguments
    main(): Process input directory or API keys
"""
import os
import subprocess
from pathlib import Path
import datetime
import argparse
import logging
import dxpy
from wscleaner import mokaguys_logger
from wscleaner.wscleaner import RunFolderManager

# Timestamp used for naming log files with datetime
TIMESTAMP = str(f"{datetime.datetime.now():%Y%m%d_%H%M%S}")
PROJECT_DIR = str(Path(__file__).absolute().parent.parent)  # Project working directory


def git_tag() -> str:
    """
    Obtain the git tag of the current commit
        :return (str):  Git tag
    """
    filepath = os.path.dirname(os.path.realpath(__file__))
    cmd = f"git -C {filepath} describe --tags"

    proc = subprocess.Popen(
        [cmd],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        shell=True,
    )
    out, _ = proc.communicate()
    #  Return standard out, removing any new line characters
    return out.rstrip().decode("utf-8")


def cli_parser():
    """Parses command line arguments.
    Args: None. The argparse.ArgumentParser auto-collects arguments from sys.args
    Returns: Argument parser object with a 'root' attribute if root directory given.
        Otherwise, --set-key and --print-key exit after actions are performed.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--auth_token_file",
        help="A text file containing the DNANexus authentication token",
        type=str,
        required=True,
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
        "--log_dir",
        help="Directory to save log file to",
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
        default=6,
    )
    parser.add_argument(
        "--version",
        help="Print version",
        action="version",
        version=f"wscleaner v{version}",
    )
    return parser.parse_args()


version = git_tag()
# Parse CLI arguments. Some arguments will exit the program intentionally. See docstring for detail.
args = cli_parser()
LOGFILE = os.path.join(
    args.log_dir, f"{TIMESTAMP}_wscleaner.log"
)  # Path for the application logfile

# Setup logging for module. Submodules inherit log handlers and filters
mokaguys_logger.log_setup(LOGFILE)
logger = logging.getLogger()
# Set the name of the root logger
logger.name = 'wscleaner'
logger.info("START")

# Setup dxpy authentication token read from command line file.
with open(args.auth_token_file) as f:
    auth_token = f.read().rstrip()
dxpy.set_security_context({"auth_token_type": "Bearer", "auth_token": auth_token})

# Set root directory and search it for runfolders
# If dry-run CLI flag is given, no directories are deleted by the runfolder manager.
RFM = RunFolderManager(args.runfolders_dir, dry_run=args.dry_run)
logger.info(f"Runfolder directory {args.runfolders_dir}")
logger.info("Identifying local runfolders to consider deleting")
local_runfolders = RFM.find_runfolders(min_age=args.min_age)
logger.info(
    f"Found local runfolders to consider deleting: {[rf.name for rf in local_runfolders]}"
)

for runfolder in local_runfolders:
    logger.info(f"Processing {runfolder.name}")
    # Delete runfolder if it meets the backup criteria
    # runfolder.dx_project is evaluated first as following criteria checks depend on it
    if runfolder.dx_project:
        fastqs_uploaded = RFM.check_fastqs(runfolder)
        logfiles_uploaded = RFM.check_logfiles(runfolder, args.logfile_count)
        upload_log_exists = RFM.upload_log_exists(runfolder)
        if fastqs_uploaded and logfiles_uploaded:
            RFM.delete(runfolder)
        else:
            if not fastqs_uploaded:
                logger.warning(f"{runfolder.name} - FASTQ MISMATCH")
            if not logfiles_uploaded:
                logger.warning(f"{runfolder.name} - LOGFILE MISMATCH")
            if not upload_log_exists:
                logger.warning(f"{runfolder.name} - UPLOAD LOG MISSING")
            else:
                clean_upload_log = RFM.check_upload_log(runfolder)
                if not clean_upload_log:
                    logger.warning(f"{runfolder.name} - UPLOAD LOG CONTAINS ERRORS")        

# Record runfolders removed by this iteration
logger.info(f"Runfolders deleted in this instance: {RFM.deleted}")
logger.info(f"END")
