#!/bin/bash

# delete the existing zip file if it exists
rm -f functionapp.zip

zip -r functionapp.zip ../server/src -x "*.git*" "*__pycache__*" "*deploy.sh*" ".venv/*"

# Replace <your_resource_group>, <your_function_app>, and <your_region> with your values
az functionapp deployment source config-zip \
    --resource-group DevDashAI_group \
    --name emlabevents \
    --src ./functionapp.zip \
    --build-remote true

# az command to create new function python
# az functionapp create --resource-group DevDashAI_group --consumption-plan-location eastus --name processgithubevent --storage-account devdashai --runtime python --functions-version 3 --os-type Linux
