#!/bin/bash

# Install system-level dependency needed by PyAudio
apt-get update && apt-get install -y portaudio19-dev

# Now install Python dependencies
pip install -r requirements.txt

