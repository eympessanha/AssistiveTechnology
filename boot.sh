#!/bin/bash

HEADSET_MAC="XX:XX:XX:XX:XX:XX"
PROJECT_FOLDER="/home/ibmec/tcc"

# Waits to assure that the sound system (PulseAudio) has started
sleep 10

echo "Starting bluetooth connections attempts..."

# Tries to connect 5 times before giving up (in case the headset takes time to turn on)
for i in {1..5}
do
   echo "Attempt $i of 5..."
   # The connect command returns success if it connects
   if bluetoothctl connect $HEADSET_MAC; then
       echo "Bluetooth connected successfully!"
       # Set volume to 100% (optional)
       pactl set-sink-volume @DEFAULT_SINK@ 100%
       break
   else
       echo "Failed to connect. Trying again in 5 seconds..."
       sleep 5
   fi
done

# --- START FLASK SERVER ---
echo "Starting Flask server..."
cd $PROJECT_FOLDER
source venv/bin/activate

# Runs the app (the unbuffered -u helps to see logs in real time)
python3 -u app.py