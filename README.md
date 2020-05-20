# Workstation Housekeeping v1.9

Scripts to manage data on the NGS workstation

---

## backup_runfolder.py

Uploads an Illumina runfolder to DNANexus.

### Usage

```bash
backup_runfolder.py [-h] -i RUNFOLDER [-a AUTH_TOKEN] [--ignore IGNORE] [-p PROJECT] [--logpath LOGPATH]
```

### What are the dependencies for this script?

This tool requires the DNAnexus utilities `ua` (upload agent) and `dx` (DNAnexus toolkit) to be available in the system PATH. Python3 is required, and this tool uses packages from the standard library.

### How does this tool work?

* The script parses the input parameters, asserting that the given runfolder exists.
* If the `-p` option is given, the script attempts to find a matching DNAnexus project. Otherwise, it looks for a single project matching the runfolder name. If more or less than 1 project matches, the script logs an error and exits.
* The runfolder is traversed and a list of files in each folder is obtained. If any comma-separated strings passed to the `--ignore` argument are present within the filepath, or filename the file is excluded.

* The DNAnexus `ua` utility is used to upload files in batches of 100 at a time. The number of upload tries is set to 100 with the `--tries` flag.
* Orthogonal tests are performed to:
    * A count of files that should be uploaded (using the ignore terms if provided)
    * A count of files in the DNA Nexus project
    * (If relevant) A count of files in the DNA Nexus project containing a pattern to be ignored. NB this may not be accurate if the ignore term is found in the result of dx find data (eg present in project name)
* Logs from this and the script are written to a logfile, named "runfolder_backup_runfolder.log". A destination for this file can be passed to the `--logpath` flag.

---

## findfastqs.sh

Report the number of gzipped fastq files in an Illumina runfolder.

### Usage

```bash
$ findfastqs.sh RUNFOLDER
>>> RUNFOLDER has 156 demultiplexed fastq files with 2 undetermined. Total: 158
```

---

## Workstation Cleaner (wscleaner)

Delete local directories that have been uploaded to the DNAnexus cloud storage service.

### Install

```bash
git clone https://github.com/moka-guys/workstation_housekeeping.git
pip install workstation_housekeeping/wscleaner
wscleaner --version # Print version number
# If installing on workstation see wscleaner/README.md section 'Workstation Environment'
```

### Usage

```bash
wscleaner ROOT_DIRECTORY --logfile LOGFILE_PATH
```

---

## ngrok_start.sh

Allow SSH access to the system by running ngrok as a background process.

### Installation

See knowledge base article for ngrok installation.

### Usage

```bash
$ ngrok_start.sh
"tcp://30.tcp.eu.ngrok.io:5555"
```

---
