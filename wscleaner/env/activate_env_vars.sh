#!/bin/sh

# Cache the python path
export wsc_PPCACHE=$PYTHONPATH

# Remove the dxtoolkit path from the pythonpath environment variable
# Python searches this when importing modules, causing clashes with conda install 
PYTHONPATH_CLEAN=$(echo $PYTHONPATH | sed s,/usr/share/dnanexus/lib/python2.7/site-packages:,,g)
# Set the new pythonpath
export PYTHONPATH=$PYTHONPATH_CLEAN
