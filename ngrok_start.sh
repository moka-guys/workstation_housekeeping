#!/bin/bash
# ngrok_start.sh - A script to allow SSH access to the system by running ngrok as a background process
#   Prints SSH details if ngrok is already running.
#   Note: The ngrok process can be closed at anytime with `kill $(pidof ngrok)`

# Get the process ID of ngrok if it is already running on the system
EXISTING_PROCESS=$(pidof ngrok)
ngrok_instance=$1
# If ngrok is not running, start as a background process and print the url for SSH access
if [ -z $EXISTING_PROCESS ] ;then
  if [[ $ngrok_instance == "docker" ]]; then
    #   cat the ngrok password into a variable so it can be passed as a environment argument to docker (-e)
    #   run docker container in detached mode (-d) 
    #   name the instance
    #   set --net=host attaches the container to the host network, rather than the docker network - this means ports don't need to be remapped.
    #   and use ngrok/ngrok:latest tcp --region eu 22 : Open an connection to ngrok server on port 22
    #   &> /dev/null : Discard stdout and stderr to empty output stream
    ngrok_token=$(cat /usr/local/src/mokaguys/.ngrok)
    docker run -d --name NGROK --net=host -it -e NGROK_AUTHTOKEN=$ngrok_token ngrok/ngrok:latest tcp 22 --region eu &> /dev/null
  else
    #   nohup [command] : Keep the process running the command even after you quit the session
    #   ngrok tcp --region eu 22 : Open an connection to ngrok server on port 22
    #   &> /dev/null : Discard stdout and stderr to empty output stream
    #   & : Run as a background process
    nohup ngrok tcp --region eu 22 &> /dev/null &
  fi
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
