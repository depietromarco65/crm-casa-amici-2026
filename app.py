import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURAZIONE INTERFACCIA PREMIUM (DARK MODE) ---
st.set_page_config(page_title="CRM BOARD - A Casa di Amici", layout="wide", page_icon="🏨")

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
    }
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

# --- 2. RETRIEVAL STRUTTURATO E PARSING ROBUSTO DELLE LINEE ---
try:
    risposta = requests.get(CSV_URL)
    if risposta.status_code == 200:
        linee = risposta.text.splitlines()
        
        if len(linee) > 1:
            # Isoliamo le righe dei dati scartando l'intestazione iniziale di GitHub
            righe_dati = linee[1:]
            
            # Pannello di ricerca reattivo in testa allo schermo
            ricerca_testuale = st.text_input("✍ Cerca all'istante per nome, e-mail o note interne:", placeholder="Digita per filtrare i record...").strip().lower()
            
            conteggio_visibili = 0
            
            # Processiamo il foglio in senso inverso per spingere i nuovi flussi in alto
            for riga_grezza in reversed(righe_dati):
                if not riga_grezza.strip():
                    continue
                    
                # Parsing posizionale immune: separiamo solo le prime 22 colonne stabili
                parti = riga_grezza.split(",", 22)
                if len(parti) < 22:
                    continue
                    
                # Mappatura sicura legata alla reale struttura geometrica del file CSV
                id_progressivo = parti[0].strip()
                data_contatto = parti[1].strip()
                cognome = parti[4].strip() if parti[4].strip() != "nd" else ""
                nome_grezzo = parti[5].strip() if parti[5].strip() != "nd" else "Ospite"
                nome_ospite = f"{cognome} {nome_grezzo}".strip()
                arrivo = parti[6].strip()
                partenza = parti[7].strip()
                alloggio = parti[8].strip() if parti[8].strip() != "nd" else "Da assegnare"
                portale = parti[14].strip()
                tariffa = parti[16].strip() if parti[16].strip() != "nd" else "0.00"
                stato = parti[21].strip() if parti[21].strip() != "nd" else "Lista d'attesa"
                
                # Se la nota finale contiene ulteriori virgole, split(..., 22) le mantiene intatte
                note_interne = parti[22].strip() if len(parti) > 22 else "Nessuna nota aggiuntiva."
                note_interne = note_interne.strip('"') # Rimuove eventuali virgolette di protezione

                # Applicazione immediata dei filtri di ricerca sul testo pulito
                testo_linea_completa = f"{nome_ospite} {parti[13]} {note_interne}".lower()
                if ricerca_testuale and ricerca_testuale not in testo_linea_completa:
                    continue
                    
                conteggio_visibili += 1

                # Classificazione cromatica degli stati ed estensione delle stringhe visive
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

                # --- 3. INIEZIONE FRONTEND DELL'INTERFACCIA IN HIGH CONTRAST ---
                st.markdown(f"""
                <div class="card-ospite">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #334155; padding-bottom: 8px;">
                        <span style="font-size: 18px; font-weight: 800; color: #ffffff; tracking-tight: -0.02em;">#{id_progressivo} | {nome_ospite}</span>
                        <span class="badge {classe_colore}">{stato_visivo}</span>
                    </div>
                    <div class="griglia-info">
                        <div>📅 <span style="color: #94a3b8;">Soggiorno:</span> <span class="dato-evidenziato">{arrivo} ➔ {partenza}</span></div>
                        <div>🏠 <span style="color: #94a3b8;">Unità Assegnata:</span> <span class="dato-evidenziato" style="color: #6366f1;">{alloggio}</span></div>
                        <div>💶 <span style="color: #94a3b8;">Tariffa Soggiorno:</span> <span class="dato-evidenziato" style="color: #10b981;">€ {tariffa}</span></div>
                        <div>🌐 <span style="color: #94a3b8;">Canale d'Origine:</span> <span class="dato-evidenziato">{portale}</span></div>
                    </div>
                    <div style="margin-top: 14px; font-size: 13px; color: #94a3b8; background-color: rgba(15, 23, 42, 0.4); padding: 10px; border-radius: 6px; border-left: 3px solid #475569;">
                        📌 <b>LOGISTICA E NOTE CRM:</b> {note_interne} <span style="float: right; font-size: 11px; color: #64748b;">Contatto: {data_contatto}</span>
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
    st.error(f"🛑 Errore nel caricamento del database ospiti. Assicurati che il file database_ospiti.csv su GitHub sia formattato correttamente.")
