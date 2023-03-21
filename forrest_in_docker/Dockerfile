FROM debian:11
RUN apt-get update && apt-get install -y curl \
    # for SDKMan
    zip unzip
    #openjdk-11-jdk
    # java dependencies
    #libasound2 libc6-i386 libc6-x32 libfreetype6 libx11-6 libxext6 libxi6 libxrender1 libxtst6 libasound2-data libpng16-16 libxcb1 libx11-data x11-common

# Install java
RUN set -eux; \
    curl -s "https://get.sdkman.io" | bash; \
    bash -c ". /root/.sdkman/bin/sdkman-init.sh && sdk install java 8.0.302-open"; \
    update-alternatives --install /usr/bin/java java /root/.sdkman/candidates/java/8.0.302-open/bin/java 1; \
    update-alternatives --install /usr/bin/javac javac /root/.sdkman/candidates/java/8.0.302-open/bin/javac 1; 
# RUN set -eux; \
#     mkdir -p /java; \
#     cd /java; \
#     curl -LO https://download.oracle.com/java/19/latest/jdk-19_linux-x64_bin.deb; \
#     dpkg -i jdk-19_linux-x64_bin.deb; \
#     update-alternatives --install /usr/bin/java java /usr/lib/jvm/jdk-19/bin/java 1; \
#     update-alternatives --install /usr/bin/javac javac /usr/lib/jvm/jdk-19/bin/javac 1; 
# javaws="java web start", I don't need it, I think
# update-alternatives --install "/usr/bin/javaws" "javaws" "/usr/lib/jvm/jdk1.7.0/bin/javaws" 1


# Install forrest, along with its dependencies.
# Will end up with one folder: /forrest/apache-forrest-0.9 which contains
# what is needed to build
RUN set -eux; \
    curl -LO https://archive.apache.org/dist/forrest/apache-forrest-0.9-dependencies.tar.gz; \
    curl -LO https://archive.apache.org/dist/forrest/apache-forrest-0.9-dependencies.tar.gz.sha1; \
    echo "`cat apache-forrest-0.9-dependencies.tar.gz.sha1` apache-forrest-0.9-dependencies.tar.gz" | sha1sum -c --quiet -; \
    mkdir -p /forrest; \
    tar --extract --directory /forrest --file apache-forrest-0.9-dependencies.tar.gz; \
    rm -rf apache-forrest-0.9-dependencies.tar.gz*;

RUN set -eux; \
    curl -LO https://archive.apache.org/dist/forrest/apache-forrest-0.9-sources.tar.gz; \
    curl -LO https://archive.apache.org/dist/forrest/apache-forrest-0.9-sources.tar.gz.sha1; \
    echo "`cat apache-forrest-0.9-sources.tar.gz.sha1` apache-forrest-0.9-sources.tar.gz" | sha1sum -c --quiet -; \
    mkdir -p /forrest; \
    tar --extract --directory /forrest --file apache-forrest-0.9-sources.tar.gz; \
    rm -rf apache-forrest-0.9-sources.tar.gz*; \
    cd /forrest/apache-forrest-0.9/main; \
    # this fixes "error: Source option 5 is no longer supported. Use 7 or later."
    sed -i '46s/value="1.5"/value="1.7"/g' build.xml; \
    # And this fixes an encoding issue
    cd java/org/apache/forrest/util; \
    iconv -f iso-8859-1 -t UTF-8 IdGeneratorTransformer.java -o IdGeneratorTransformer.java; \
    cd /forrest/apache-forrest-0.9/main; \
    sed -i '521iencoding="UTF8"' build.xml;


# build forrest
RUN set -eux; \
    cd /forrest/apache-forrest-0.9/main; \
    ./build.sh;

ENV FORREST_HOME=/forrest/apache-forrest-0.9
ENV PATH="${FORREST_HOME}/bin:${PATH}"
