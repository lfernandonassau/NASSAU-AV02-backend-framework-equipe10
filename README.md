# 📦 Projeto Flask – CRUD com Autenticação e Banco Relacional

Este projeto é uma aplicação **Back-End em Python usando Flask**, criada para demonstrar:

- Criação de entidades e relacionamentos  
- Persistência de dados com **SQLAlchemy**  
- Autenticação básica com **Flask-Login**  
- Operações CRUD completas (Create, Read, Update, Delete)

---

## 🚀 Tecnologias Utilizadas

- Python 3.x  
- Flask  
- Flask SQLAlchemy  
- Flask Login  
- SQLite  
- Werkzeug (hash de senhas)

---


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

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'


