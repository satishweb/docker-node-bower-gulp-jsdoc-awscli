#!/bin/bash
# Node 6.9 (boron) + bower + gulp + jsdoc + awscli Docker image
# Author: Satish Gaikwad <satish@satishweb.com>

# We will always take latest stable ubuntu docker image as base image
FROM node:boron
MAINTAINER Satish Gaikwad <satish@satishweb.com>

RUN apt-get -y update \
        # Lets install base packages required for awscli
        && apt-get install -y python python-pip ca-certificates \
        # Lets install awscli latest version
        && pip install awscli \
		# Lets install bower, gulp and jsdoc
		&& npm install -g bower gulp jsdoc \
        # Remove auto installed unwanted packages post build-essential package bundle removal
        && apt-get -qy autoremove --purge \
        # Removing devel packages, few MBs less :)
        # Lets remove all downloaded packages from cache. This reduces image size significantly.
        # Note: Docker should remove it on its own however no harm having this command here
        && rm -rf /var/cache/apt/archives/*deb \
        # Lets create the entrypoint script to handle switch between invoking of default bash shell and aws command execution.
        # We will launch bash shell if there is/are no input parameter(s)/command given to docker run command
        # We will run aws command by default if CMD is not called by docker run command.
        && echo '#!/bin/bash'>/opt/entrypoint.sh \
        && echo 'set -e && exec "$@"' >>/opt/entrypoint.sh \
        # Lets make entrypoint script executable
        && chmod +x /opt/entrypoint.sh

# This command had to be separate since docker build has problem with dpkg --force-depends command for determining exit status check.
RUN cd /tmp; \
        # awscli help pages use groff command for printing on screen.
        # Installing groff with apt-get installs way too many unwanted packages making image size bigger
        # Installing groff manually with only required libs will keep image size reasonable
        apt-get download groff groff-base && dpkg --force-depends -i *.deb ; rm -rf /tmp/*deb ;\
        # Docker build command fails due to dpkg dependancy errors, we need to ignore errors here hence we exit with code 0 to let docker think this RUN was successful.
        exit 0

# Lets define entrypoint to execute the entrypoint script.
ENTRYPOINT ["/opt/entrypoint.sh"]

# Default argument to pass to entrypoint if docker run command do not pass any arguments.
CMD ["/bin/bash"]