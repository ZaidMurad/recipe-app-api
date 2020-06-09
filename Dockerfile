FROM python:3.7-alpine
MAINTAINER Zaid Murad.

ENV PYTHONBUFFERED 1

# Install dependencies
COPY ./requirements.txt /requirements.txt
# In the line below, we add packages that will remain in our docker container even after its built.
# We need to install the package that is used for django to communicate with postgres, which implies adding some dependencies required to install that package
RUN apk add --update --no-cache postgresql-client jpeg-dev
# This uses the package manager that comes with alpine (called apk) to add a package, (--update) is for updating the registry before adding it.
# (--no-cache) means without storing the regisrty index on our dockerfile to minimize the number of extra files in our docker container to keep it as small as possible (best practice)
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
# This installs some temporary packages (dependencies) required for installing the pip packages, then we remove them when done. (--virtual) sets up an alias for our dependencies so that we remove them later (the alias is the string after it)
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps
# this delets the extra dependencies since we do not need them anymore

# Setup directory structure
RUN mkdir /app
WORKDIR /app
COPY ./app/ /app

# we create the directories to have a place to store our media files in our container without getting permission errors
# it is recommended to store any files that may need to be shared with other containers in a sub directory called vol
# -p means make all the sub-directories we need (if u dont include it, it will say there is not vol directory existing)
# media directory is for all media files uploaded by the user
RUN mkdir -p /vol/web/media
# static file is typically used for JS and CSS files
RUN mkdir -p /vol/web/static
RUN adduser -D user
# the next line sets the ownership of vol directory and all sub-directories to the user we added called user (we have to do this before switching to the user in the next command)
# -R means it will set not only vol directory, but also all subdirectories to user ownership
RUN chown -R user:user /vol/
# the next command means that the user can do everything with the directory but the rest can read and execute from the directory
RUN chmod -R 755 /vol/web
USER user
