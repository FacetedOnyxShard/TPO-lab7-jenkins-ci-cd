FROM jenkins/jenkins:latest

USER root

RUN apt-get update

RUN apt-get install -y qemu-system-arm unzip wget netcat-traditional
RUN apt-get install -y python3 python3-pip python3-venv
RUN apt-get install -y chromium-driver chromium && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN /opt/venv/bin/pip install selenium requests pytest locust urllib3

USER jenkins
WORKDIR /openbmc-testing

COPY --chown=jenkins:jenkins . .
