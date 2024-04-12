#!/bin/bash

docker build . -t aggregator

docker run -it -v ${PWD}:/code -p 8020:8020 --rm aggregator
