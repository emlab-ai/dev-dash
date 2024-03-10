# Use the official Python image as the base image
FROM python:3.12-alpine

# Set the working directory in the container

COPY ./src ./app

WORKDIR /app
# Install the required dependencies
RUN pip install --no-cache-dir -r ./requirements.txt

EXPOSE 8080
# Set the entry point command to run the server.py file
CMD ["python", "server.py"]