FROM python:2.7.18-buster

RUN echo "deb http://archive.debian.org/debian/ buster main" > /etc/apt/sources.list \
 && echo "deb http://archive.debian.org/debian-security/ buster/updates main" >> /etc/apt/sources.list \
 && echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99ignore-valid-until

RUN apt-get update && \
    apt-get install -y --no-install-recommends  \
    sudo vim && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


RUN useradd user --create-home
RUN usermod --append --groups sudo user
RUN usermod --shell /bin/bash user

RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER user
RUN echo 'PATH=/home/user/.local/bin:$PATH' >> /home/user/.bashrc

ADD --chown=user:user  ../.. /opt/trash-cli
WORKDIR /opt/trash-cli

RUN pip install -e /opt/trash-cli /opt/trash-cli[dev]

WORKDIR /home/user

ENTRYPOINT ["bash"]
