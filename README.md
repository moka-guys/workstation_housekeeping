# Workstation Housekeeping
Scripts to manage data on the NGS workstation

---

## backup_runfolder.py v1.0
Uploads an Illumina runfolder to DNANexus.

### Quickstart
```
    usage: backup_runfolder.py [-h] -i RUNFOLDER [-a AUTH_TOKEN] [--ignore IGNORE]
                            [-p PROJECT] [--logpath LOGPATH]
```

### What are the dependencies for this script?
This tool requires the DNAnexus utilities `ua` (upload agent) and `dx` (DNAnexus toolkit) to be available in the system PATH. Python3 is required, and this tool uses packages from the standard library.

### How does this tool work?
* The script parses the input parameters, asserting that the given runfolder exists.
* If the `-p` option is given, the script attempts to find a matching DNAnexus project. Otherwise, it looks for a single project matching the runfolder name. If more or less than 1 project matches, the script logs an error and exits.
* From a list of files in the runfolder, files matching any of the comma-separated strings passed to `--ignore` are removed. The default is '/L00', which ignores BCL files in directories with this prefix. To upload all files in a runfolder, pass the argument `--ignore ""`.
* Finally, each remaining file is passed to the DNAnexus `ua` utility. This will attempt an upload if the files are not found in the expected location in the DNAnexus project. The number of upload tries is set to 100 with the `--tries` flag.
* Logs from this and the script are written to STDERR and a logfile, named after the runfolder. A destination for this file can be passed to the `--logpath` flag.

---

## findfastqs.sh
Report the number of gzipped fastq files in an Illumina runfolder.

### Usage
```
$ findfastqs.sh RUNFOLDER
>>> RUNFOLDER has 156 demultiplexed fastq files with 2 undetermined. Total: 158
```

---