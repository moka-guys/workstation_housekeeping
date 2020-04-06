#!/bin/bash

# Activate wscleaner environment
eval "$(/usr/local/bin/miniconda3/bin/conda shell.bash hook)" # Add conda environment to system path
conda activate wscleaner

# Set variables
logfile="/usr/local/src/mokaguys/automate_demultiplexing_logfiles/wscleaner_logs/$(date -d now +%y%m%d)_wscleaner.log"
runfolders="/media/data3/share"

# Execute
wscleaner $runfolders --logfile $logfile 
