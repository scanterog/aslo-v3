# Use Slim variant of Python from Docker Hub
FROM python:2.7-slim

# Update Repos and Install git
RUN  apt-get update\
     && apt-get install -y git gettext

# Thanks to  https://github.com/samdroid-apps/aslo/blob/master/activity-build-docker/Dockerfile#L24 for the instructions
# Clone the Sugar Toolkit
RUN git clone https://github.com/sugarlabs/sugar-toolkit-gtk3 --depth=1; \
    mkdir -p /usr/local/lib/python2.7/site-packages;  \
    mv sugar-toolkit-gtk3/src/sugar3 /usr/local/lib/python2.7/site-packages/sugar3; \
    rm -rf sugar-toolkit-gtk3

RUN rm -rf /usr/local/lib/python2.7/site-packages/sugar; \
    ln -s /usr/local/lib/python2.7/site-packages/sugar3 /usr/local/lib/python2.7/site-packages/sugar


# Copy build script to container
COPY build.sh $PWD


# Thanks to https://forums.docker.com/t/is-it-possible-to-pass-arguments-in-dockerfile/14488/3 for the entrypoint tip
ENTRYPOINT ["/build.sh"]
