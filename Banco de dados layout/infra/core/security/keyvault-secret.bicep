param keyVaultName string
param name string
param secretValue string

resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' existing = {
  name: keyVaultName
}

resource secret 'Microsoft.KeyVault/vaults/secrets@2022-07-01' = {
  parent: keyVault
  name: name
  properties: {
    value: secretValue
  }
}

output secretUri string = secret.properties.secretUri
