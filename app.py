import streamlit as st
import pandas as pd
import re

# --- CONFIGURAZIONE E STILE PREMUIM (DARK MODE) ---
st.set_page_config(page_title="CRM - A Casa di Amici 2026", layout="wide", page_icon="🏨")
st.markdown("""
<style>
    .stApp { background-color: #0b0f19; }
    .card-ospite { background: #1e293b; border: 1px solid #334155; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    .badge { padding: 3px 8px; border-radius: 10px; font-size: 11px; font-weight: bold; }
    .badge-confermata { background-color: #10b981; color: white; }
    .badge-attesa { background-color: #f59e0b; color: white; }
</style>
""", unsafe_allow_html=True)

st.title("🏨 CRM Board Premium")
CSV_URL = "https://github.com/depietromarco65/crm-casa-amici-2026/blob/main/database_ospiti.csv"

# --- LOGICA E VISUALIZZAZIONE ---
try:
    # Lettura basata su indici per evitare errori di nomi colonna
    df = pd.read_csv(CSV_URL, on_bad_lines="skip", engine="python")
    
    # Ricerca
    search = st.text_input("🔍 Cerca ospite...")
    if search:
        df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

    # Renderizzazione Card
    for _, riga in df.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="card-ospite">
                <h4>{riga.iloc[4]} {riga.iloc[5]}</h4>
                <p>Arrivo: {riga.iloc[6]} | Partenza: {riga.iloc[7]}</p>
                <p>Alloggio: {riga.iloc[8]} | Tariffa: {riga.iloc[16]}</p>
            </div>
            """, unsafe_allow_html=True)
except Exception as e:
    st.error(f"Errore caricamento dati: {e}")
