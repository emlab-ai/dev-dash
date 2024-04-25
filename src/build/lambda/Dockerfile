FROM public.ecr.aws/lambda/python:3.12

# Copy function code
COPY ./server ${LAMBDA_TASK_ROOT}

# Install any required packages
RUN pip install -r requirements.txt

# the actuall handler command is overriten in CDK app.py
CMD ["app.handler"] 