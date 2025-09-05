# 🥗 Nutri_Lab — Sistema para Nutricionistas

**Nutri_Lab** é uma plataforma desenvolvida para otimizar o trabalho de nutricionistas, permitindo o gerenciamento eficiente de pacientes, consultas, planos alimentares e evolução nutricional. Com uma interface simples e recursos completos, o sistema oferece suporte ao atendimento nutricional diário com agilidade e segurança.

---

## 🚀 Funcionalidades Principais

- ✅ Cadastro de pacientes com dados clínicos e nutricionais
- 🗓️ Agendamento de consultas e histórico de atendimentos
- 📊 Registro da evolução física (peso, IMC, medidas)
- 🥗 Elaboração de planos alimentares personalizados
- 📁 Armazenamento de arquivos e prescrições
- 🔔 Envio de lembretes e notificações
- 👤 Sistema de login com autenticação
- 📎 Geração de relatórios e controle de agenda

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.11+**
- **Django 4+**
- **SQLite3** (banco local para desenvolvimento)
- **Bootstrap** (para o frontend responsivo)
- **JavaScript** e **HTML5** (interface dinâmica)

---

## 📦 Como rodar o projeto localmente

### 1. Clone o repositório
```bash
git clone https://github.com/celsoleite38/nutri_lab.git
cd nutri_lab

 Crie e ative um ambiente virtual (opcional, mas recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Aplique as migrações
python manage.py migrate

# Execute o servidor de desenvolvimento
python manage.py runserver
