# 📦 Projeto Flask – CRUD com Autenticação e Banco Relacional

Este projeto é uma aplicação **Back-End em Python usando Flask**, criada para demonstrar:

- Criação de entidades e relacionamentos  
- Persistência de dados com **SQLAlchemy**  
- Autenticação básica com **Flask-Login**  
- Operações CRUD completas (Create, Read, Update, Delete)

---

## Membros do Grupo 10
#### Daniel Manoel Santos da Silva - 01841723

## 🚀 Tecnologias Utilizadas

- Python 3.x  
- Flask  
- Flask SQLAlchemy  
- Flask Login  
- SQLite  




---

## ⚙️ Funcionalidades

### 🔐 Autenticação
- Login e logout  
- Senhas criptografadas  
- Gerenciamento de sessão com Flask-Login  

### 🧑‍💻 Usuário
- id  
- nome  
- email  
- senha (hash)

### 🏬 Loja
- id  
- nome  
- cnpj (string)  
- contato  
- Relacionamento: **1 Loja → N Produtos**

### 📦 Produto
- id  
- nome  
- preço  
- loja_id (chave estrangeira)

---

## 🗃️ Banco de Dados

Configurado em:


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'


---

 ⚙️ Instalação e Execução

 1️⃣ Criar ambiente virtual

**Windows:**

python -m venv venv
venv\Scripts\activate

2️⃣ Instalar dependências

Após ativar o ambiente:

pip install -r requirements.txt

3️⃣ Rodar a aplicação
python app.py


A API iniciará em:

http://127.0.0.1:5000


