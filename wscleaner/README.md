# Workstation Cleaner

Workstation Cleaner (wscleaner) deletes local directories that have been uploaded to the DNAnexus cloud storage service.

When executed, Runfolders in the input (root) directory are deleted based on the following criteria:

* A single DNAnexus project is found matching the runfolder name
* All local FASTQ files are uploaded and in a 'closed' state
* Six logfiles are present in the DNA Nexus project /Logfiles directory

A DNAnexus API key must be cached locally using the `--set-key` option. 

## Install

```bash
git clone https://github.com/moka-guys/wscleaner.git
pip install ./wscleaner
```

## Usage

```bash
wscleaner --set-key DNA_NEXUS_KEY # Localyl caches dnanexus api key
wscleaner ROOT_DIRECTORY --logfile LOGFILE_PATH
```

## Test

```bash
# Run from the cloned repo directory after installation
pytest . --auth_token DNA_NEXUS_KEY
```

## License

Developed by Viapath Genome Informatics
