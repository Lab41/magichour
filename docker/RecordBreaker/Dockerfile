FROM phusion/baseimage:latest

MAINTAINER dgrossman

ENV DEBIAN_FRONTEND noninteractive

# accept-java-license
RUN echo /usr/bin/debconf shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections

#install the software needed for compile do the compile
RUN apt-get update && \
 add-apt-repository ppa:webupd8team/java && \
 apt-get update

RUN apt-get install -yq oracle-java6-installer oracle-java6-set-default && \
  apt-get install -yq maven && \
  apt-get install -yq git && \
  apt-get autoremove -yq && \
  apt-get clean -yq && \
  rm -rf /var/lib/apt/lists/* && \
  mkdir /root/work && \
  cd /root/work && \
  mkdir -p /root/.m2/repository && \
  git clone https://github.com/VirtualClarity/RecordBreaker.git && \
  cd RecordBreaker && \
  ln -s /root/.m2/repository jars && \
  mvn package 

#booboo bandaid for running the software with the correct classpath
ADD ./learnstructure /root/work/RecordBreaker/bin/learnstructure

RUN chmod 755 /root/work/RecordBreaker/bin/learnstructure

