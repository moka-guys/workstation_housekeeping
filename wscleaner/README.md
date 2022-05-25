# Workstation Cleaner

Workstation Cleaner (wscleaner) deletes local directories that have been uploaded to the DNAnexus cloud storage service.

When executed, Runfolders in the input (root) directory are deleted based on the following criteria:

* A single DNAnexus project is found matching the runfolder name
* All local FASTQ files are uploaded and in a 'closed' state
* 5 logfiles are present in the DNA Nexus project /Logfiles directory

or if the run is identified as a TSO500 run, based on:
  * the bcl2fastq2_output.log file created by the automated scripts

  AND
  * Presence of `_TSO` in the human readable DNANexus project name

A DNAnexus API key must be cached locally using the `--set-key` option. 

## Install

```bash
git clone https://github.com/moka-guys/workstation_housekeeping.git
pip install workstation_housekeeping/wscleaner
wscleaner --version # Print version number
```
Note that may need to activate the environment before installing with pip.
On the workstation 2 environments exist - wscleaner and wscleaner_test (for development work)

## Quickstart

```bash
wscleaner ROOT_DIRECTORY
```

## Usage

```
usage: wscleaner [-h] [--auth AUTH] [--dry-run] [--logfile LOGFILE]
                 [--min-age MIN_AGE] [--logfile-count LOGFILE_COUNT]
                 [--version]
                 root

positional arguments:
  root                  A directory containing runfolders to process

optional arguments:
  -h, --help            show this help message and exit
  --auth AUTH           A text file containing the DNANexus authentication
                        token
  --dry-run             Perform a dry run without deleting files
  --logfile LOGFILE     A path for the application logfile
  --min-age MIN_AGE     The age (days) a runfolder must be to be deleted
  --logfile-count LOGFILE_COUNT
                        The number of logfiles a runfolder must have in
                        /Logfiles
  --version             Print version
```

## Test

```bash
# Run from the cloned repo directory after installation
pytest . --auth_token DNA_NEXUS_KEY
```

## Workstation Environment
The directory `env/` in this repository contains conda environment scripts for the workstation. These remove conflicts in the PYTHONPATH environment variable by editing the variable when conda is activated. The conda documentation describes where to place these scripts under ['saving environment variables'](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#macos-and-linux).


## License

Developed by Viapath Genome Informatics
