ARG BUILD_FROM
FROM $BUILD_FROM

# Add env
ENV LANG C.UTF-8

# Setup base
RUN apk add --no-cache jq curl findutils python3 python3-dev && \
    pip3 install requests python-dateutil==2.6.1 pytz==2018.3 dropbox==9.4.0

# Copy data
COPY run.sh /
COPY dropbox_uploader.py /
COPY backup_cleanup.py /
RUN ["chmod", "a+x", "/run.sh"]
RUN ["chmod", "a+x", "/dropbox_uploader.py"]
RUN ["chmod", "a+x", "/backup_cleanup.py"]
WORKDIR /

CMD [ "/run.sh" ]