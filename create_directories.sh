#!/bin/sh

echo "Creating directories ....."

echo "Creating directory for storing downloaded repositories"
mkdir -p /tmp/activities

echo "Creating directories to store downloded bundled activities"

sudo mkdir -p /opt/bundles
sudo chmod +w -R /opt/bundles/

echo "Done "