FROM ger-is-registry.caas.intel.com/hpc-middleware/python:3.8-slim-buster
LABEL maintainer="Eric Perea"

ARG TOKEN="<ONE_SOURCE_TOKEN>"
ENV http_proxy=http://proxy-dmz.intel.com:911
ENV https_proxy=http://proxy-dmz.intel.com:912
ENV no_proxy=.intel.com,127.0.0.1,localhost
ENV PYTHONUNBUFFERED 1
ENV ONE_SOURCE_TOKEN=${TOKEN}
ENV DEBIAN_FRONTEND=noninteractive
EXPOSE 8000

RUN chmod 777 /tmp
RUN apt-get update && apt-get -yqq install build-essential bash git tmux curl vim dnsutils krb5-user libpam-krb5 python3-kerberos gcc libkrb5-dev && apt-get clean


RUN curl http://certificates.intel.com/repository/certificates/IntelSHA256RootCA-Base64.crt  > /tmp/IntelSHA256RootCA.crt
RUN cat /tmp/IntelSHA256RootCA.crt >> /etc/ssl/certs/ca-certificates.crt

# create root directory for our project in the container
RUN mkdir /app
RUN chmod 777 /app

COPY ./docker-entrypoint.sh /
RUN chmod 755 /docker-entrypoint.sh

# Install any needed packages specified in requirements.txt
RUN git config --global url."https://${ONE_SOURCE_TOKEN}:@github.com/".insteadOf "https://github.com/"
RUN set -o vi

# Copying requirements on its own so that it can be cached in builds
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/
RUN cp /app/.tmux.conf /root/.tmux.conf

RUN cat /tmp/IntelSHA256RootCA.crt > /app/ssl/IntelSHA256RootCA-Base64.crt
ENV SSL_CERT_FILE /app/ssl/IntelSHA256RootCA-Base64.crt

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD []