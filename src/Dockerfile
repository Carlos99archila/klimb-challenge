FROM --platform=linux/amd64 python:3.11

COPY . /app

# Set the working directory to /app
WORKDIR /app
ENV ACCEPT_EULA=Y
ENV DEBIAN_FRONTEND=noninteractive

# Install FreeTDS and dependencies for PyODBC DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install apt-utils curl -y
RUN curl https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc
RUN curl https://packages.microsoft.com/config/debian/11/prod.list | tee /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18
# optional: for bcp and sqlcmd
RUN ACCEPT_EULA=Y apt-get install -y mssql-tools18
RUN echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc \
    source ~/.bashrc
RUN apt-get install -y unixodbc-dev
# optional: kerberos library for debian-slim distributions
# RUN apt-get install -y libgssapi-krb5-2
RUN apt-get clean -y
# Para cuando se instala FreeTDS
# ADD odbcinst.ini /etc/odbcinst.ini
# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY certs/server-ca.pem /etc/ssl/certs

# Instala las dependencias de python
#RUN pip install -r requirements.txt 

# Ejecuta la aplicación utilizando uvicorn
CMD exec uvicorn main:app --port $PORT --host 0.0.0.0 --workers $WORKERS
#CMD exec gunicorn main:app --workers $WORKERS --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
