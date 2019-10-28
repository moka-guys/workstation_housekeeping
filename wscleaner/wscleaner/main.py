#!/usr/bin/env python3
"""wscleaner

Delete runfolders in a root directory on the condition that it has uploaded to DNA Nexus.

Methods:
    cli_parser(): Parses command line arguments
    main(): Process input directory or API keys
"""

import argparse
import logging
import pkg_resources
from wscleaner import mokaguys_logger
from wscleaner.auth import SetKeyAction, PrintKeyAction, dx_set_auth
from wscleaner.lib import RunFolder, RunFolderManager



def cli_parser():
    """Parses command line arguments.
    Args: None. The argparse.ArgumentParser auto-collects arguments from sys.args
    Returns: Argument parser object with a 'root' attribute if root directory given.
        Otherwise, --set-key and --print-key exit after actions are performed.
    """
    parser = argparse.ArgumentParser()
    # argparse API for adding custom routines. SetKeyAction and PrintKeyAction are classes with 
    # routines that exit the software after an action is performed.
    parser.register('action', 'setkey', SetKeyAction)
    parser.register('action', 'printkey', PrintKeyAction)
    # Define CLI arguments
    parser.add_argument('--set-key', action='setkey', help='Cache a DNA Nexus API key')
    parser.add_argument('--print-key', nargs=0, action='printkey', help='Print the cached DNA Nexus API key')
    parser.add_argument('--dry-run', help='Perform a dry run without deleting files', action='store_true', default=False)
    parser.add_argument('root', help='A directory containing runfolders to process')
    parser.add_argument('--logfile', help='A path for the application logfile', default='mokaguys_logger.log')
    parser.add_argument('--min-age', help='The age (days) a runfolder must be to be deleted', type=int, default=14)
    # Get version from setup.py as version CLI response
    version_number = pkg_resources.require("wscleaner")[0].version
    parser.add_argument('--version', help='Print version', action='version', version=f"wscleaner v{version_number}")
    args = parser.parse_args()
    return args

def main():
    # Parse CLI arguments. Some arguments will exit the program intentionally. See docstring for detail.
    args = cli_parser()

    # Setup logging for module. Submodules inherit log handlers and filters
    mokaguys_logger.log_setup(args.logfile)
    logger = logging.getLogger(__name__)
    logger.info(f'START')

    # Setup dxpy with cached authentication token
    dx_set_auth()

    # Set root directory and search it for runfolders
    # If dry-run CLI flag is given, no directories are deleted by the runfolder manager.
    RFM = RunFolderManager(args.root, dry_run=args.dry_run)
    logger.info(f'Root directory {args.root}')
    local_runfolders = RFM.find_runfolders(min_age=args.min_age)
    logger.debug(f'Found local runfolders: {[rf.name for rf in local_runfolders]}')

    for runfolder in local_runfolders:
        logger.info(f'Processing {runfolder.name}')
        # Delete runfolder if it meets the backup criteria
        # runfolder.dx_project is evaluated first as following criteria checks depend on it
        if runfolder.dx_project:
            fastqs_uploaded = RFM.check_fastqs(runfolder)
            logfiles_uploaded = RFM.check_logfiles(runfolder)
            if fastqs_uploaded and logfiles_uploaded:
                RFM.delete(runfolder)
            elif not fastqs_uploaded:
                logger.warning(f'{runfolder.name} - FASTQ MISMATCH')
            elif not logfiles_uploaded:
                logger.warning(f'{runfolder.name} - LOGFILE MISMATCH')
        else:
            logger.warning(f'{runfolder.name} - DX PROJECT MISMATCH')

    # Record runfolders removed by this iteration
    logger.info(f'Runfolders deleted in this instance: {RFM.deleted}')
    logger.info(f'END')
    # END


if __name__ == '__main__':
    main()