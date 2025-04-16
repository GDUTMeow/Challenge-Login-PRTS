FROM centos:7

# 修复仓库配置
RUN sed -i \
    -e 's|^mirrorlist=|#mirrorlist=|g' \
    -e 's|^#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' \
    /etc/yum.repos.d/CentOS-*.repo

# 安装基础依赖
RUN yum install -y epel-release && \
    yum groupinstall -y "Development Tools" && \
    yum install -y \
    wget \
    curl \
    cronie \
    sed \
    openssl \
    openssl-devel \
    libcurl-devel \
    bzip2 \
    libffi \
    zlib \
    sqlite \
    xz \
    glibc \
    libnsl \
    nss-devel \
    expat && \
    yum clean all && \
    rm -rf /var/cache/yum

# 安装 Redis 5.0.14
RUN cd /usr/local/src && \
    wget -q http://download.redis.io/releases/redis-5.0.14.tar.gz && \
    tar xzf redis-5.0.14.tar.gz && \
    cd redis-5.0.14 && \
    make && \
    make install && \
    rm -rf /usr/local/src/redis-5.0.14.tar.gz /usr/local/src/redis-5.0.14

# 安装预编译 Python 3.9 二进制包
RUN cd /usr/local && \
    wget -q https://github.com/indygreg/python-build-standalone/releases/download/20230726/cpython-3.9.17+20230726-x86_64-unknown-linux-gnu-install_only.tar.gz && \
    tar xzf cpython-3.9.17+20230726-x86_64-unknown-linux-gnu-install_only.tar.gz && \
    ln -sf /usr/local/python/bin/python3.9 /usr/bin/python3 && \
    ln -sf /usr/local/python/bin/python3.9 /usr/bin/python3.9 && \
    ln -sf /usr/local/python/bin/pip3.9 /usr/bin/pip3 && \
    ln -sf /usr/local/python/bin/pip3.9 /usr/bin/pip3.9 && \
    python3 -m pip install --upgrade pip setuptools wheel && \
    rm cpython-3.9.17+20230726-x86_64-unknown-linux-gnu-install_only.tar.gz

WORKDIR /app

# 安装应用依赖
COPY requirements.txt .
RUN CC=gcc PYCURL_SSL_LIBRARY=nss pip3 install --no-cache-dir -r requirements.txt
RUN pip3 list

# 复制应用文件
COPY app.py .
COPY templates/ templates/
COPY static/ static/
COPY secret.sh .
RUN chmod +x secret.sh

# 配置环境变量
ENV FLAG2="flag{DOnt_you-daRE-forGEt-Me_:>}"
ENV ATTACKR_FLAG=""
ARG ATTACKR_FLAG
RUN echo $ATTACKR_FLAG > /flag && \
    sed -i "s#<<flag>>#$ATTACKR_FLAG#g" templates/index.html && \
    ./secret.sh

# 配置 Redis
RUN mkdir -p /etc/redis && \
    echo "bind 0.0.0.0" > /etc/redis/redis.conf && \
    echo "protected-mode no" >> /etc/redis/redis.conf && \
    echo "dir /tmp" >> /etc/redis/redis.conf && \
    chmod 777 /tmp

EXPOSE 5000

# 启动命令
CMD ["sh", "-c", "/usr/sbin/crond && redis-server /etc/redis/redis.conf --daemonize yes && python3 app.py"]