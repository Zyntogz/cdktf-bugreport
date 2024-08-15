FROM amazonlinux:2023.5.20240722.0

### init image ###
# initialize proxy variables so they can be set as build_args
ARG http_proxy
ARG https_proxy
ARG no_proxy

RUN dnf upgrade -y && \
    # utility tool for adding package sources
    dnf install -y yum-utils && \
    # stuff we need for the image
    dnf install -y python3.11 python3.11-pip \
    # general stuff for ease of use
    bash git unzip vim \
    # stuff for vs code
    tar && \
    dnf clean all && rm -rf /var/cache/yum

# set 3.11 as standard python. this is different from python3 binary, which points to 3.9.
# amazon advises to not switch this pointer, otherwise image-internal stuff may break
# Hence: Ensure to use python binary, not python3!
RUN ln -s /usr/bin/python3.11 /usr/bin/python && \
    # symlink pip binaries for easier usage
    ln -s /usr/bin/pip3.11 /usr/bin/pip && \
    ln -s /usr/bin/pip3.11 /usr/bin/pip3 && \
    # symlink vim to vi to satisfy vs code behavior
    ln -s /usr/bin/vim /usr/bin/vi

# upgrade pip and setuptools
RUN pip install --upgrade pip setuptools

# install pipx into its own venv to keep global env clean
ARG PIPX_VERSION=1.6.0
# make poetry install to this location to isolate its dependencies
ENV PIPX_HOME="/opt/pipx-venv"
RUN python -m venv $PIPX_HOME && \
    # update pip/setuptools used by venv
    $PIPX_HOME/bin/pip install --upgrade pip setuptools && \
    # install pipx
    $PIPX_HOME/bin/pip install pipx==$PIPX_VERSION && \
    # Add pipx to bin
    ln -s $PIPX_HOME/bin/pipx /usr/local/bin/pipx && \
    $PIPX_HOME/bin/python -m pipx ensurepath && \
    pipx ensurepath --global    # optional to allow pipx actions with --global argument

ARG POETRY_VERSION=1.8.3
# install & setup poetry using pipx
RUN pipx install --global poetry==${POETRY_VERSION} && \
    pipx inject --global poetry poetry-plugin-pypi-mirror
ENV PYTHONWARNINGS="ignore:Unverified HTTPS request"

# install dumb-init using pipx
RUN pipx install --global dumb-init

# Poetry settings
# we are working with global python no venv
RUN poetry config virtualenvs.create false && \
    # disable because poetry cannot handle custom certs currently
    poetry config certificates.repo_provided.cert false

# placeholder for $USER
# ENV instead of ARG because subsequent images may use this variable
ENV DEV_USER='dev-user'
# create personal user
RUN useradd ${DEV_USER} -m -s /bin/bash -g users

# Run container as user
USER ${DEV_USER}

# setting python-relevant environment variables
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# set workdir
RUN chown -R ${DEV_USER}:users /app

# run indefinitely
ENTRYPOINT [ "dumb-init", "tail", "-f", "/dev/null" ]

USER root

ARG TERRAFORM_VERSION=1.9.4
RUN dnf upgrade -y && \
    # utility tool for adding package sources
    dnf install -y yum-utils && \
    yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo && \
    # stuff we need for the image
    dnf install -y npm terraform-${TERRAFORM_VERSION}-1 && \
    dnf clean all && rm -rf /var/cache/yum

ARG CDKTF_VERSION=0.20.8
RUN npm install --global cdktf-cli@${CDKTF_VERSION} && \
    npm cache clean --force

# npm best practice
ENV NODE_ENV=production

# commented out because we try to stay with poetry natively
# install pipenv (suggested for cdktf init)
ARG PIPENV_VERISON=2024.0.1
RUN pipx install --global pipenv==${PIPENV_VERISON}

# copy code, change ownership to our future container user
COPY --chown=${DEV_USER}:users ./ .

# Install packages from poetry.lock file
RUN poetry config virtualenvs.create false && poetry install --no-root

USER $DEV_USER

# Install packages from poetry.lock file
RUN poetry config virtualenvs.create true && poetry install --no-root

# Install pipenv packages
RUN pipenv install