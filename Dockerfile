# https://raw.githubusercontent.com/blang/latex-docker/master/Dockerfile.ubuntu

FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive

# Install pdflatex
RUN apt-get update -q && apt-get install -qy \
    texlive-full \
    python-pygments gnuplot \
    make git \
    && rm -rf /var/lib/apt/lists/*

# Install python3
RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Mount point for app code
VOLUME ["/texume"]
WORKDIR /texume

# Mount point for placing latex code
VOLUME ["/src"]

# Mount logs directory
VOLUME ["/tmp/logs/"]

# Ports that shall be exposed
EXPOSE 80 443

CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]

