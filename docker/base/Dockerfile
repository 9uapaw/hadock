FROM ubuntu:16.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      openjdk-8-jdk \
      net-tools \
      curl \
      libc6 \
      zlib1g \
      zstd \
      libsnappy-dev \
      libssl-dev \
      netcat \
      gnupg \
    && rm -rf /var/lib/apt/lists/*
      
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/

RUN ln -s /opt/hadoop/etc/hadoop /etc/hadoop
RUN ln -s /opt/hadoop /hadoop

RUN mkdir /hadoop-data

ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=/etc/hadoop
ENV MULTIHOMED_NETWORK=1
ENV USER=root
ENV PATH $HADOOP_HOME/bin/:$PATH

ADD entrypoint.sh /entrypoint.sh

RUN chmod a+x /entrypoint.sh

RUN mkdir -p /opt/hadoop/logs
ADD config-set.sh /config-set.sh

ENTRYPOINT ["/entrypoint.sh"]
