@description('Resource group location')
param location string = resourceGroup().location

@description('Azure Container Registry name')
param acrName string = 'myregistry123'

@description('Container Apps environment name')
param envName string = 'greenhouse-env'

@description('InfluxDB admin password')
@secure()
param influxPassword string

@description('InfluxDB admin token')
@secure()
param influxToken string

@description('Model container image tag')
param modelImage string = 'gam-model:v1'

@description('Influx container image tag')
param influxImage string = 'influx:v1'

@description('Grafana container image tag')
param grafanaImage string = 'grafana:v1'

@description('Azure Container Apps workload name prefix')
param appPrefix string = 'greenhouse'

//
// ─────────────────────────────────────────────────────────────
// 1. Azure Container Registry
// ─────────────────────────────────────────────────────────────
//

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

//
// ─────────────────────────────────────────────────────────────
// 2. Container Apps Environment
// ─────────────────────────────────────────────────────────────
//

resource caEnv 'Microsoft.Web/containerApps/environments@2023-05-01' = {
  name: envName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: '00000000-0000-0000-0000-000000000000'
        sharedKey: 'dummyKey'
      }
    }
  }
}

//
// ─────────────────────────────────────────────────────────────
// 3. InfluxDB Container App (internal only)
// ─────────────────────────────────────────────────────────────
//

resource influxdbApp 'Microsoft.Web/containerApps@2023-05-01' = {
  name: '${appPrefix}-influxdb'
  location: location
  properties: {
    managedEnvironmentId: caEnv.id
    configuration: {
      ingress: {
        external: false
        targetPort: 8086
      }
      registries: [
        {
          server: '${acrName}.azurecr.io'
          username: acr.listCredentials().username
          passwordSecretRef: 'acrPwd'
        }
      ]
      secrets: [
        {
          name: 'acrPwd'
          value: acr.listCredentials().passwords[0].value
        }
        {
          name: 'influxPassword'
          value: influxPassword
        }
        {
          name: 'influxToken'
          value: influxToken
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'influxdb'
          image: '${acrName}.azurecr.io/${influxImage}'
          env: [
            { name: 'DOCKER_INFLUXDB_INIT_MODE', value: 'setup' }
            { name: 'DOCKER_INFLUXDB_INIT_USERNAME', value: 'admin' }
            { name: 'DOCKER_INFLUXDB_INIT_PASSWORD', secretRef: 'influxPassword' }
            { name: 'DOCKER_INFLUXDB_INIT_ORG', value: 'greenhouse' }
            { name: 'DOCKER_INFLUXDB_INIT_BUCKET', value: 'gc_data' }
            { name: 'DOCKER_INFLUXDB_INIT_ADMIN_TOKEN', secretRef: 'influxToken' }
          ]
        }
      ]
    }
  }
}

//
// ─────────────────────────────────────────────────────────────
// 4. Grafana (external ingress)
// ─────────────────────────────────────────────────────────────
//

resource grafanaApp 'Microsoft.Web/containerApps@2023-05-01' = {
  name: '${appPrefix}-grafana'
  location: location
  properties: {
    managedEnvironmentId: caEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 3000
      }
      registries: [
        {
          server: '${acrName}.azurecr.io'
          username: acr.listCredentials().username
          passwordSecretRef: 'acrPwd'
        }
      ]
      secrets: [
        {
          name: 'acrPwd'
          value: acr.listCredentials().passwords[0].value
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'grafana'
          image: '${acrName}.azurecr.io/${grafanaImage}'
          env: [
            { name: 'GF_SECURITY_ADMIN_PASSWORD', value: 'admin' }
          ]
        }
      ]
    }
  }
}

//
// ─────────────────────────────────────────────────────────────
// 5. Model API Container App (internal)
// ─────────────────────────────────────────────────────────────
//

resource modelApp 'Microsoft.Web/containerApps@2023-05-01' = {
  name: '${appPrefix}-model'
  location: location
  properties: {
    managedEnvironmentId: caEnv.id
    configuration: {
      ingress: {
        external: false
        targetPort: 8000
      }
      registries: [
        {
          server: '${acrName}.azurecr.io'
          username: acr.listCredentials().username
          passwordSecretRef: 'acrPwd'
        }
      ]
      secrets: [
        {
          name: 'acrPwd'
          value: acr.listCredentials().passwords[0].value
        }
        {
          name: 'influxToken'
          value: influxToken
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'model'
          image: '${acrName}.azurecr.io/${modelImage}'
          env: [
            { name: 'INFLUX_URL', value: 'http://${appPrefix}-influxdb:8086' }
            { name: 'INFLUX_TOKEN', secretRef: 'influxToken' }
            { name: 'INFLUX_ORG', value: 'greenhouse' }
            { name: 'INFLUX_BUCKET', value: 'gc_data' }
          ]
        }
      ]
    }
  }
}

//
// ─────────────────────────────────────────────────────────────
// 6. Scheduled Prediction Job
// ─────────────────────────────────────────────────────────────
//

resource predictionJob 'Microsoft.Web/containerApps/jobs@2023-05-01' = {
  name: '${appPrefix}-predictor-job'
  location: location
  properties: {
    environmentId: caEnv.id
    configuration: {
      triggerType: 'Schedule'
      scheduleTriggerConfig: {
        cronExpression: '*/5 * * * *'
      }
      registries: [
        {
          server: '${acrName}.azurecr.io'
          username: acr.listCredentials().username
          passwordSecretRef: 'acrPwd'
        }
      ]
      secrets: [
        {
          name: 'acrPwd'
          value: acr.listCredentials().passwords[0].value
        }
        {
          name: 'influxToken'
          value: influxToken
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'model'
          image: '${acrName}.azurecr.io/${modelImage}'
          env: [
            { name: 'INFLUX_URL', value: 'http://${appPrefix}-influxdb:8086' }
            { name: 'INFLUX_TOKEN', secretRef: 'influxToken' }
            { name: 'INFLUX_ORG', value: 'greenhouse' }
            { name: 'INFLUX_BUCKET', value: 'gc_data' }
          ]
        }
      ]
    }
  }
}
