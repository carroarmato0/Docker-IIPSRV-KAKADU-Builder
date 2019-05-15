# Base container
FROM centos:6.8

# Administration
LABEL maintainer="carroarmato0@inuits.eu"

# Variables
ENV IIPSRV_REPO     "https://github.com/ruven/iipsrv.git"
ENV IIPSRV_COMMIT   "61bfa65d686fd0c0242a3c0b183ef77fef7364a8"
ENV FPM_VERSION     "1.10.2"
ENV RUBY_VERSION    "2.6.3"

# Install packages
RUN yum install -y \
    git \
    gcc-c++ \ 
    patch \
    readline \
    readline-devel \
    zlib \
    zlib-devel \
    libyaml-devel \
    libffi-devel \
    openssl-devel \
    make \
    bzip2 \
    autoconf \
    automake \
    libtool \
    bison \
    iconv-devel \
    sqlite-devel

# Install RVM
RUN curl -sSL https://rvm.io/mpapis.asc | gpg2 --import - && curl -sSL https://rvm.io/pkuczynski.asc | gpg2 --import - && curl -L get.rvm.io | bash -s stable
# Configure RVM
RUN /bin/bash -l -c "rvm reload && rvm requirements run && rvm install ${RUBY_VERSION} && rvm use ${RUBY_VERSION} --default"
# Install FPM
RUN /bin/bash -l -c "gem install fpm -v ${FPM_VERSION}"
# Pull IIPSRV
RUN git clone ${IIPSRV_REPO} /root/iipsrv && cd /root/iipsrv && git checkout ${IIPSRV_COMMIT}