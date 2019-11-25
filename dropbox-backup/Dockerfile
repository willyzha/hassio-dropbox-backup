ARG BUILD_FROM=hassioaddons/base:5.0.2
FROM ${BUILD_FROM}

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

# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_REF
ARG BUILD_VERSION

# Labels
LABEL \
    io.hass.name="Dropbox Backup" \
    io.hass.description="Backup Hass.io snapshots to Dropbox." \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="Willy Zhang <willyzha@gmail.com>" \
    org.label-schema.description="Backup Hass.io snapshots to Dropbox" \
    org.label-schema.build-date=${BUILD_DATE} \
    org.label-schema.name="Dropbox Backup" \
    org.label-schema.schema-version="1.0" \
    org.label-schema.url="https://github.com/willyzha/hassio-dropbox-backup/blob/master/README.md" \
    org.label-schema.usage="https://github.com/willyzha/hassio-dropbox-backup/blob/master/README.md" \
    org.label-schema.vcs-ref=${BUILD_REF} \
    org.label-schema.vcs-url="https://github.com/willyzha/hassio-dropbox-backup" \
    org.label-schema.vendor="Willy's Hass.io Add-ons"
