# Stage 0: Create a reusable base image for Python with necessary tools
FROM python:3.12-alpine as base

# Set working directory
WORKDIR /app

# Install GCC and other build tools in the base image
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev openssl-dev cargo geos-dev

# Copy the requirements file for Python dependencies
COPY ./server/requirements.txt /app/requirements.txt

# Install Python dependencies in the base image
RUN pip install --no-cache-dir -r /app/requirements.txt

# Stage 1: Build the web app
FROM node:21 as builder

WORKDIR /app

COPY ./web/package.json /app/package.json
COPY ./web/package-lock.json /app/package-lock.json
RUN npm install

COPY ./web /app
COPY ./server /server

RUN npm run build

# Stage 2: Create the runtime container
FROM base as runtime

WORKDIR /app

# Install the required dependencies
COPY --from=builder /server /app
# Copy the built web app from the builder stage
COPY --from=builder /app/dist /app/static/dist

EXPOSE 8080

# Set the entry point command to run the server.py file
CMD ["python", "/app/server.py"]
