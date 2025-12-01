#!/bin/bash
set -e

echo ">>> Pulling latest"
git pull origin master

echo ">>> Stopping existing containers"
docker compose down

echo  ">>> Building new image"
docker compose build

echo ">>> Starting containers"
docker compose up -d

echo ">>> Cleaning up unused images"
docker image prune -f

echo ">>> Deployment completed successfully!"

