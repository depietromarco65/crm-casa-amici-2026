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
        linee = [l for l in risposta.text.splitlines() if l.strip()]
        if len(linee) > 1:
            lettore = csv.reader(linee)
            next(lettore)  # Salta intestazione
            righe = list(lettore)
            
            ricerca = st.text_input("✍ Cerca per nome, e-mail o note interne:", placeholder="Digita per filtrare i record...").strip().lower()
            conteggio = 0
            
            for p in reversed(righe):
                if len(p) < 23: continue
                
                # Estrazione pulita delle variabili posizionali (0-22)
                id_p, d_c, o_c, l_t, cognome, nome, arr, part, allog = p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8]
                o_tot, min_n, ad, bam, mail, port, char, tariff, ext, t_tar, s_sal, t_sog, stato, note = p[9], p[10], p[11], p[12], p[13], p[14], p[15], p[16], p[17], p[18], p[19], p[20], p[21], p[22]
                
                nome_completo = f"{cognome} {nome}".replace("nd ", "").strip() if f"{cognome} {nome}".strip() != "nd nd" else "Ospite"
                allog_v = allog if allog.lower() != "nd" else "Da assegnare"
                tariff_v = tariff if tariff.lower() != "nd" else "0.00"
                
                if ricerca and ricerca not in f"{nome_completo} {port} {allog_v} {note} {mail} {id_p}".lower(): continue
                conteggio += 1
                
                # Definizione accattivante del badge cromatico mediterraneo
                st_l = stato.lower()
                c_badge, v_badge = ("badge-verde", "Confermata / In Corso") if "conferma" in st_l or "corso" in st_l or "arrivato" in st_l else (("badge-giallo", "Lista d'attesa") if "attesa" in st_l or "sospeso" in st_l else (("badge-grigio", "Non Contattabile") if "non contattabile" in st_l else ("badge-rosso", "Richiesta Scaduta")))
                
                st.markdown(f"""
                <div class="card-ospite">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #edf2f7; padding-bottom: 8px;">
                        <span style="font-size: 18px; font-weight: 800; color: #1a202c !important;">#{id_p} | {nome_completo}</span>
                        <span class="badge {c_badge}">{v_badge}</span>
                    </div>
                    <div class="griglia-info">
                        <div>📅 <span style="color: #718096 !important;">Soggiorno:</span> <span class="dato-evidenziato">{arr} ➔ {part}</span></div>
                        <div>🏠 <span style="color: #718096 !important;">Unità:</span> <span class="dato-evidenziato" style="color: #4c51bf !important;">{allog_v}</span></div>
                        <div>💶 <span style="color: #718096 !important;">Tariffa:</span> <span class="dato-evidenziato" style="color: #2f855a !important;">€ {tariff_v}</span></div>
                        <div>🌐 <span style="color: #718096 !important;">Canale:</span> <span class="dato-evidenziato">{port}</span></div>
                    </div>
                    <div class="griglia-info" style="margin-top: 8px; border-top: 1px dashed #e2e8f0; padding-top: 8px; font-size: 13px;">
                        <div>👥 <span style="color: #718096 !important;">Ospiti:</span> {o_tot} ({ad} Ad. + {bam} Bamb.) {min_n if min_n != "nd" else ""}</div>
                        <div>📧 <span style="color: #718096 !important;">E-mail:</span> {mail}</div>
                        <div>🔍 <span style="color: #718096 !important;">Info Alloggio:</span> {char if char != "nd" else "Standard"}</div>
                        <div>⏱ <span style="color: #718096 !important;">Lead Time:</span> {l_t} gg</div>
                    </div>
                    <div style="margin-top: 14px; font-size: 13px; color: #4a5568 !important; background-color: #f7fafc; padding: 10px; border-radius: 6px; border-left: 3px solid #cbd5e0;">
                        📌 <b>LOGISTICA E NOTE CRM:</b> {note} <span style="float: right; font-size: 11px; color: #a0aec0 !important;">Contatto: {d_c} alle {o_c}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            if conteggio == 0: st.warning("❌ Nessun record corrispondente trovato.")
        else: st.info("📂 Il database ospiti risulta vuoto su GitHub.")
    else: st.error("🛑 Impossibile connettersi a GitHub per prelevare il CSV.")
except Exception as e:
    st.error(f"🛑 Errore nel caricamento del database: {e}")
