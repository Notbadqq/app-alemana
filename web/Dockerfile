FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

EXPOSE 5000

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /appli/requirements.txt

WORKDIR /appli

RUN pip install Flask && \
	pip install Flask-WTF && \
	pip install flask-sqlalchemy && \
	pip install psycopg2-binary && \
	pip install flask-bootstrap

COPY . /appli

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]
