#!/bin/bash

docker run -d \
  --name jenkins-openbmc \
  -p 8080:8080 \
  -v jenkins_data:/var/jenkins_home \
  -v $(pwd)/romulus:/romulus \
  -v ~/.ssh:/var/jenkins_home/.ssh \
  --privileged \
  jenkins-openbmc:latest