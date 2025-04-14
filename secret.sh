#!/bin/sh

secret_key=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 16)
sed -i "s#{{secret}}#${secret_key}#g" app.py
