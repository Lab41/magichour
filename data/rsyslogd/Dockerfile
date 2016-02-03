FROM ubuntu:15.10
RUN apt-get update \
    && apt-get -y install rsyslog \
    && apt-get -y install vim \
    && apt-get -y install netcat \
    && apt-get -y install net-tools \
    && update-rc.d rsyslog defaults  
ADD ./logentries.conf /etc/rsyslog.d/logentries.conf
ADD ./rsyslog.conf /etc/rsyslog.conf
ADD ./50-default.conf /etc/rsyslog.d/
EXPOSE 514/udp
EXPOSE 514/tcp
CMD ["/usr/sbin/rsyslogd","-n"]

