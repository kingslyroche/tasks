FROM python:3.6-slim

# Upgrade pip
RUN pip install --upgrade pip

COPY . /app

WORKDIR /app

# pip install the local requirements.txt
RUN pip install -r requirements.txt

# Define our command to be run when launching the container
CMD gunicorn app:app --bind 0.0.0.0:$PORT --reload
