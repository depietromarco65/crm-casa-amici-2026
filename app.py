import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURAZIONE ARCHITETTURA E INTERFACCIA IMMERSIVA ---
st.set_page_config(page_title="CRM BOARD - A Casa di Amici", layout="wide", page_icon="🏨")

# Iniezione di fogli di stile CSS per la Dark Mode Premium e i Badge Neon
st.markdown("""
<style>
    .stApp { background-color: #0b1329; color: #f1f5f9; }
    h1 { color: #ffffff; font-family: 'Inter', sans-serif; font-weight: 800; tracking-tight: -0.05em; }
    .card-ospite {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        padding: 22px;
        border-radius: 14px;
        margin-bottom: 16px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s;
    }
    .card-ospite:hover { transform: translateY(-2px); border-color: #475569; }
    .badge {
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-verde { background-color: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.4); }
    .badge-giallo { background-color: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.4); }
    .badge-rosso { background-color: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.4); }
    .badge-grigio { background-color: rgba(148, 163, 184, 0.15); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.4); }
    .griglia-info { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 10px; font-size: 14px; }
    .dato-evidenziato { color: #e2e8f0; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.title("🏨 A Casa di Amici — Dashboard Direzionale")
st.markdown("---")

CSV_URL = "https://githubusercontent.com"

# --- 2. LETTURA SICURA E ADATTAMENTO DINAMICO DEI CAMPI ---
try:
    # Scarica il file saltando le righe corrotte ed evitando i blocchi del motore C
    df = pd.read_csv(CSV_URL, on_bad_lines="skip", engine="python")
    
    if not df.empty:
        # Pulizia preventiva degli spazi nascosti nell'intestazione di GitHub
        df.columns = df.columns.str.strip()
        
        # Creazione del pannello dei filtri ad alto contrasto
        c_f1, c_f2 = st.columns([2, 1])
        with c_f1:
            ricerca_testuale = st.text_input("✍ Cerca all'istante per nome, e-mail o note interne:", placeholder="Digita per filtrare i record...").strip().lower()
        with c_f2:
            filtro_portale = st.selectbox("🌐 Isola per Portale:", ["Tutti i Canali"] + list(df.iloc[:, 14].dropna().unique()))

        # Applicazione logica dei filtri sul DataFrame in memoria
        df_filtrato = df.copy()
        if filtro_portale != "Tutti i Canali":
            df_filtrato = df_filtrato[df_filtrato.iloc[:, 14] == filtro_portale]
            
        if ricerca_testuale:
            maschera = df_filtrato.apply(lambda row: row.astype(str).str.lower().str.contains(ricerca_testuale).any(), axis=1)
            df_filtrato = df_filtrato[maschera]

        # --- 3. RENDERIZZAZIONE DEL COMPONENTE GRAFICO PREMIUM ---
        if not df_filtrato.empty:
            st.caption(f"Visualizzazione di {len(df_filtrato)} pratiche commerciali filtrate.")
            
            # Scorriamo il database al contrario per mostrare i lead più freschi in cima allo schermo
            for idx in reversed(df_filtrato.index):
                riga = df_filtrato.loc[idx]
                
                # Estrazione posizionale sicura indicizzata sull'array reale a 23 colonne
                id_progressivo = str(riga.iloc[0]).replace(".0", "")
                data_contatto = str(riga.iloc[1])
                cognome = str(riga.iloc[4]) if str(riga.iloc[4]) != "nd" else ""
                nome_ospite = f"{cognome} {str(riga.iloc[5])}".strip()
                arrivo = str(riga.iloc[6])
                partenza = str(riga.iloc[7])
                alloggio = str(riga.iloc[8]) if str(riga.iloc[8]) != "nd" else "Da assegnare"
                portale = str(riga.iloc[14])
                tariffa = str(riga.iloc[16]) if str(riga.iloc[16]) != "nd" else "0.00"
                stato = str(riga.iloc[21]).strip()
                note_interne = str(riga.iloc[22]) if len(str(riga.iloc[22])) > 2 else "Nessuna nota aggiuntiva d'esercizio."

                # Mappatura cromatica dello stato per l'assegnazione dei badge fluo
                st_low = stato.lower()
                if "conferma" in st_low or "corso" in st_low:
                    classe_colore = "badge-verde"
                elif "attesa" in st_low or "sospeso" in st_low:
                    classe_colore = "badge-giallo"
                elif "non contattabile" in st_low:
                    classe_colore = "badge-grigio"
                else:
                    classe_colore = "badge-rosso"

                # Stampa a schermo della Card HTML personalizzata
                st.markdown(f"""
                <div class="card-ospite">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #334155; padding-bottom: 8px;">
                        <span style="font-size: 18px; font-weight: 800; color: #ffffff; tracking-tight: -0.02em;">#{id_progressivo} | {nome_ospite}</span>
                        <span class="badge {classe_colore}">{stato}</span>
                    </div>
                    <div class="griglia-info">
                        <div>📅 <span style="color: #94a3b8;">Soggiorno:</span> <span class="dato-evidenziato">{arrivo} ➔ {partenza}</span></div>
                        <div>🏠 <span style="color: #94a3b8;">Unità Assegnata:</span> <span class="dato-evidenziato" style="color: #6366f1;">{alloggio}</span></div>
                        <div>💶 <span style="color: #94a3b8;">Tariffa Alloggio:</span> <span class="dato-evidenziato" style="color: #10b981;">€ {tariffa}</span></div>
                        <div>🌐 <span style="color: #94a3b8;">Canale d'Origine:</span> <span class="dato-evidenziato">{portale}</span></div>
                    </div>
                    <div style="margin-top: 14px; font-size: 13px; color: #94a3b8; background-color: rgba(15, 23, 42, 0.4); padding: 10px; border-radius: 6px; border-left: 3px solid #475569;">
                        📌 <b>LOGISTICA E NOTE CRM:</b> {note_interne} <span style="float: right; font-size: 11px; color: #64748b;">Contatto: {data_contatto}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("❌ Nessun record trovato nel database corrispondente ai filtri impostati.")
    else:
        st.info("📂 Il database ospiti risulta attualmente vuoto su GitHub.")
except Exception as e:
    st.error(f"🛑 Errore nel caricamento del database ospiti. Assicurati che il file database_ospiti.csv su GitHub sia formattato correttamente.")
