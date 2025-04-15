FROM python:3.12.9-slim

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    sed cron wget build-essential curl && \
    wget http://download.redis.io/releases/redis-5.0.14.tar.gz && \
    tar xzf redis-5.0.14.tar.gz && \
    cd redis-5.0.14 && \
    make -j$(nproc) && \
    make install && \
    rm -rf redis-5.0.14* && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY templates/ templates/
COPY static/ static/
COPY secret.sh .
RUN chmod +x secret.sh
ENV FLAG2="flag{DOnt_you-daRE-forGEt-Me_:>}"
ENV ATTACKR_FLAG=""
ARG ATTACKR_FLAG
RUN echo $ATTACKR_FLAG > /flag && \
    sed -i "s#<<flag>>#$ATTACKR_FLAG#g" templates/index.html && \
    ./secret.sh

RUN mkdir /etc/redis && \
    echo "bind 0.0.0.0" > /etc/redis/redis.conf && \
    echo "protected-mode no" >> /etc/redis/redis.conf && \
    echo "dir /tmp" >> /etc/redis/redis.conf && \
    chmod 777 /tmp

EXPOSE 5000 6379

CMD ["sh", "-c", "service cron start && redis-server /etc/redis/redis.conf --daemonize yes && python app.py"]