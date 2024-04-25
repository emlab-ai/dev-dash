#!/bin/bash

# delete the existing zip file if it exists
rm -f functionapp.zip

cd ../server/src
zip -r functionapp.zip . -x "*.git*" "*__pycache__*" ".venv/*"
mv functionapp.zip ../../build/
cd ../../build

# Replace <your_resource_group>, <your_function_app>, and <your_region> with your values
az functionapp deployment source config-zip \
    --resource-group DevDashAI_group \
    --name emlabevents \
    --src ./functionapp.zip \
    --build-remote true

rm -f functionapp.zip

