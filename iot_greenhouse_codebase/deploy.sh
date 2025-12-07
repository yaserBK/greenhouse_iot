az deployment group create \
  --resource-group myRG \
  --template-file main.bicep \
  --parameters influxPassword="MyInfluxPassword123" influxToken="supersecret"