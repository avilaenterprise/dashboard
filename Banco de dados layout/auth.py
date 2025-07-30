import streamlit as st
import hashlib
import json
import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

class AuthenticationManager:
    def __init__(self):
        self.users_file = "users.json"
        self.init_default_users()
        
    def init_default_users(self):
        """Initialize with default admin user if no users exist"""
        if not os.path.exists(self.users_file):
            default_users = {
                "admin": {
                    "password": self.hash_password("admin123"),
                    "role": "admin",
                    "email": "admin@avilatransportes.com",
                    "name": "Administrador"
                }
            }
            self.save_users(default_users)
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_users(self):
        """Load users from JSON file"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_users(self, users):
        """Save users to JSON file"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    
    def authenticate_user(self, username, password):
        """Authenticate user with username and password"""
        users = self.load_users()
        if username in users:
            hashed_password = self.hash_password(password)
            if users[username]["password"] == hashed_password:
                return users[username]
        return None
    
    def create_user(self, username, password, email, name, role="user"):
        """Create new user"""
        users = self.load_users()
        if username in users:
            return False, "Usuário já existe"
        
        users[username] = {
            "password": self.hash_password(password),
            "role": role,
            "email": email,
            "name": name
        }
        self.save_users(users)
        return True, "Usuário criado com sucesso"
    
    def update_password(self, username, new_password):
        """Update user password"""
        users = self.load_users()
        if username in users:
            users[username]["password"] = self.hash_password(new_password)
            self.save_users(users)
            return True
        return False
    
    def get_users(self):
        """Get all users (without passwords)"""
        users = self.load_users()
        safe_users = {}
        for username, user_data in users.items():
            safe_users[username] = {
                "role": user_data["role"],
                "email": user_data["email"],
                "name": user_data["name"]
            }
        return safe_users
    
    def delete_user(self, username):
        """Delete user"""
        users = self.load_users()
        if username in users and username != "admin":  # Protect admin user
            del users[username]
            self.save_users(users)
            return True
        return False

def show_login_page():
    """Show login page"""
    st.title("🚛 Avila Transportes - Dashboard")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("🔐 Login")
        
        with st.form("login_form"):
            username = st.text_input("👤 Usuário")
            password = st.text_input("🔒 Senha", type="password")
            login_button = st.form_submit_button("Entrar", use_container_width=True)
            
            if login_button:
                if username and password:
                    auth_manager = AuthenticationManager()
                    user = auth_manager.authenticate_user(username, password)
                    
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_role = user["role"]
                        st.session_state.user_name = user["name"]
                        st.session_state.user_email = user["email"]
                        st.success("Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Usuário ou senha incorretos!")
                else:
                    st.warning("⚠️ Por favor, preencha todos os campos")
        
        # Default credentials info
        with st.expander("ℹ️ Credenciais Padrão"):
            st.info("""
            **Usuário padrão:**
            - Usuário: admin
            - Senha: admin123
            
            *Por favor, altere a senha após o primeiro login.*
            """)

def show_user_management():
    """Show user management page (admin only)"""
    if st.session_state.get("user_role") != "admin":
        st.error("🚫 Acesso negado. Apenas administradores podem gerenciar usuários.")
        return
    
    st.title("👥 Gerenciamento de Usuários")
    
    auth_manager = AuthenticationManager()
    
    # Create new user
    with st.expander("➕ Criar Novo Usuário"):
        with st.form("create_user_form"):
            new_username = st.text_input("Nome de usuário")
            new_password = st.text_input("Senha", type="password")
            new_email = st.text_input("Email")
            new_name = st.text_input("Nome completo")
            new_role = st.selectbox("Função", ["user", "admin"])
            
            create_button = st.form_submit_button("Criar Usuário")
            
            if create_button:
                if new_username and new_password and new_email and new_name:
                    success, message = auth_manager.create_user(
                        new_username, new_password, new_email, new_name, new_role
                    )
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Por favor, preencha todos os campos")
    
    # List existing users
    st.subheader("📋 Usuários Existentes")
    users = auth_manager.get_users()
    
    for username, user_data in users.items():
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
        
        with col1:
            st.write(f"**{username}**")
        with col2:
            st.write(user_data["name"])
        with col3:
            st.write(user_data["email"])
        with col4:
            st.write(user_data["role"])
        with col5:
            if username != "admin":  # Protect admin user
                if st.button("🗑️", key=f"delete_{username}"):
                    if auth_manager.delete_user(username):
                        st.success(f"Usuário {username} removido")
                        st.rerun()

def check_authentication():
    """Check if user is authenticated"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        show_login_page()
        return False
    return True

def logout():
    """Logout user"""
    for key in ["authenticated", "username", "user_role", "user_name", "user_email"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def show_user_info():
    """Show user info in sidebar"""
    if st.session_state.get("authenticated"):
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 👤 Usuário Logado")
            st.write(f"**Nome:** {st.session_state.get('user_name', 'N/A')}")
            st.write(f"**Usuário:** {st.session_state.get('username', 'N/A')}")
            st.write(f"**Função:** {st.session_state.get('user_role', 'N/A')}")
            
            if st.button("🚪 Logout", use_container_width=True):
                logout()
