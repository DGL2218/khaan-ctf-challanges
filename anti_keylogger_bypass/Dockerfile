FROM python:3.11-slim

# Install system dependencies, including SSH server, tmux, and sudo
RUN apt-get update && apt-get install -y \
    openssh-server \
    sudo \
    tmux \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set up SSH
RUN mkdir -p /var/run/sshd
RUN echo 'root:rootpassword' | chpasswd
# Allow root login for administration (optional, but good for local troubleshooting)
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# Create low-privilege user 'ctf' with password 'ctf'
RUN useradd -rm -d /home/ctf -s /bin/bash -g root -G sudo -u 1000 ctf
RUN echo 'ctf:ctf' | chpasswd

WORKDIR /app
COPY challenge/ /app/

# Set up supervisord or simple startup script to run our daemons
COPY challenge/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 22

ENTRYPOINT ["/app/entrypoint.sh"]
