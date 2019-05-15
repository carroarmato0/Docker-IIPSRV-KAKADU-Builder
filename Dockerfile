# Base container
FROM centos:6.8

# Administration
LABEL maintainer="carroarmato0@inuits.eu"

# Variables
ENV IIPSRV_REPO         "https://github.com/ruven/iipsrv.git"
ENV IIPSRV_COMMIT       "61bfa65d686fd0c0242a3c0b183ef77fef7364a8"
ENV FPM_VERSION         "1.10.2"
ENV RUBY_VERSION        "2.6.3"
ENV KAKADU_VERSION      "v7_5-01574L"
ENV KAKADU_PKG_VERSION  "7.5.01574-1"
ENV ARCHITECTURE        "Linux-x86-64"

# Add EPEL
RUN yum install -y epel-release

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
    sqlite-devel \
    java-1.7.0-openjdk.x86_64 \
    java-1.7.0-openjdk-devel.x86_64 \
    rpm-build \
    libjpeg-turbo-devel \
    libpng-devel \
    libtiff-devel \
    zlib-devel \
    rpmdevtools \
    fcgi-devel \
    lcms2-devel \
    selinux-policy-devel


# Install RVM
RUN curl -sSL https://rvm.io/mpapis.asc | gpg2 --import - && curl -sSL https://rvm.io/pkuczynski.asc | gpg2 --import - && curl -L get.rvm.io | bash -s stable
# Configure RVM
RUN /bin/bash -l -c "rvm reload && rvm requirements run && rvm install ${RUBY_VERSION} && rvm use ${RUBY_VERSION} --default"
# Install FPM
RUN /bin/bash -l -c "gem install fpm -v ${FPM_VERSION}"
# Copy over Kakadu
ADD "kakadu/${KAKADU_VERSION}" /usr/share/kakadu
# Disable AVX2
RUN cd /usr/share/kakadu && sed -i '/AVX2FLAGS = -mavx2 -mfma/ s/^#*/#/' */make/Makefile-${ARCHITECTURE}-gcc
RUN cd /usr/share/kakadu && sed -i '/#C_OPT += -DKDU_NO_AVX2/ s/^#//' */make/Makefile-${ARCHITECTURE}-gcc
# Disable SSSE3
RUN cd /usr/share/kakadu && sed -i '/SSSE3FLAGS = -mssse3/ s/^#*/#/' */make/Makefile-${ARCHITECTURE}-gcc
RUN cd /usr/share/kakadu && sed -i '/#C_OPT += -DKDU_NO_SSSE3/ s/^#//' */make/Makefile-${ARCHITECTURE}-gcc
# Compile Kakadu
RUN cd /usr/share/kakadu/make; export JAVA_HOME=/usr/lib/jvm/java; make -f Makefile-${ARCHITECTURE}-gcc
# Package Kakadu
RUN /bin/bash -l -c "fpm -s dir -t rpm -n kakadu -v ${KAKADU_PKG_VERSION} -d java-1.7.0-openjdk --provides '/usr/share/kakadu/apps/make/libkdu_v75R.so()(64bit)' --description \"Kakadu SDK with License. Compiled without SSE3 and AVX2, using Java OpenJDK 1.7.0\" /usr/share/kakadu/ /usr/share/java/kdu_jni/"

# Pull IIPSRV
RUN git clone ${IIPSRV_REPO} /root/iipsrv-iipsrv-1.0 && cd /root/iipsrv-iipsrv-1.0 && git checkout ${IIPSRV_COMMIT}
# Copy over SRPM content
ADD "iipsrv-srpm" /root/iipsrv-srpm/
# Compress iipsrv git content to tar.gz
RUN tar -C /root/ -czvf /root/iipsrv-srpm/iipsrv-1.0.tar.gz --exclude-vcs iipsrv-iipsrv-1.0
# Create rpm building environment
RUN rpmdev-setuptree
# Copy things into place
RUN mv /root/iipsrv-srpm/*.spec /root/rpmbuild/SPECS; mv /root/iipsrv-srpm/* /root/rpmbuild/SOURCES/
# Compile and build IIPSRV package
RUN cd /root/rpmbuild; rpmbuild -ba SPECS/iipsrv.spec
