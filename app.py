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
    "numero progressivo",
    "Data del contatto",
    "Cognome",
    "Nome",
    "Nominativi Ospiti",
    "data presunta di Arrivo",
    "data presunta di Partenza",
    "Numero Ospiti",
    "adulti",
    "minori",
    "Email",
    "Portale di provenienza",
    "Note aggiuntive",
    "Cane (Razza/Taglia)",
    "Esito"
]
# =========================
# BLOCCO 2
# INCOLLA SUBITO SOTTO IL BLOCCO 1
# =========================

def carica_database():

    records = []

    try:

        risposta = requests.get(
            DATABASE_URL,
            timeout=20
        )

        risposta.raise_for_status()

        testo = io.StringIO(risposta.text)

        reader = csv.DictReader(testo)

        for riga in reader:

            record = {}

            for campo in CAMPI_DATABASE:

                record[campo] = riga.get(
                    campo,
                    ""
                ).strip()

            records.append(record)

    except Exception as errore:

        st.error(
            f"Errore lettura database:\n{errore}"
        )

    return records


righe = carica_database()
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
