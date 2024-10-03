#!/bin/bash

# Infinite loop
while true
do
  # Run the command
  actiona --execute script.ascr -E -C -x
 
  # Generate a random sleep time between 30 and 80 seconds
  sleep_time=$((30 + RANDOM % 50))
 
  # Print the random sleep time (optional, for debugging)
  echo "Sleeping for $sleep_time seconds..."

  # Sleep for the random amount of time
  sleep $sleep_time
done

