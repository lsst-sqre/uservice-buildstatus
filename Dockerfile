FROM       centos:7
MAINTAINER sqre-admin
LABEL      version="0.0.2" description="LSST DM/SQuaRE status microservice" \
           name="lsstsqre/uservice-buildstatus"

USER       root
RUN        yum update -y && \
           yum install -y epel-release && \
           yum repolist && \
           yum install -y git python-pip python-devel && \
	   pip install --upgrade pip && \
           pip install requests sqre-uservice-buildstatus && \
           useradd -d /home/flasker -m flasker

USER flasker
WORKDIR /home/flasker
EXPOSE 5000
CMD sqre-uservice-buildstatus
	   
