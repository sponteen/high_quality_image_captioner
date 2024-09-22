
# ----------------------------------------------------------------
# build image
# ----------------------------------------------------------------

    FROM python:3.10.12 AS compile-image
    ARG DOCKER_USER=user
    ARG DOCKER_APP=aiml

    RUN apt-get update
    RUN apt-get install -y --no-install-recommends build-essential gcc sudo 
    RUN apt-get install -y --no-install-recommends iputils-ping iproute2
    RUN addgroup --system --gid 1000 $DOCKER_USER && adduser --uid 1000 --gid 1000 --home /home/$DOCKER_USER --disabled-password $DOCKER_USER
    USER $DOCKER_USER

    RUN python -m venv /home/$DOCKER_USER/.venv
    RUN . /home/$DOCKER_USER/.venv/bin/activate
    # Make sure we use the virtualenv:
    ENV PATH="/home/$DOCKER_USER/.venv/bin:$PATH"

    # Set environment varibles
    ENV PYTHONDONTWRITEBYTECODE 1
    ENV PYTHONUNBUFFERED 1

    ENV WORKSPACE /data
    ENV APP /app

    # root needs this line to find 'aiml' script
    ENV PYTHONPATH "${PYTHONPATH}:/app/"

    # Set the working directory in docker
    WORKDIR $APP

    # Copy the current directory contents into the container at /app
    COPY . $APP
    COPY ./deploy/entrypoint.sh /
    # download wing remote debugging support
    #RUN wget -qO- https://wingware.com/pub/wingpro/9.1.1.0/wing-debugger-linux-x64-9.1.1.0.tar.bz2 | tar xj -C /home/$DOCKER_USER

    # install module with all dependencies using editable mode (allow hot-reload)
    RUN . /home/$DOCKER_USER/.venv/bin/activate
    # Install any needed packages specified in requirements.txt
    # RUN pip install deploy/models-0.1.6-py2.py3-none-any.whl
    # RUN pip install --no-cache-dir -r requirements/base.txt
    # RUN pip install -r requirements/base.txt
    USER root
    RUN pip install -e .

    
    # in production, install CUDA inside Docker https://medium.com/@albertqueralto/enabling-cuda-capabilities-in-docker-containers-51a3566ad014
    # now is taking prohibitively long...

    # ----------------------------------------------------------------
    # runtime image
    # ----------------------------------------------------------------
    # get a smaller image just with needed files
    # FROM python:3.10.12 AS build-image
    # ARG DOCKER_USER=user
    # ARG DOCKER_APP=aiml

    # RUN addgroup --system --gid 1000 $DOCKER_USER && adduser --uid 1000 --gid 1000 --home /home/$DOCKER_USER --disabled-password $DOCKER_USER
    # USER $DOCKER_USER

    # COPY --from=compile-image --chown=$DOCKER_USER /home/$DOCKER_USER/.venv /home/$DOCKER_USER/.venv
    # COPY --from=compile-image --chown=$DOCKER_USER /entrypoint.sh /entrypoint.sh

    # ENV PATH="/home/$DOCKER_USER/.venv/bin:$PATH"
    # ENV PYTHONPATH "${PYTHONPATH}:/app/"

    # RUN . /home/$DOCKER_USER/.venv/bin/activate

    WORKDIR $WORKSPACE
    USER root


    #EXPOSE $PORT
    ENTRYPOINT ["/entrypoint.sh"]


    # # Use an official Python runtime as a parent image
    # FROM python:3.10.12
    # # Specify the command to run on container start
    # # note: docker compose may override this
    # # uvicorn aiml.aiml:app --host 0.0.0.0 --port 80
    # # uvicorn aiml.aiml:app --host 0.0.0.0 --port 80 --ssl-keyfile=/app/deploy/ssl/privkey.pem --ssl-certfile=/app/deploy/ssl/fullchain.pem

    # CMD ["uvicorn", "aiml.aiml:app", "--host", "0.0.0.0", "--port", "14080"]
    