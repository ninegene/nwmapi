#!/usr/bin/env bash

THIS_DIR=$(cd "$(dirname "$0")"; pwd)

ini=${1-development.ini}

paster serve --reload $ini
