# 🚛 Dashboard Avila Transportes

Sistema unificado de gestão para Avila Transportes com integração completa ao Azure.

## 🎯 Funcionalidades

### Core System
- **Dashboard Geral**: Visão consolidada de todos os dados
- **Consulta de Faturas**: Gestão de faturas e faturamento
- **Consulta de Minuta**: Controle de minutas de transporte
- **Financeiro**: Módulo financeiro completo com OFX
- **Emissões**: Controle de emissões de documentos
- **Cotação**: Sistema de cotação de fretes
- **Ordem de Coleta**: Gestão de ordens de coleta
- **Contatos**: Gerenciamento de contatos e clientes

### Recursos Avançados
- **🔐 Autenticação**: Sistema de login com usuários e perfis
- **☁️ Integração Azure**: Backup automático e sincronização
- **📧 Email**: Envio de emails para clientes via SendGrid
- **📊 Monitoramento**: Application Insights para telemetria
- **🗄️ Banco de Dados**: SQL Server no Azure para persistência

## 🚀 Deploy no Azure

### Pré-requisitos
1. **Azure CLI** instalado
2. **Azure Developer CLI (azd)** instalado
3. **Docker** instalado (para containerização)
4. **Conta Azure** com permissões de administrador

### Instalação do Azure Developer CLI
```powershell
# Windows (PowerShell)
winget install microsoft.azd

# Ou baixe em: https://aka.ms/install-azd
```

### Deploy Automático
```bash
# 1. Clone o repositório e navegue até a pasta
cd "d:\Avila DevOps\dashboard\dashboard\dashboard\Banco de dados layout"

# 2. Login no Azure
azd auth login

# 3. Inicialize o projeto (primeira vez)
azd init

# 4. Deploy da infraestrutura e aplicação
azd up
```

### Deploy Manual (Alternativa)
```bash
# 1. Deploy da infraestrutura
az deployment sub create \
  --location "Brazil South" \
  --template-file infra/main.bicep \
  --parameters @infra/main.parameters.json

# 2. Build e push da imagem Docker
az acr build --registry <your-registry> --image dashboard-web .

# 3. Deploy da aplicação
az containerapp update \
  --name <your-app> \
  --resource-group <your-rg> \
  --image <your-registry>.azurecr.io/dashboard-web:latest
```

## 🔧 Configuração

### Variáveis de Ambiente
As seguintes variáveis serão configuradas automaticamente pelo Azure:

```bash
AZURE_CLIENT_ID=<managed-identity-client-id>
AZURE_KEY_VAULT_NAME=<key-vault-name>
STORAGE_ACCOUNT_NAME=<storage-account-name>
SQL_SERVER_NAME=<sql-server-name>
SQL_DATABASE_NAME=<database-name>
APPLICATIONINSIGHTS_CONNECTION_STRING=<app-insights-connection>
```

### Segredos no Key Vault
Os seguintes segredos precisam ser configurados no Azure Key Vault:

1. **SQL-CONNECTION-STRING**: String de conexão do SQL Server
2. **SENDGRID-API-KEY**: Chave API do SendGrid para envio de emails

