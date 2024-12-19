FROM public.ecr.aws/lambda/python:3.12


RUN pip install --upgrade pip
RUN pip install poetry


# Copy function code
COPY ./server ${LAMBDA_TASK_ROOT}

COPY ./pyproject.toml ${LAMBDA_TASK_ROOT}/pyproject.toml
COPY ./poetry.lock ${LAMBDA_TASK_ROOT}/poetry.lock

RUN poetry install

# Install any required packages
# RUN pip install -r requirements.txt

# the actuall handler command is overriten in CDK app.py
CMD ["app.handler"]