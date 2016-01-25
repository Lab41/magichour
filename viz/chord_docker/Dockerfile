FROM ubuntu:trusty
MAINTAINER "yonast@lab41.org"

RUN apt-get update
RUN apt-get install --assume-yes git nodejs npm
RUN npm install -g bower

# NOTE: There is an open PR that would add support for chord diagrams
RUN git clone git://github.com/densitydesign/raw.git
RUN ln -s /usr/bin/nodejs /usr/bin/node

RUN cd raw && bower --allow-root install

EXPOSE 5000

WORKDIR /raw

CMD ["python", "-m", "SimpleHTTPServer", "5000"]
