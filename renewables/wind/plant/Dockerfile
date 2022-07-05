FROM ghcr.io/sandia-minimega/phenix/phenix:main

COPY ./apps /usr/local/src/windy-app

WORKDIR /usr/local/src/windy-app

RUN pip3 install -e ./

CMD ["phenix", "help"]
