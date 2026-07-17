FROM python:slim

RUN useradd --create-home user --uid 1000 --shell /bin/bash \
    && usermod -aG sudo user \
    && mkdir -p /etc/sudoers.d/ \
    && echo "user ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/user \
    && chmod 0440 /etc/sudoers.d \
    && chmod 0440 /etc/sudoers.d/user

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update -o Dir::Etc::sourcelist="sources.list" \
                      -o Acquire::Languages="none" \
    && apt-get install -y --no-install-recommends \
       sudo \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* # /usr/share/doc/* /usr/share/man/*


COPY tmp/trash_cli.tar.gz /trash_cli.tar.gz
RUN pip install /trash_cli.tar.gz
ENV PATH="/usr/local/bin:$PATH"

USER user
WORKDIR /home/user

ENTRYPOINT ["/bin/bash"]