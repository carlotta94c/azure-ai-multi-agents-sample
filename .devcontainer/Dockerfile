FROM mcr.microsoft.com/devcontainers/python:3.13-bullseye

# Install pip for Python 3.13
RUN python -m pip install --upgrade pip

# Install the packages required to run the sample 
COPY ./requirements.txt .
RUN pip install -r requirements.txt

ENV ENVIRONMENT=container