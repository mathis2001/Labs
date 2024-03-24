FROM python:3

#Install and update system dependencies
RUN apt update -y; apt install -y supervisor
RUN pip install flask
RUN pip install requests
RUN pip install weasyprint
RUN pip install lxml

#Prepare and setup the working directory
RUN mkdir -p /app
WORKDIR /app
COPY app .
COPY config/supervisord.conf /etc/supervisord.conf

EXPOSE 1337

#Disable pycache
ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT [ "/usr/bin/supervisord", "-c", "/etc/supervisord.conf" ]
