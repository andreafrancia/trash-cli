FROM python:trixie

RUN apt-get update && \
    apt-get install -y --no-install-recommends  \
    sudo vim && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


RUN useradd user --create-home
RUN usermod --append --groups sudo user
RUN usermod --shell /bin/bash user

RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

ADD --chown=user:user  ../.. /opt/trash-cli

RUN pip install -e /opt/trash-cli

ENTRYPOINT ["bash"]

WORKDIR /home/user
USER user
