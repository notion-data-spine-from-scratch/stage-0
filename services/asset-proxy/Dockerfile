FROM openresty/openresty:1.25.3.1-3-alpine
RUN apk add --no-cache lua5.4 lua5.4-socket curl python3 py3-pip \
    && pip install boto3
COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
COPY lua /etc/nginx/lua
COPY presign.py /usr/local/bin/presign.py
COPY thumb.py /usr/local/bin/thumb.py
CMD ["openresty", "-g", "daemon off;"]
