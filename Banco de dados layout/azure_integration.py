import os
import pandas as pd
from azure.storage.blob import BlobServiceClient
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import streamlit as st
import logging

class AzureIntegration:
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.storage_account_name = os.getenv('STORAGE_ACCOUNT_NAME')
        self.key_vault_name = os.getenv('AZURE_KEY_VAULT_NAME')
        
        # Initialize clients
        self.blob_service_client = None
        self.secret_client = None
        
        if self.storage_account_name:
            self.blob_service_client = BlobServiceClient(
                account_url=f"https://{self.storage_account_name}.blob.core.windows.net",
                credential=self.credential
            )
        
        if self.key_vault_name:
            self.secret_client = SecretClient(
                vault_url=f"https://{self.key_vault_name}.vault.azure.net/",
                credential=self.credential
            )
    
    def get_secret(self, secret_name):
        """Get secret from Azure Key Vault"""
        try:
            if self.secret_client:
                secret = self.secret_client.get_secret(secret_name)
                return secret.value
            return None
        except Exception as e:
            logging.error(f"Error getting secret {secret_name}: {e}")
            return None
    
    def upload_csv_to_blob(self, csv_data, container_name, blob_name):
        """Upload CSV data to Azure Blob Storage"""
        try:
            if self.blob_service_client:
                blob_client = self.blob_service_client.get_blob_client(
                    container=container_name, 
                    blob=blob_name
                )
                
                # Convert DataFrame to CSV string
                if isinstance(csv_data, pd.DataFrame):
                    csv_string = csv_data.to_csv(index=False)
                else:
                    csv_string = csv_data
                
                blob_client.upload_blob(csv_string, overwrite=True)
                return True
            return False
        except Exception as e:
            logging.error(f"Error uploading CSV to blob: {e}")
            return False
    
    def download_csv_from_blob(self, container_name, blob_name):
        """Download CSV data from Azure Blob Storage"""
        try:
            if self.blob_service_client:
                blob_client = self.blob_service_client.get_blob_client(
                    container=container_name, 
                    blob=blob_name
                )
                
                blob_data = blob_client.download_blob()
                csv_content = blob_data.readall().decode('utf-8')
                
                # Convert to DataFrame
                from io import StringIO
                return pd.read_csv(StringIO(csv_content))
            return None
        except Exception as e:
            logging.error(f"Error downloading CSV from blob: {e}")
            return None
    
    def list_blobs_in_container(self, container_name):
        """List all blobs in a container"""
        try:
            if self.blob_service_client:
                container_client = self.blob_service_client.get_container_client(container_name)
                blob_list = container_client.list_blobs()
                return [blob.name for blob in blob_list]
            return []
        except Exception as e:
            logging.error(f"Error listing blobs: {e}")
            return []
    
    def backup_local_files(self):
        """Backup local CSV files to Azure Blob Storage"""
        csv_files = [
            'base.csv',
            'extrato.csv', 
            'contatos.csv',
            'data/base_financeira.csv'
        ]
        
        success_count = 0
        for file_path in csv_files:
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path)
                    blob_name = file_path.replace('/', '_').replace('\\', '_')
                    
                    if self.upload_csv_to_blob(df, 'backup-files', blob_name):
                        success_count += 1
                        logging.info(f"Backed up {file_path} to Azure")
                except Exception as e:
                    logging.error(f"Error backing up {file_path}: {e}")
        
        return success_count, len(csv_files)
    
    def sync_data_to_azure(self, df, table_name):
        """Sync DataFrame to Azure (both Blob and optionally SQL)"""
        try:
            # Upload to Blob Storage
            blob_uploaded = self.upload_csv_to_blob(df, 'csv-files', f"{table_name}.csv")
            
            # If SQL connection string is available, also sync to SQL
            sql_connection = self.get_secret('SQL-CONNECTION-STRING')
            sql_synced = False
            
            if sql_connection:
                try:
                    import sqlalchemy
                    engine = sqlalchemy.create_engine(sql_connection)
                    df.to_sql(table_name, engine, if_exists='replace', index=False)
                    sql_synced = True
                except Exception as e:
                    logging.error(f"Error syncing to SQL: {e}")
            
            return blob_uploaded, sql_synced
        except Exception as e:
            logging.error(f"Error syncing data to Azure: {e}")
            return False, False

