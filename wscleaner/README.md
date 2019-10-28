# Workstation Cleaner

Workstation Cleaner (wscleaner) deletes local directories that have been uploaded to the DNAnexus cloud storage service.

When executed, Runfolders in the input (root) directory are deleted based on the following criteria:

* A single DNAnexus project is found matching the runfolder name
* All local FASTQ files are uploaded and in a 'closed' state
* Six logfiles are present in the DNA Nexus project /Logfiles directory

A DNAnexus API key must be cached locally using the `--set-key` option. 

## Install

```bash
git clone https://github.com/moka-guys/workstation_housekeeping.git
pip install workstation_housekeeping/wscleaner
wscleaner --version # Print version number
```

## Quickstart

```bash
wscleaner --set-key DNA_NEXUS_KEY # Cache dnanexus api key
wscleaner ROOT_DIRECTORY
```

## Usage

```
wscleaner   [-h] [--set-key SET_KEY] [--print-key] [--dry-run]
            [--logfile LOGFILE] [--min-age MIN_AGE] [--version]
            root

positional arguments:
  root               A directory containing runfolders to process

optional arguments:
  -h, --help         show this help message and exit
  --set-key SET_KEY  Cache a DNA Nexus API key
  --print-key        Print the cached DNA Nexus API key
  --dry-run          Perform a dry run without deleting files
  --logfile LOGFILE  A path for the application logfile
  --min-age MIN_AGE  The age (days) a runfolder must be to be deleted
  --version          Print version
```

## Test

```bash
# Run from the cloned repo directory after installation
pytest . --auth_token DNA_NEXUS_KEY
```

## License

Developed by Viapath Genome Informatics
