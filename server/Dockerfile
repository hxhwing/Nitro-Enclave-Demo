FROM amazonlinux

# Install python for running the server and net-tools for modifying network config
RUN yum install python3 net-tools rng-tools -y

RUN rngd -r /dev/urandom

WORKDIR /app


COPY requirements.txt ./
RUN pip3 install -r /app/requirements.txt
RUN echo "PIP REQUIREMENT"
RUN pip3 install aws_encryption_sdk
RUN echo "PIP INSTALL"
COPY run.py ./
COPY server.py ./
COPY traffic-forwarder.py ./
COPY run.sh ./
COPY kmstool_enclave_cli ./
COPY libnsm.so ./

RUN chmod +x run.sh

CMD ["/app/run.sh"]
