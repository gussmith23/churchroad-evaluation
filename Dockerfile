FROM ubuntu:22.04
ARG MAKE_JOBS=2

# Install apt dependencies. DEBIAN_FRONTEND is necessary for making sure tzdata
# setup runs non-interactively.
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
  && apt-get install -y \
  build-essential \
  curl \
  git
RUN apt-get install -y --no-install-recommends make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
RUN apt-get install -y mecab-ipadic-utf8



# Set up Python.
WORKDIR /root
RUN git clone --depth=1 https://github.com/pyenv/pyenv.git .pyenv
ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH"
WORKDIR /root/churchroad-evaluation
ADD .python-version .python-version
RUN pyenv install $(cat .python-version) && \
  pyenv global $(cat .python-version)

# Install the Python package itself.
ADD requirements.txt requirements.txt
ADD pyproject.toml pyproject.toml
ADD src/ src/
RUN pip3 install .

WORKDIR /root/churchroad-evaluation
ADD run-evaluation.sh run-evaluation.sh
ADD dodo.py dodo.py
ADD benchmarks/ benchmarks/
ADD manifest.yml manifest.yml
ENV CRE_MANIFEST_PATH="/root/churchroad-evaluation/manifest.yml"
# TODO this isn't right. Should really just package the Python code and install
# it rather than hacking the PYTHONPATH; this hack isn't even right.
CMD [ "./run-evaluation.sh" ]