### Configuração do SendGrid
1. Crie uma conta no [SendGrid](https://sendgrid.com/)
2. Gere uma API Key
3. Adicione a API Key ao Key Vault como `SENDGRID-API-KEY`

## 👥 Gerenciamento de Usuários

### Usuário Padrão
- **Usuário**: admin
- **Senha**: admin123
- **Função**: Administrador

⚠️ **IMPORTANTE**: Altere a senha padrão após o primeiro login!

### Criação de Usuários
1. Faça login como administrador
2. Acesse "👥 Gerenciar Usuários" no menu
3. Preencha os dados do novo usuário
4. Selecione a função (user/admin)

## 📊 Monitoramento

### Application Insights
- **Telemetria**: Logs automáticos da aplicação
- **Performance**: Métricas de performance
- **Erros**: Tracking de erros e exceções
- **Uso**: Estatísticas de uso do sistema

### Logs
Acesse os logs em:
- **Azure Portal** > Application Insights > Logs
- **Kusto Query Language (KQL)** para consultas avançadas

## 🔄 Backup e Sincronização

### Backup Automático
- Todos os CSV são automaticamente sincronizados com o Azure Blob Storage
- Backup pode ser executado manualmente via interface

### Estrutura no Azure Storage
```
csv-files/           # Dados atuais
├── base.csv
├── extrato.csv
├── contatos.csv
└── base_financeira.csv

backup-files/        # Backups históricos
├── base_backup_YYYY-MM-DD.csv
└── ...
```

## 🏗️ Arquitetura

### Componentes Azure
- **Container Apps**: Hosting da aplicação Streamlit
- **SQL Database**: Persistência de dados estruturados
- **Storage Account**: Arquivos CSV e backups
- **Key Vault**: Gestão de segredos e chaves
- **Application Insights**: Monitoramento e telemetria
- **Container Registry**: Imagens Docker
- **Managed Identity**: Autenticação entre serviços

### Fluxo de Dados
```
Streamlit App → Container Apps → SQL Database
     ↓              ↓              ↓
Storage Account ← Key Vault → Application Insights
```

## 🛠️ Desenvolvimento Local

### Instalação
```bash
# 1. Clone o repositório
git clone <repository-url>
cd dashboard

# 2. Instale dependências
pip install -r requirements.txt

# 3. Configure variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# 4. Execute a aplicação
streamlit run main.py
```

### Docker Local
```bash
# Build da imagem
docker build -t dashboard-web .

# Execução local
docker run -p 8000:8000 dashboard-web
```

## 📧 Email e Notificações

### Configuração de Email
1. Configure o SendGrid API Key no Key Vault
2. Customize o domínio de envio (`from_email`) em `azure_integration.py`
3. Teste via interface "📧 Teste de Email"

### Templates de Email
Os emails podem ser customizados no arquivo `azure_integration.py`:
```python
# Exemplo de email personalizado
mail = Mail(
    from_email='noreply@avilatransportes.com',
    to_emails=to_email,
    subject=subject,
    html_content=content
)
```

## 🔒 Segurança

### Boas Práticas Implementadas
- **Managed Identity**: Autenticação sem senhas entre serviços Azure
- **Key Vault**: Todos os segredos centralizados
- **HTTPS**: Comunicação criptografada
- **Role-Based Access**: Controle de acesso baseado em funções
- **Password Hashing**: Senhas com hash SHA-256

### Controle de Acesso
- **Usuários**: Acesso básico ao sistema
- **Administradores**: Acesso completo + gestão de usuários

## 🐛 Troubleshooting

### Problemas Comuns

1. **Erro de Autenticação Azure**
   ```bash
   az login
   azd auth login
   ```

2. **Container não inicia**
   - Verifique os logs no Azure Portal
   - Confirme variáveis de ambiente

3. **Erro de conexão SQL**
   - Verifique firewall do SQL Server
   - Confirme connection string no Key Vault

4. **SendGrid não funciona**
   - Verifique API Key no Key Vault
   - Confirme domínio verificado no SendGrid

### Logs Úteis
```bash
# Container Apps logs
az containerapp logs show --name <app-name> --resource-group <rg-name>

# Application Insights
# Acesse via Azure Portal > Application Insights > Logs
```

## 📞 Suporte

Para suporte técnico:
1. Verifique os logs no Application Insights
2. Consulte a documentação do Azure
3. Entre em contato com o administrador do sistema

## 🎉 Próximos Passos

Após o deploy bem-sucedido:
1. ✅ Altere a senha do usuário admin
2. ✅ Configure o SendGrid para emails
3. ✅ Crie usuários para a equipe
4. ✅ Faça backup inicial dos dados
5. ✅ Configure monitoramento personalizado
6. ✅ Teste todas as funcionalidades
