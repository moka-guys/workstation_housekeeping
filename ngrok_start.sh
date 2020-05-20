#!/bin/bash
# ngrok_start.sh - A script to allow SSH access to the system by running ngrok as a background process
#   Prints SSH details if ngrok is already running.
#   Note: The ngrok process can be closed at anytime with `kill $(pidof ngrok)`

# Get the process ID of ngrok if it is already running on the system
EXISTING_PROCESS=$(pidof ngrok)

if [ -z $EXISTING_PROCESS ] ;then
  # If ngrok is not running, start as a background process and print the url for SSH access
  #   nohup [command] : Keep the process running the command even after you quit the session
  #   ngrok tcp --region eu 22 : Open an connection to ngrok server on port 22
  #   &> /dev/null : Discard stdout and stderr to empty output stream
  #   & : Run as a background process
  nohup ngrok tcp --region eu 22 &> /dev/null &
  # Pause for a few seconds to allow the connection to complete.
  sleep 3
  # Write the ngrok public url for SSH access to the syslog.
  #   Triggers alert in slack with ssh url details and writes to stderr.
  NGROK_URL=$(curl http://localhost:4040/api/tunnels 2>/dev/null | jq ".tunnels[0].public_url")
  logger -s "ngrok_start - new workstation host - $NGROK_URL"
else 
  # If ngrok is already running, print the public url for SSH access to stderr
  NGROK_URL=$(curl http://localhost:4040/api/tunnels 2>/dev/null | jq ".tunnels[0].public_url") 
  echo "ngrok_start - $NGROK_URL" 1>&2
fi
