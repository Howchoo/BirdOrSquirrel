FROM resin/rpi-raspbian:jessie
MAINTAINER Tyler Jones <tyler@howchoo.com>

# Install dependencies
RUN apt-get update && apt-get install -y \
    git-core \
    build-essential \
    gcc \
    python \
    python-dev \
    python-pip \
    python-picamera \
    python-virtualenv \
    supervisor \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*
RUN git clone git://git.drogon.net/wiringPi
RUN cd wiringPi && ./build

# Create the app directory
RUN mkdir /app
WORKDIR /app

# Add requirements and install
ADD requirements.txt /app/
RUN pip install -r requirements.txt

# Add the supervisor config
ADD supervisor.conf /etc/supervisor/conf.d/

# Create log file
RUN mkdir -p /var/log
RUN touch /var/log/birdorsquirrel.py

# Add the application code
ADD . /app/

CMD ["supervisord", "-n"]
