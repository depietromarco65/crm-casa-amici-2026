# =========================
# BLOCCO 1
# SOSTITUISCI LE PRIME RIGHE DEL FILE
# =========================

import streamlit as st
import csv
import io
import requests

from datetime import datetime

st.set_page_config(
    page_title="CRM - A Casa di Amici",
    page_icon="🏡",
    layout="wide"
)

DATABASE_URL = "https://raw.githubusercontent.com/depietromarco65/crm-casa-amici-2026/main/database_ospiti.csv"

CAMPI_DATABASE = [
    "N. Progressivo",
    "Data Contatto",
    "Ora Contatto",
    "Giorni Lead Time",
    "Cognome Capofamiglia",
    "Nome Capofamiglia",
    "Data Presunta Arrivo",
    "Data Presunta Partenza",
    "Alloggio Assegnato",
    "Numero Ospiti Totale",
    "Nominativo Ospiti (Dettaglio + Compleanni + Onomastici)",
    "Adulti",
    "Minori",
    "Email",
    "Portale di Provenienza",
    "Razza Taglia e Nome Cane",
    "Tariffa Totale (€)",
    "Costo Biancheria (€)",
    "Tipo Tariffa (Standard/Non Rimb.)",
    "Stato Saldo",
    "Mezzo di Trasporto e Orario Arrivo",
    "Stato Richiesta",
    "Note Aggiuntive"
]
# =========================
# BLOCCO 2
# INCOLLA SUBITO SOTTO IL BLOCCO 1
# =========================

def carica_database():

    try:

        risposta = requests.get(DATABASE_URL, timeout=20)
        risposta.raise_for_status()

        contenuto = io.StringIO(risposta.text)

        reader = csv.DictReader(contenuto)

        records = []

        for riga in reader:

            record = {}

            for campo in CAMPI_DATABASE:

                valore = riga.get(campo, "")

                if valore is None:
                    valore = ""

                record[campo] = str(valore).strip()

            records.append(record)

        return records

    except Exception as e:

        st.error(f"Errore lettura database: {e}")

        return []
# =========================
# BLOCCO 3
# INCOLLA SUBITO SOTTO IL BLOCCO 2
# =========================

def lead_time(data_contatto, data_arrivo):

    try:

        d1 = datetime.strptime(
            data_contatto,
            "%d/%m/%Y"
        )

        d2 = datetime.strptime(
            data_arrivo,
            "%d/%m/%Y"
        )

        return (d2-d1).days

    except:

        return None
