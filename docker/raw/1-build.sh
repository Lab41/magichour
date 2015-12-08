#!/bin/bash
set -e

# image name
__image=lab41/raw

# build image
echo "Building raw image visualization container"
docker build -t $__image .
