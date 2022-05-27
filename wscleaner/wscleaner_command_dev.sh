#!/bin/bash

# Activate wscleaner environment
eval "$(/usr/local/bin/miniconda3/bin/conda shell.bash hook)" # Add conda environment to system path
conda activate wscleaner_test

# Set variables
logfile="/usr/local/src/mokaguys/automate_demultiplexing_logfiles/wscleaner_logs/$(date -d now +%y%m%d)_wscleaner.log"
runfolders="/media/data3/share"

# Execute
/usr/local/bin/miniconda3/envs/wscleaner_test/bin/python3 /usr/local/src/mokaguys/development_area/workstation_housekeeping/wscleaner/wscleaner/main.py $runfolders --logfile $logfile --dry-run --min-age=1
