#!/bin/bash

# Activate wscleaner environment
eval "$(conda shell.bash hook)" # Add conda environment to system path
conda activate wscleaner

# Set varianbles
logfile="/home/mokaguys/Documents/automate_demultiplexing_logfiles/wscleaner_logs/$(date -d now +%y%m%d)_wscleaner.log"
runfolders="/media/data3/share"

# Execute
wscleaner $runfolders --logfile $logfile 
