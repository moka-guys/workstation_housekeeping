## Workstation Cleaner (wscleaner)

The Viapath Genome Informatics team use a linux workstation to manage sequencing files. These files are uploaded to the DNAnexus service for storage, however clearing the workstation is time intensive. Workstation Cleaner (wscleaner) automates the deletion of local directories that have been uploaded to the DNAnexus cloud storage service.

A RunFolderManager class will instatiate objects for local Runfolders, each of which has an associated DNA Nexus project object. The manager loops over the runfolders and deletes them if all checks pass.

DNA Nexus projects are accessed with the dxpy module, a python wrapper for the DNA Nexus API.

When executed, Runfolders in the input (root) directory are deleted based on the following criteria:

* A single DNAnexus project is found matching the runfolder name
* All local FASTQ files are uploaded and in a 'closed' state
* X logfiles are present in the DNA Nexus project /Logfiles directory (NB X can be added as a command line argument - default is 5)

OR if the run is identified as a TSO500 run, based on:
  * the bcl2fastq2_output.log file created by the automated scripts
  AND
  * Presence of `_TSO` in the human readable DNANexus project name

A DNAnexus API key must be cached locally using the `--set-key` option. 

## Workstation Environment

The directory `env/` in this repository contains conda environment scripts for the workstation. These remove conflicts in the PYTHONPATH environment variable by editing the variable when conda is activated. The conda documentation describes where to place these scripts under ['saving environment variables'](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#macos-and-linux).


```bash
git clone https://github.com/moka-guys/workstation_housekeeping.git
pip install workstation_housekeeping/wscleaner
wscleaner --version # Print version number
```

## Automated usage
The script `wscleaner_command.sh` is called by the crontab. This activates the enviroment and passes the logfile path (and any other non-default arguments).
A development command script `wscleaner_command_dev.sh` can be used to call the test environment and provide testing arguments, eg --dry-run


## Manual Usage

```
usage: wscleaner [-h] [--auth AUTH] [--dry-run] [--logfile LOGFILE]
                 [--min-age MIN_AGE] [--logfile-count LOGFILE_COUNT]
                 [--version]
                 root

positional arguments:
  root                  A directory containing runfolders to process

optional arguments:
  -h, --help            show this help message and exit
  --runfolders_dir      A directory containing runfolders to process
  --auth AUTH           A text file containing the DNANexus authentication
                        token
  --dry-run             Perform a dry run without deleting files
  --min-age MIN_AGE     The age (days) a runfolder must be to be deleted
  --logfile-count LOGFILE_COUNT
                        The number of logfiles a runfolder must have in
                        /Logfiles
  --version             Print version
```

**The conda environment must be activated prior to running the wscleaner command.**

### Dry run mode

For example, if running in dry run mode:

```
conda activate wscleaner && python3 -m wscleaner /media/data3/share --dry-run
```

### Live mode

If running in production mode:

```
conda activate wscleaner && python3 -m wscleaner /media/data3/share
```

## Test

```bash
# Run from the cloned repo directory after installation
pytest . --auth_token DNA_NEXUS_KEY
```

## License

Developed by Synnovis Genome Informatics
