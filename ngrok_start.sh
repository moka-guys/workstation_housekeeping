#!/bin/bash


# Get the process ID of ngrok if it is already running on the system
EXISTING_PROCESS=$(pidof ngrok)

if [ -z $EXISTING_PROCESS ] ;then
  # If ngrok is not running, start as a background process and print the url for SSH access	
  nohup ngrok tcp --region eu 22 &> /dev/null &
  sleep 3
  NGROK_URL=$(curl http://localhost:4040/api/tunnels 2>/dev/null | jq ".tunnels[0].public_url")
  echo $NGROK_URL
else 
  # If ngrok is already running, print the url for SSH access
  NGROK_URL=$(curl http://localhost:4040/api/tunnels 2>/dev/null | jq ".tunnels[0].public_url") 
  echo $NGROK_URL
fi
