# Stage 0: Create a reusable base image for Python with necessary tools
FROM public.ecr.aws/lambda/python:3.12 as base

# RUN microdnf install -y \
#     gcc \
#     gcc-c++ \
#     python3-devel \
#     libffi-devel \
#     openssl-devel \
#     && microdnf clean all

# # RUN geos-config --cflags
# ENV CFLAGS="-Wno-error=incompatible-pointer-types"

RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry self add poetry-plugin-export

WORKDIR /app
# Copy the requirements file for Python dependencies
# COPY ./server/requirements.txt /app/requirements.txt
COPY ./pyproject.toml /app/pyproject.toml
COPY ./poetry.lock  /app/poetry.lock
RUN poetry self update

RUN poetry export --without-hashes --format requirements.txt --output /app/requirements.txt
# Install Python dependencies in the base image
RUN pip install --no-cache-dir -r  /app/requirements.txt

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

WORKDIR /var/task
# Install the required dependencies
COPY --from=builder /server  ${LAMBDA_TASK_ROOT}
# Copy the built web app from the builder stage
COPY --from=builder /app/dist  ${LAMBDA_TASK_ROOT}/static/dist

# the actuall handler command is overriten in CDK app.py
CMD ["server.handler"]
