FROM python:3.12.9-slim

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends sed && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY templates/ templates/
COPY static/ static/
COPY secret.sh .
RUN chmod +x secret.sh
ENV ATTACKR_FLAG=""
ARG ATTACKR_FLAG
RUN echo $ATTACKR_FLAG > /flag && \
    sed -i "s#<<flag>>#$ATTACKR_FLAG#g" templates/index.html && \
    ./secret.sh

EXPOSE 5000

CMD ["python", "app.py"]