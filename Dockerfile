FROM ubuntu:22.04
ARG MAKE_JOBS=2

# Install apt dependencies. DEBIAN_FRONTEND is necessary for making sure tzdata
# setup runs non-interactively.
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
  && apt-get install -y \
  locales \
  python3 \
  python3-pip

# Set the locale. Necessary for Vivado.
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
  locale-gen
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8     

# Set up Python.
WORKDIR /root
ADD requirements.txt requirements.txt
RUN pip3 install --requirement requirements.txt 

WORKDIR /root
ADD run-evaluation.sh run-evaluation.sh
ADD dodo.py dodo.py
CMD [ "./run-evaluation.sh" ]
