FROM python:3.8
WORKDIR /app
COPY . .
RUN pip install awscli
RUN pip install .