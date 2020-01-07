FROM python:3
RUN pip install pygresql
COPY . /app
WORKDIR /app
CMD [ "python", "./testScript.py" ]