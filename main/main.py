import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
#from openai import OpenAI
#from dotenv import load_dotenv
#load_dotenv()

# Configuração do logo e título
LOGO_PATH = "C:\\Users\\larissacampos\\Documents\\GitHub\\SiteNivinha\\Captura de tela 2025-10-02 094322.png"  # ajuste o caminho se necessário
st.set_page_config(page_title="Gestão de Pacientes - Nivea Aquino", layout="wide", page_icon=LOGO_PATH)
st.image(LOGO_PATH, width=150)
st.title("Gestão de Pacientes - Nivea Aquino")

# --- Arquivos CSV ---
PATIENTS_FILE = "patients.csv"
APPOINTMENTS_FILE = "appointments.csv"
PAYMENTS_FILE = "payments.csv"

# Funções para carregar e salvar CSVs
def load_csv(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    else:
        return pd.DataFrame(columns=columns)

def save_csv(df, file):
    df.to_csv(file, index=False)

# Carregar dados
patients = load_csv(PATIENTS_FILE, ["Nome", "Sessoes", "Preco", "Horario", "Fixo"])
appointments = load_csv(APPOINTMENTS_FILE, ["Paciente", "Data", "Horario", "Status", "Motivo"])
payments = load_csv(PAYMENTS_FILE, ["Paciente", "Status", "Valor"])

# --- Login ---
users = {"admin": "coxinha123", "Nivinha": "NivinhaEAnaVitoria341"}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    user = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    if st.button("Login"):
        if user in users and users[user] == password:
            st.session_state.logged_in = True
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")
    st.stop()

# --- Menu lateral ---
menu = st.sidebar.radio("Menu", ["Cadastro de Pacientes", "Monitoramento"])

# --- Cadastro de Pacientes ---
if menu == "Cadastro de Pacientes":
    st.header("Cadastro de Pacientes")
    nome = st.text_input("Nome do Paciente")
    sessoes = st.number_input("Quantidade de Sessões por mês", min_value=1)
    preco = st.number_input("Precificação do mês (R$)", min_value=0.0, format="%.2f")
    horario = st.time_input("Horário da consulta")
    fixo = st.checkbox("Paciente fixo neste horário toda semana")

    if st.button("Cadastrar Paciente"):
        if nome and sessoes and preco:
            new_patient = pd.DataFrame([[nome, sessoes, preco, horario.strftime("%H:%M"), fixo]],
                                       columns=["Nome", "Sessoes", "Preco", "Horario", "Fixo"])
            patients = pd.concat([patients, new_patient], ignore_index=True)
            save_csv(patients, PATIENTS_FILE)

            payments = pd.concat([payments, pd.DataFrame([[nome, "Devedor", preco]],
                                                     columns=["Paciente", "Status", "Valor"])], ignore_index=True)
            save_csv(payments, PAYMENTS_FILE)

            if fixo:
                for i in range(sessoes):
                    data = (datetime.now() + timedelta(weeks=i)).strftime("%Y-%m-%d")
                    new_appt = pd.DataFrame([[nome, data, horario.strftime("%H:%M"), "Agendado", ""]],
                                            columns=["Paciente", "Data", "Horario", "Status", "Motivo"])
                    appointments = pd.concat([appointments, new_appt], ignore_index=True)
                save_csv(appointments, APPOINTMENTS_FILE)

            st.success(f"Paciente {nome} cadastrado com sucesso!")
        else:
            st.error("Preencha todos os campos obrigatórios!")

    st.subheader("Pacientes Cadastrados")
    st.dataframe(patients)

# --- Monitoramento ---
elif menu == "Monitoramento":
    st.header("Monitoramento de Pagamentos e Consultas")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Pago")
        pagos = payments[payments["Status"] == "Pago"]
        st.write(pagos)
    with col2:
        st.subheader("Devedor")
        devedores = payments[payments["Status"] == "Devedor"]
        st.write(devedores)
    with col3:
        st.subheader("Parcelado")
        parcelados = payments[payments["Status"] == "Parcelado"]
        st.write(parcelados)

    paciente_pagamento = st.selectbox("Selecionar paciente para atualizar pagamento", patients["Nome"])
    status_pagamento = st.selectbox("Novo status", ["Pago", "Devedor", "Parcelado"])
    if st.button("Atualizar Pagamento"):
        payments.loc[payments["Paciente"] == paciente_pagamento, "Status"] = status_pagamento
        save_csv(payments, PAYMENTS_FILE)
        st.success("Pagamento atualizado!")

    st.subheader("Agendamentos")
    st.dataframe(appointments)

    paciente_ag = st.selectbox("Paciente para remarcar/desmarcar", patients["Nome"])
    nova_data = st.date_input("Nova data")
    motivo = st.text_input("Motivo da alteração")

    if st.button("Remarcar"):
        appointments.loc[appointments["Paciente"] == paciente_ag, ["Data", "Motivo"]] = [nova_data.strftime("%Y-%m-%d"), motivo]
        save_csv(appointments, APPOINTMENTS_FILE)
        st.success("Consulta remarcada!")

    if st.button("Desmarcar"):
        appointments.loc[appointments["Paciente"] == paciente_ag, ["Status", "Motivo"]] = ["Cancelado", motivo]
        save_csv(appointments, APPOINTMENTS_FILE)
        st.success("Consulta desmarcada!")

# --- Chatbot ---
#elif menu == "Chatbot":
#    st.header("Chatbot Inteligente")
    #client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#
    #if not client.api_key:
    #    st.warning("Configure sua chave OpenAI com export OPENAI_API_KEY='sua_chave'")
    #else:
    #    user_input = st.text_input("Você:")
    #    if st.button("Enviar") and user_input:
    #        try:
    #            response = client.chat.completions.create(
    #            model="gpt-3.5-turbo",
    #            messages=[{"role": "user", "content": user_input}]
    #        )
    #            
    #            st.write("Chatbot:", response.choices[0].message.content)
    #        except Exception as e:
    #            st.error(f"Erro: {e}")

