## Workstation Cleaner (wscleaner)

The Synnovis Genome Informatics team use a linux workstation to manage sequencing files. These files are uploaded to the DNAnexus service for storage, however clearing the workstation is time intensive. Workstation Cleaner (wscleaner) automates the deletion of local directories that have been uploaded to the DNAnexus cloud storage service.

A RunFolderManager class will instantiate objects for local runfolders, each of which has an associated DNAnexus project object. The manager loops over the runfolders and deletes them if all checks pass. DNAnexus projects are accessed with the dxpy module, a python wrapper for the DNAnexus API.

## Protocol

When executed, runfolders in the input (root) directory are identified based on:
* Matching the expected runfolder regex pattern

Runfolders are identified for deletion if meeting the following criteria:
* A single DNAnexus project is found matching the runfolder name
* All local FASTQ files are uploaded and in a 'closed' state (for TSO runfolders, there are no local fastqs so this check automatically passes)
* X logfiles are present in the DNAnexus project `automated_scripts_logfiles` directory (NB X can be added as a command line argument - default is 6)
* Runfolder's upload runfolder log file contains no errors

TSO runfolders must meet the following additional criteria to be identified for deletion:
* Presence of bcl2fastq2_output.log file
* Presence of `TSO run.` in the bcl2fastq log file
* Presence of `_TSO` in the human readable DNANexus project name

## Usage

The script takes the following arguments, and can be run in either dry run mode (doesn't delete runfolders) or live mode (deletes runfolders). The script has been developed using python 3.10.6.

_**When running on the workstation, the conda environment must be activated prior to running the wscleaner command.**_

```
usage: __main__.py [-h] --auth_token_file AUTH_TOKEN_FILE [--dry-run] --runfolders_dir RUNFOLDERS_DIR --log_dir LOG_DIR [--min-age MIN_AGE]
                   [--logfile-count LOGFILE_COUNT] [--version]

options:
  -h, --help            show this help message and exit
  --auth_token_file AUTH_TOKEN_FILE
                        A text file containing the DNANexus authentication token
  --dry-run             Perform a dry run without deleting files
  --runfolders_dir RUNFOLDERS_DIR
                        A directory containing runfolders to process
  --log_dir LOG_DIR     Directory to save log file to
  --min-age MIN_AGE     The age (days) a runfolder must be to be deleted
  --logfile-count LOGFILE_COUNT
                        The number of logfiles a runfolder must have in /Logfiles
  --version             Print version
```


### Dry run mode

For example, if running in dry run mode:

```
conda activate python3.10.6 && python3 -m wscleaner --dry-run --runfolders_dir $RUNFOLDERS_DIR --auth_token_file $AUTH_TOKEN_FILEPATH --log_dir $LOG_DIR
```

### Live mode

If running in production mode:

```
conda activate python3.10.6 && python3 -m wscleaner --runfolders_dir $RUNFOLDERS_DIR --auth_token_file $AUTH_TOKEN_FILEPATH --log_dir $LOG_DIR
```

## Testing

Tests should be run and all passing prior to any new release.

```bash
python3 -m pytest -v --auth_token_file=$FULL_PATH_TO_FILE_CONTAINING_AUTH_TOKEN
```


### Developed by Synnovis Genome Informatics