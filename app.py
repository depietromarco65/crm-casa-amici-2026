import streamlit as st
import requests
import csv

# --- 1. CONFIGURAZIONE INTERFACCIA PUGLIA LIGHT & WARM (CON CORREZIONE BUG SCROLL) ---
st.set_page_config(page_title="CRM BOARD - A Casa di Amici 2026", layout="wide", page_icon="🏨")

# Iniezione CSS avanzata per bloccare lo sfondo chiaro ed evitare l'oscuramento durante lo scroll
st.markdown("""
<style>
    html, body, .stApp, .main, [data-testid="stAppViewContainer"] {
        background-color: #fcfbf7 !important;
        background-attachment: fixed !important;
        color: #2d3748 !important;
    }
    h1 { color: #1a202c !important; font-family: 'Inter', sans-serif; font-weight: 800; tracking-tight: -0.05em; text-align: center; margin-top: 5px; }
    .container-logo { display: flex; justify-content: center; align-items: center; padding: 15px 0; margin-bottom: 5px; }
    .logo-aziendale { max-width: 280px; height: auto; filter: drop-shadow(0px 4px 6px rgba(0, 0, 0, 0.05)); }
    
    /* Card stile pietra leccese bianca con bordi morbidi e ombreggiature stabili */
    .card-ospite {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        padding: 22px;
        border-radius: 14px;
        margin-bottom: 16px;
        box-shadow: 0 4px 15px -3px rgba(148, 120, 80, 0.08);
    }
    
    /* Badge di stato a tonalità pastello mediterranee ad alto contrasto */
    .badge {
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
    }
    .badge-verde { background-color: #e6fffa !important; color: #008767 !important; border: 1px solid #b2f5ea !important; }
    .badge-giallo { background-color: #fefcbf !important; color: #b7791f !important; border: 1px solid #faf089 !important; }
    .badge-rosso { background-color: #fed7d7 !important; color: #c53030 !important; border: 1px solid #feb2b2 !important; }
    .badge-grigio { background-color: #edf2f7 !important; color: #4a5568 !important; border: 1px solid #e2e8f0 !important; }
    
    .griglia-info { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 10px; font-size: 14px; }
    .dato-evidenziato { color: #1a202c !important; font-weight: 600; }
    
    /* Forza la visibilità del testo degli input di Streamlit su sfondo chiaro */
    .stTextInput>div>div>input { background-color: #ffffff !important; border: 1px solid #cbd5e0 !important; color: #2d3748 !important; }
    label, p, span { color: #2d3748 !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGO ISTITUZIONALE ---
LOGO_URL = "https://github.com/depietromarco65/crm-casa-amici-2026/blob/main/logo-scritta.gif"
st.markdown(f'<div class="container-logo"><img src="{LOGO_URL}" class="logo-aziendale" alt="Logo"></div>', unsafe_allow_html=True)
st.title("A Casa di Amici — Dashboard Direzionale")
st.markdown("---")

# LINK SORGENTE COMPLETO
CSV_URL = "https://github.com/depietromarco65/crm-casa-amici-2026/blob/main/database_ospiti.csv"

# --- 3. RETRIEVAL E PARSING ANAGRAFICA COMPLETA ---
try:
    risposta = requests.get(CSV_URL)
    if risposta.status_code == 200:
        linee = [linea for linea in risposta.text.splitlines() if linea.strip()]
        
        if len(linee) > 1:
            lettore_csv = csv.reader(linee)
            intestazione = next(lettore_csv)  # Salta la riga dei titoli
            righe_dati = list(lettore_csv)
            
            # Pannello di ricerca reattivo in testa
            ricerca_testuale = st.text_input("✍ Cerca all'istante per nome, e-mail o note interne:", placeholder="Digita per filtrare i record...").strip().lower()
            
            conteggio_visibili = 0
            
            # Ciclo analitico completo riga per riga (dall'ultimo inserito al primo storico)
            for parti in reversed(righe_dati):
                if len(parti) < 23:
                    continue
                
                # ASSEGNAZIONE DEI 23 ELEMENTI DELLO STORICO
                id_progressivo = str(parti[0]).strip().replace(".0", "")
                data_contatto = str(parti[1]).strip()
                ora_contatto = str(parti[2]).strip()
                giorni_lead_time = str(parti[3]).strip()
                cognome = str(parti[4]).strip() if str(parti[4]).strip().lower() != "nd" else ""
                nome_grezzo = str(parti[5]).strip() if str(parti[5]).strip().lower() != "nd" else "Ospite"
                nome_ospite = f"{cognome} {nome_grezzo}".strip()
                arrivo = str(parti[6]).strip()
                partenza = str(parti[7]).strip()
                alloggio = str(parti[8]).strip() if str(parti[8]).strip().lower() != "nd" else "Da assegnare"
                ospiti_totali = str(parti[9]).strip()
                dettaglio_minori = str(parti[10]).strip()
                adulti = str(parti[11]).strip()
                bambini = str(parti[12]).strip()
                email = str(parti[13]).strip()
                portale = str(parti[14]).strip()
                caratteristiche = str(parti[15]).strip()
                tariffa = str(parti[16]).strip() if str(parti[16]).strip().lower() != "nd" else "0.00"
                extra = str(parti[17]).strip()
                tipo_tariffe = str(parti[18]).strip()
                stato_saldo = str(parti[19]).strip()
                tassa_soggiorno = str(parti[20]).strip()
                stato = str(parti[21]).strip() if str(parti[21]).strip().lower() != "nd" else "Lista d'attesa"
                note_interne = str(parti[22]).strip() if len(parti) > 22 else "Nessuna nota aggiuntiva."

                # Algoritmo filtro di ricerca globale
                testo_completo_linea = f"{nome_ospite} {portale} {alloggio} {note_interne} {email} {id_progressivo}".lower()
                if ricerca_testuale and ricerca_testuale not in testo_completo_linea:
                    continue
                    
                conteggio_visibili += 1

                # Mappatura condizionale per l'assegnazione dei colori ai badge pastello
                st_low = stato.lower()
                if "conferma" in st_low or "corso" in st_low or "arrivato" in st_low:
                    classe_colore = "badge-verde"
                    stato_visivo = "Confermata / In Corso"
                elif "attesa" in st_low or "sospeso" in st_low:
                    classe_colore = "badge-giallo"
                    stato_visivo = "Lista d'attesa"
                elif "non contattabile" in st_low:
                    classe_colore = "badge-grigio"
                    stato_visivo = "Non Contattabile"
                else:
                    classe_colore = "badge-rosso"
                    stato_visivo = "Richiesta Scaduta"

                # Renderizzazione grafica visiva della Card HTML Premium Puglia Light
                st.markdown(f"""
                <div class="card-ospite">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #edf2f7; padding-bottom: 8px;">
                        <span style="font-size: 18px; font-weight: 800; color: #1a202c !important; tracking-tight: -0.02em;">#{id_progressivo} | {nome_ospite}</span>
                        <span class="badge {classe_colore}">{stato_visivo}</span>
                    </div>
                    <div class="griglia-info">
                        <div>📅 <span style="color: #718096 !important;">Soggiorno:</span> <span class="dato-evidenziato">{arrivo} ➔ {partenza}</span></div>
                        <div>🏠 <span style="color: #718096 !important;">Unità Assegnata:</span> <span class="dato-evidenziato" style="color: #4c51bf !important;">{alloggio}</span></div>
                        <div>💶 <span style="color: #718096 !important;">Tariffa Soggiorno:</span> <span class="dato-evidenziato" style="color: #2f855a !important;">€ {tariffa}</span></div>
                        <div>🌐 <span style="color: #718096 !important;">Canale d'Origine:</span> <span class="dato-evidenziato">{portale}</span></div>
                    </div>
                    <div class="griglia-info" style="margin-top: 8px; border-top: 1px dashed #e2e8f0; padding-top: 8px; font-size: 13px;">
                        <div>👥 <span style="color: #718096 !important;">Ospiti:</span> {ospiti_totali} ({adulti} Ad. + {bambini} Bamb.) {dettaglio_minori if dettaglio_minori != "nd" else ""}</div>
                        <div>📧 <span style="color: #718096 !important;">E-mail:</span> {email}</div>
                        <div>🔍 <span style="color: #718096 !important;">Info Alloggio:</span> {caratteristiche if caratteristiche != "nd" else "Standard"}</div>
                        <div>⏱ <span style="color: #718096 !important;">Lead Time:</span> {giorni_lead_time} gg</div>
                    </div>
                    <div style="margin-top: 14px; font-size: 13px; color: #4a5568 !important; background-color: #f7fafc; padding: 10px; border-radius: 6px; border-left: 3px solid #cbd5e0;">
                        📌 <b>LOGISTICA E NOTE CRM:</b> {note_interne} <span style="float: right; font-size: 11px; color: #a0aec0 !important;">Contatto: {data_contatto} alle ore {ora_contatto}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            if conteggio_visibili == 0:
                st.warning("❌ Nessun record trovato nel database corrispondente ai parametri digitati.")
        else:
            st.info("📂 Il database ospiti risulta attualmente vuoto su GitHub.")
    else:
        st.error("🛑 Impossibile connettersi alla repository di GitHub per prelevare il file sorgente.")
except Exception as e:
    st.error(f"🛑 Errore nel caricamento del database ospiti: {e}")
