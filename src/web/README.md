## how to build and run emlab locally

Make sure you are logged in to AWS(aws configure)


get AWS_SECRET_ACCESS_KEY from local env,and add it to compose.yml file
cat ~/.aws/credentials

from src folder, run this command
docker-compose -f ./build/web/docker-compose.yml up --build

compose file has all required parameters