FROM public.ecr.aws/lambda/python:3.12

# Copy function code
COPY ./src ${LAMBDA_TASK_ROOT}

# Install any required packages
RUN pip install -r requirements.txt

CMD ["lambda_github_events.handler"]