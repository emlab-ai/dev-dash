# Stage 0: Create a reusable base image for Python with necessary tools
FROM python:3.13-alpine as base

# Set working directory
WORKDIR /app

RUN apk update
# Install GCC and other build tools in the base image
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    py3-shapely \
    geos-dev

RUN geos-config --cflags
ENV CFLAGS="-Wno-error=incompatible-pointer-types"

RUN pip install --upgrade pip
RUN pip install poetry

# Copy the requirements file for Python dependencies
# COPY ./server/requirements.txt /app/requirements.txt
COPY ./pyproject.toml /app/pyproject.toml
COPY ./poetry.lock /app/poetry.lock

# Install Python dependencies in the base image
# RUN pip install --no-cache-dir -r /app/requirements.txt
RUN poetry install

# Stage 1: Build the web app
FROM node:22 as builder

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
CMD ["poetry", "run", "python", "/app/server.py"]
