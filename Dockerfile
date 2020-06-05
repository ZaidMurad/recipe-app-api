FROM python:3.7-alpine
MAINTAINER Zaid Murad.

ENV PYTHONBUFFERED 1

# Install dependencies
COPY ./requirements.txt /requirements.txt
# We need to install the package that is used for django to communicate with postgres, which implies adding some dependencies required to install that package
RUN apk add --update --no-cache postgresql-client
# This uses the package manager that comes with alpine (called apk) to add a package, (--update) updating the registry before adding it, (--no-cache) without storing the regisrty index on our dockerfile to minimize the number of extra files in our docker container to keep it as small as possible (best practice)
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev
# This installs some temporary packages required while running our requirements, then we remove them when done. (--virtual) sets up an alias for our dependencies so that we remove them later (the alias is the string after it)
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps
# this delets the extra dependencies since we do not need them anymore

# Setup directory structure
RUN mkdir /app
WORKDIR /app
COPY ./app/ /app

RUN adduser -D user
USER user
