# Use Ubuntu 22.04 as a base image
FROM ubuntu:22.04

# Update and install Python, pip, and other necessary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    wget \
    git \
    tini \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Add a user id with 1000. 
ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}
RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

# Make sure the contents of our repo are in ${HOME}
COPY . ${HOME}
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}

# Set the working directory in the container
WORKDIR ${HOME}

# Ensure that /usr/local/bin is in the PATH
ENV PATH="/usr/local/bin:/home/jovyan/.local/bin/:${PATH}"

# Expose the Jupyter Notebook port
EXPOSE 8888

# Install Jupyter and other Python dependencies
# RUN python3 -m pip install --no-cache-dir notebook jupyterlab

# Install dependencies specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Set ENTRYPOINT to handle the arguments passed by Binder
ENTRYPOINT ["tini", "-g", "--"]

# Default command to start Jupyter Notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.default_url=/lab/"]

