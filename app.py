import streamlit as st
import pandas as pd
import re
import os
from datetime import datetime

# --- CONFIGURAZIONE E STILE ---
st.set_page_config(page_title="CRM - A Casa di Amici 2026", layout="wide", page_icon="🏨")
st.markdown("""<style>.reportview-container { background: #0b0f19; } .main { background-color: #0b0f19; color: #f1f5f9; }</style>""", unsafe_allow_html=True)
st.title("🏨 CRM Board Premium — A Casa di Amici")

# --- GESTIONE DATI (Sintesi) ---
if not os.path.exists("database_ospiti.csv"):
    # (Codice di creazione CSV omesso per brevità)
    pass

tab_inserimento, tab_ricerca = st.tabs(["📥 Inserimento", "🔍 Dashboard"])

with tab_inserimento:
    # (Logica di parsing dati e pulsante di salvataggio)
    pass

with tab_ricerca:
    if os.path.exists("database_ospiti.csv"):
        df = pd.read_csv("database_ospiti.csv")
        # Visualizzazione custom con st.markdown e HTML/CSS per badge colorati
        for _, riga in df.iterrows():
            st.markdown(f"**{riga['Nome Ospite']}** - {riga['Stato Prenotazione']}", unsafe_allow_html=True)