def show_azure_status():
    """Show Azure integration status in sidebar"""
    azure = AzureIntegration()
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### ☁️ Status Azure")
        
        # Check environment variables
        storage_account = os.getenv('STORAGE_ACCOUNT_NAME')
        key_vault = os.getenv('AZURE_KEY_VAULT_NAME')
        client_id = os.getenv('AZURE_CLIENT_ID')
        
        if storage_account:
            st.success("✅ Storage Account")
        else:
            st.error("❌ Storage Account")
        
        if key_vault:
            st.success("✅ Key Vault")
        else:
            st.error("❌ Key Vault")
        
        if client_id:
            st.success("✅ Managed Identity")
        else:
            st.error("❌ Managed Identity")
        
        # Test connections
        if st.button("🔄 Testar Conexões"):
            with st.spinner("Testando conexões..."):
                test_results = []
                
                # Test Blob Storage
                try:
                    if azure.blob_service_client:
                        containers = azure.blob_service_client.list_containers()
                        list(containers)  # Try to iterate
                        test_results.append("✅ Blob Storage")
                    else:
                        test_results.append("❌ Blob Storage")
                except:
                    test_results.append("❌ Blob Storage")
                
                # Test Key Vault
                try:
                    if azure.secret_client:
                        azure.secret_client.list_properties_of_secrets()
                        test_results.append("✅ Key Vault")
                    else:
                        test_results.append("❌ Key Vault")
                except:
                    test_results.append("❌ Key Vault")
                
                for result in test_results:
                    if "✅" in result:
                        st.success(result)
                    else:
                        st.error(result)

def backup_to_azure():
    """Backup data to Azure"""
    azure = AzureIntegration()
    
    st.subheader("☁️ Backup para Azure")
    
    if st.button("🔄 Fazer Backup Completo"):
        with st.spinner("Fazendo backup..."):
            success_count, total_files = azure.backup_local_files()
            
            if success_count > 0:
                st.success(f"✅ Backup concluído: {success_count}/{total_files} arquivos")
            else:
                st.error("❌ Falha no backup")
    
    # Show backed up files
    if azure.blob_service_client:
        st.subheader("📁 Arquivos no Azure")
        
        try:
            backup_files = azure.list_blobs_in_container('backup-files')
            csv_files = azure.list_blobs_in_container('csv-files')
            
            if backup_files:
                st.write("**Backup Files:**")
                for file in backup_files:
                    st.write(f"• {file}")
            
            if csv_files:
                st.write("**CSV Files:**")
                for file in csv_files:
                    st.write(f"• {file}")
                    
        except Exception as e:
            st.error(f"Erro ao listar arquivos: {e}")

# Email integration using SendGrid
class EmailService:
    def __init__(self):
        self.azure = AzureIntegration()
        self.api_key = self.azure.get_secret('SENDGRID-API-KEY')
    
    def send_email(self, to_email, subject, content):
        """Send email using SendGrid"""
        try:
            if not self.api_key:
                return False, "SendGrid API key not configured"
            
            import sendgrid
            from sendgrid.helpers.mail import Mail
            
            sg = sendgrid.SendGridAPIClient(api_key=self.api_key)
            
            mail = Mail(
                from_email='noreply@avilatransportes.com',
                to_emails=to_email,
                subject=subject,
                html_content=content
            )
            
            response = sg.send(mail)
            return True, f"Email sent successfully (Status: {response.status_code})"
            
        except Exception as e:
            logging.error(f"Error sending email: {e}")
            return False, str(e)

def show_email_test():
    """Show email testing interface"""
    st.subheader("📧 Teste de Email")
    
    email_service = EmailService()
    
    with st.form("email_test_form"):
        to_email = st.text_input("Email de destino")
        subject = st.text_input("Assunto", value="Teste Dashboard Avila Transportes")
        content = st.text_area("Conteúdo", value="Este é um email de teste do Dashboard Avila Transportes.")
        
        send_button = st.form_submit_button("📤 Enviar Email")
        
        if send_button and to_email and subject and content:
            with st.spinner("Enviando email..."):
                success, message = email_service.send_email(to_email, subject, content)
                
                if success:
                    st.success(message)
                else:
                    st.error(f"Erro ao enviar email: {message}")
