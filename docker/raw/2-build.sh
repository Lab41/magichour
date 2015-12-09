#!/bin/bash

# image name
__image=lab41/raw
__server_port=$1

# run image
docker run -it\
        -p $__server_port:5000 \
        $__image
