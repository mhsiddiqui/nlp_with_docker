FROM ubuntu:xenial
MAINTAINER Martin Jansche <mjansche@google.com>

#ADD goog_af_unison_wav_22k.tar /usr/local/src/

RUN apt-get update && apt-get install -y \
      automake \
      bc \
      curl \
      g++ \
      git \
      libc-dev \
      libreadline-dev \
      libtool \
      make \
      ncurses-dev \
      nvi \
      libjack-jackd2-dev \ 
      libsmf-dev \
      python-gtk2 \
      python-gtksourceview2 \
      pkg-config \
      python \
      python-dev \
      python-setuptools \
      unzip \
      wavpack \
      wget \
      zip \
      csh \
      alsa \
      alsa-utils \
      alsa* \
      zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*


COPY usr_local /usr/local/

# Fetch and prepare Festival & friends
WORKDIR /usr/local/src
RUN tar -xvsf festlex_CMU.tar.gz 
RUN tar -xvsf festlex_POSLEX.tar.gz
RUN tar -xvsf festlex_OALD.tar.gz 
RUN tar -xvsf festvox_rablpc16k.tar.gz
RUN tar -xvsf festvox_kallpc16k.tar.gz

ENV ESTDIR /usr/local/src/speech_tools
ENV FESTVOXDIR /usr/local/src/festvox
ENV SPTKDIR /usr/local

# Build and install SPTK
WORKDIR /usr/local/src/SPTK-3.10
RUN ./configure --prefix=$SPTKDIR && make && make install

# Build the Edinburgh Speech Tools
WORKDIR /usr/local/src/speech_tools
RUN ./configure && make

# Build Festival
WORKDIR /usr/local/src/festival
RUN ./configure && make

# Build Festvox
WORKDIR /usr/local/src/festvox
RUN ./configure && make

#WORKDIR /usr/local/src
#RUN rm -fr SPTK-3.10
