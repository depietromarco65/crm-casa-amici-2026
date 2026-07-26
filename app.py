import streamlit as st
import requests
import csv

# --- 1. CONFIGURAZIONE INTERFACCIA PREMIUM (DARK MODE) ---
st.set_page_config(page_title="CRM BOARD - A Casa di Amici 2026", layout="wide", page_icon="🏨")

st.markdown("""
<style>
    .stApp { background-color: #0b1329; color: #f1f5f9; }
    h1 { color: #ffffff; font-family: 'Inter', sans-serif; font-weight: 800; tracking-tight: -0.05em; text-align: center; }
    .container-logo { display: flex; justify-content: center; align-items: center; padding: 20px 0; }
    .logo-aziendale { max-width: 320px; height: auto; filter: drop-shadow(0px 4px 12px rgba(99, 102, 241, 0.2)); }
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

# --- 2. LOGO ISTITUZIONALE ---
LOGO_URL = "https://githubusercontent.com"
st.markdown(f'<div class="container-logo"><img src="{LOGO_URL}" class="logo-aziendale" alt="Logo"></div>', unsafe_allow_html=True)
st.title("A Casa di Amici — Dashboard Direzionale")
st.markdown("---")

CSV_URL = "https://githubusercontent.com"

# --- 3. RETRIEVAL E PARSING ROBUSTO DELLE RIGHE ---
try:
    risposta = requests.get(CSV_URL)
    if risposta.status_code == 200:
        # Dividiamo le righe eliminando spazi di a capo spuri
        linee = [linea for linea in risposta.text.splitlines() if linea.strip()]
        
        if len(linee) > 1:
            # Legge le righe gestendo i blocchi di testo qualificati tra virgolette
            lettore_csv = csv.reader(linee)
            intestazione = next(lettore_csv) # Salta la riga dei titoli
            
            righe_dati = list(lettore_csv)
            
            # Pannello di ricerca reattivo in testa allo schermo
            ricerca_testuale = st.text_input("✍ Cerca all'istante per nome, e-mail o note interne:", placeholder="Digita per filtrare i record...").strip().lower()
            
            conteggio_visibili = 0
            
            # Scorriamo in senso inverso per vedere le pratiche calde in cima
            for parti in reversed(righe_dati):
                if len(parti) < 22:
                    continue
                
                # Estrazione basata su indici fisici dell'array pulito (0-22)
                id_progressivo = str(parti[0]).strip().replace(".0", "")
                data_contatto = str(parti[1]).strip()
                cognome = str(parti[4]).strip() if str(parti[4]).strip().lower() != "nd" else ""
                nome_grezzo = str(parti[5]).strip() if str(parti[5]).strip().lower() != "nd" else "Ospite"
                nome_ospite = f"{cognome} {nome_grezzo}".strip()
                arrivo = str(parti[6]).strip()
                partenza = str(parti[7]).strip()
                alloggio = str(parti[8]).strip() if str(parti[8]).strip().lower() != "nd" else "Da assegnare"
                portale = str(parti[14]).strip()
                tariffa = str(parti[16]).strip() if str(parti[16]).strip().lower() != "nd" else "0.00"
                stato = str(parti[21]).strip() if str(parti[21]).strip().lower() != "nd" else "Lista d'attesa"
                note_interne = str(parti[22]).strip() if len(parti) > 22 else "Nessuna nota aggiuntiva."

                # Filtro testuale globale su tutti i campi visibili della tessera
                testo_completo_linea = f"{nome_ospite} {portale} {alloggio} {note_interne}".lower()
                if ricerca_testuale and ricerca_testuale not in testo_completo_linea:
                    continue
                    
                conteggio_visibili += 1

                # Mappatura cromatica per l'assegnazione dei badge fluo
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

                # Renderizzazione visiva della Card HTML
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

