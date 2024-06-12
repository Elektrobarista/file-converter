# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3-slim

EXPOSE 5001

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Install cron
RUN apt-get update && apt-get install -y cron

# Copy all files in app directory
WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app

# Add crontab file in the cron directory
COPY crontab /etc/cron.d/maintainer-cron

# Apply cron job
RUN crontab /etc/cron.d/maintainer-cron

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Start the cron service and your application
#CMD ["sh", "-c", "python /app/request_handler/startdb.py && cron && tail -f /var/log/cron.log & gunicorn --bind 0.0.0.0:5001 run:app"]
CMD ["sh", "-c", "cron && su appuser -c 'python /app/request_handler/startdb.py && gunicorn --bind 0.0.0.0:5001 run:app' && tail -f /var/log/cron.log"]