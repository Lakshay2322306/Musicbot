#!/usr/bin/env bash

# Update and install Chromium and its dependencies
apt-get update
apt-get install -y chromium-browser chromium-chromedriver fonts-liberation libappindicator3-1 libnss3 xdg-utils
