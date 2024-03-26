
# create azure function
az functionapp create --resource-group DevDashAI_group --consumption-plan-location ukwest --name emlabevents --runtime python --functions-version 4 --os-type Linux -s emlabaistorage