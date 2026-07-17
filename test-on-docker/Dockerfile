FROM python:slim

RUN useradd --create-home user --uid 1000 --shell /bin/bash

COPY tmp/trash_cli.tar.gz /trash_cli.tar.gz
RUN pip install /trash_cli.tar.gz
ENV PATH="/usr/local/bin:$PATH"

USER user
WORKDIR /home/user

ENTRYPOINT ["/bin/bash"]