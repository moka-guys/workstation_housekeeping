# Workstation Housekeeping
Scripts to manage data on the NGS workstation

## backup_runfolder.py v1.0
Uploads an Illumina runfolder to DNANexus.

### Quickstart
```
    usage: backup_runfolder.py [-h] -i RUNFOLDER [-a AUTH_TOKEN] [--ignore IGNORE]
                            [-p PROJECT] [--logpath LOGPATH]
```

### What are the dependencies for this script?
This tool requires the DNAnexus utilities `ua` (upload agent) and `dx` (DNAnexus toolkit) to be available in the system PATH.

### How does this tool work?
* The script parses the input parameters, asserting that the given runfolder exists. If the `-p` option is given, the script searches for a single matching DNAnexus project. Otherwise, it looks for a single project matching the runfolder name. If more or less than 1 project matches, the script logs an error and exits.
* From a list of files in the runfolder, files matching any of the comma-separated strings passed to `--ignore` are removed. The default is '/L00', which ignores BCL files in directories with this prefix.
* Finally, each remaining file is passed to the DNAnexus `ua` utility. This will attempt uploads if the files are not found in the expected location in the DNAnexus project. 
* Logs from this and the script are written to STDERR and a logfile, named after the runfolder. A destination for this file can be passed to the `--logpath` flag.
