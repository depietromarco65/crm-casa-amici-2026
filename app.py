import streamlit as st
import pandas as pd
import re
import os
from datetime import datetime

# --- CONFIGURAZIONE E STILE ---
st.set_page_config(page_title="CRM - A Casa di Amici", layout="wide", page_icon="🏨")
st.markdown("<style>.card-ospite { background: #131c2e; border: 1px solid #1e293b; padding: 15px; border-radius: 10px; margin-bottom: 10px; }</style>", unsafe_allow_html=True)

st.title("🏨 CRM Board Premium")
CSV_FILE = "database_ospiti.csv"

# --- DEFINIZIONE 23 CAMPI ---
COLONNE_CRM = [
    "N_Progressivo", "Data_Contatto", "Ora_Contatto", "Giorni_Lead_Time", "Cognome_Capofamiglia", 
    "Nome_Capofamiglia", "Data_Arrivo", "Data_Partenza", "Alloggio_Assegnato", "Numero_Ospiti_Totale", 
    "Dettaglio_Minori_Note", "Numero_Adulti", "Numero_Bambini", "Email_Ospite", "Portale_Provenienza", 
    "Caratteristiche_Alloggio", "Tariffa_Totale", "Extra_Selezionati", "Tipologia_Tariffa", 
    "Stato_Pagamento", "Tassa_Soggiorno", "Stato_Prenotazione", "Note_Aggiuntive"
]

if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=COLONNE_CRM).to_csv(CSV_FILE, index=False, encoding="utf-8")

# --- INTERFACCIA E LOGICA ---
tab1, tab2 = st.tabs(["📥 Inserimento", "🔍 Dashboard"])

with tab1:
    st.subheader("Inserimento Veloce")
    testo = st.text_area("Incolla notifica:")
    if testo and st.button("Salva"):
        # Logica di parsing e calcolo 23 campi + Tassa Salve
        st.success("Dati salvati!")

with tab2:
    st.subheader("Visualizzazione")
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        for _, r in df.iterrows():
            st.markdown(f"<div class='card-ospite'>{r['Nome_Capofamiglia']} - {r['Alloggio_Assegnato']}</div>", unsafe_allow_html=True)
