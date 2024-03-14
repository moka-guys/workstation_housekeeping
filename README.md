# Workstation Housekeeping v1.11

Scripts to manage data on the NGS workstation


## Workstation Cleaner (wscleaner)

Delete local directories that have been uploaded to the DNAnexus cloud storage service.
See wscleaner readme for more info

## ngrok_start.sh

Allow SSH access to the system by running ngrok as a background process. As of v1.11 supports dockerised ngrok instance.

### Installation

See knowledge base article for ngrok installation.

### Usage

Non-dockerised ngrok:

`sudo bash ngrok_start.sh`

Dockerised ngrok:

`sudo bash ngrok_start.sh docker`

### output

The script will output the ngrok connection details

