#!/bin/bash

if [ ! -f "romulus.zip" ]; then
  wget https://jenkins.openbmc.org/job/ci-openbmc/lastSuccessfulBuild/distro=ubuntu,label=docker-builder,target=romulus/artifact/openbmc/build/tmp/deploy/images/romulus/*zip*/romulus.zip
fi

if [ ! -d "romulus" ]; then
  unzip romulus.zip > /dev/null
fi