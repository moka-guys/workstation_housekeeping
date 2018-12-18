#!/bin/bash

# Commands to help with runfolder managemenet (Nana)
findfastqs(){ 
    input_directory=$1
    # Find all fastqs in the input directory.
    # Grep -v filters out undetermined fastqs from this list, which are not typically uploaded to DNAnexus
    numfqs=$(find $input_directory -iname "*.fastq.gz" | grep -v "Undetermined" |  wc -l);
    # Count the number of undetermined fastqs in input directory
    undetermined=$(find $1 -iname "Undetermined*.fastq.gz" | wc -l);
    total=$((numfqs + undetermined))
    echo "$input_directory has $numfqs demultiplexed fastq files with $undetermined undetermined. Total: $total";
    }

findfastqs $1