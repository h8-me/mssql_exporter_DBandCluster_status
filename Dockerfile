FROM python:3.8-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    unixodbc-dev && \
    rm -rf /var/lib/apt/lists/*

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

RUN echo "deb https://packages.microsoft.com/debian/10/prod/ buster main" > /etc/apt/sources.list.d/mssql-release.list
 
RUN apt-get update && \
    apt-get install -y --no-install-recommends msodbcsql17 && \
    rm -rf /var/lib/apt/lists/*
 
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY exporterfull.py /usr/src/app/exporterfull.py

WORKDIR /usr/src/app

CMD ["python", "exporterfull.py"]
