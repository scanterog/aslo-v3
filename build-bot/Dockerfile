# Use Slim variant of Python from Docker Hub
FROM python:3-slim

# Update Repos and Install git
RUN  apt-get update\
     && apt-get install -y git

# Thanks to  https://github.com/samdroid-apps/aslo/blob/master/activity-build-docker/Dockerfile#L24 for the instructions
# Clone the Sugar Toolkit
RUN git clone https://github.com/sugarlabs/sugar-toolkit-gtk3 --depth=1; \
    mkdir -p /usr/lib/python3/site-packages;  \
    mv sugar-toolkit-gtk3/src/sugar3 /usr/lib/python3/site-packages/sugar3; \
    rm -rf sugar-toolkit-gtk3

# Copy build script to container
COPY build.sh $PWD

CMD ['bash', 'build.sh']
