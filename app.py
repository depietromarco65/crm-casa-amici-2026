import streamlit as st
import requests
import csv

# --- 1. CONFIGURAZIONE TEMA E INTERFACCIA ---
st.set_page_config(page_title="CRM BOARD - A Casa di Amici 2026", layout="wide", page_icon="🏨")

st.markdown("""
<style>
    html, body, .stApp, .main, [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"], [data-testid="stHeader"] {
        background-color: #fcfbf7 !important; background-attachment: fixed !important; min-height: 100% !important; height: auto !important; color: #2d3748 !important;
    }
    h1, h2, h3, label, p, span, div { color: #2d3748 !important; }
    .metric-box { background-color: #ffffff; border: 1px solid #e2e8f0; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    .card-ospite { background-color: #ffffff !important; border: 1px solid #e2e8f0 !important; padding: 22px; border-radius: 14px; margin-bottom: 16px; box-shadow: 0 4px 15px -3px rgba(148, 120, 80, 0.08); }
    .badge { padding: 5px 12px; border-radius: 9999px; font-size: 11px; font-weight: 700; text-transform: uppercase; display: inline-block; }
    .badge-verde { background-color: #e6fffa !important; color: #008767 !important; border: 1px solid #b2f5ea !important; }
    .badge-giallo { background-color: #fefcbf !important; color: #b7791f !important; border: 1px solid #faf089 !important; }
    .badge-rosso { background-color: #fed7d7 !important; color: #c53030 !important; border: 1px solid #feb2b2 !important; }
    .badge-grigio { background-color: #edf2f7 !important; color: #4a5568 !important; border: 1px solid #e2e8f0 !important; }
    .griglia-info { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 10px; font-size: 14px; }
    .dato-evidenziato { color: #1a202c !important; font-weight: 600; }
    .container-logo { display: flex; justify-content: center; align-items: center; padding: 15px 0; }
    .logo-aziendale { max-width: 280px; height: auto; }
    .stTextInput>div>div>input { background-color: #ffffff !important; border: 1px solid #cbd5e0 !important; color: #2d3748 !important; }
</style>
""", unsafe_allow_html=True)

# Logo e Titolo
st.markdown('<div class="container-logo"><img src="https://github.com/depietromarco65/crm-casa-amici-2026/blob/main/logo-scritta.gif" class="logo-aziendale" alt="Logo"></div>', unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>A Casa di Amici — Dashboard Direzionale</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- 2. RECUPERO DATI E SOLIDO PARSING GEOMETRICO A 23 CAMPI ---
CSV_URL = "https://github.com/depietromarco65/crm-casa-amici-2026/blob/main/database_ospiti.csv"


try:
    risposta = requests.get(CSV_URL)
    if risposta.status_code == 200:
        linee = [l for l in risposta.text.splitlines() if l.strip()]
        if len(linee) > 1:
            lettore = csv.reader(linee)
            next(lettore)  # Salta intestazione
            righe = list(lettore)
            
            # --- CALCOLO METRICHE AZIENDALI IN TEMPO REALE ---
            totale_fatturato = 0.0
            pratiche_attive = 0
            
            for p in righe:
                if len(p) < 23: continue
                stato_p = p[21].strip().lower()
                if "conferma" in stato_p or "corso" in stato_p or "arrivato" in stato_p:
                    pratiche_attive += 1
                    try:
                        valore_tariffa = p[16].strip().replace(",", ".")
                        totale_fatturato += float(valore_tariffa)
                    except ValueError:
                        pass
            
            # Rendering Blocchi Indicatori Contabili
            c_m1, c_m2 = st.columns(2)
            with c_m1:
                st.markdown(f'<div class="metric-box"><span style="font-size:14px; color:#718096; font-weight:600;">💰 FATTURATO CONSOLIDATO (PREVENTIVI ATTIVI / CONFERMATI)</span><br><span style="font-size:28px; font-weight:800; color:#2f855a;">€ {totale_fatturato:,.2f}</span></div>', unsafe_allow_html=True)
            with c_m2:
                st.markdown(f'<div class="metric-box"><span style="font-size:14px; color:#718096; font-weight:600;">📈 PRATICHE ATTIVE IN CORSO</span><br><span style="font-size:28px; font-weight:800; color:#4c51bf;">{pratiche_attive} CONTATTI VIA WEB</span></div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            ricerca = st.text_input("✍ Cerca per nome, e-mail o note interne:", placeholder="Digita per filtrare i record...").strip().lower()
            conteggio = 0
            
            for p in reversed(righe):
                if len(p) < 23: continue
                
                # Mappatura rigorosa geometrica (0-22)
                id_p = p[0].strip()
                d_c = p[1].strip()
                o_c = p[2].strip()
                l_t = p[3].strip()
                cognome = p[4].strip() if p[4].strip().lower() != "nd" else ""
                nome = p[5].strip() if p[5].strip().lower() != "nd" else ""
                arr = p[6].strip()
                part = p[7].strip()
                allog = p[8].strip()
                o_tot = p[9].strip()
                min_n = p[10].strip()
                ad = p[11].strip()
                bam = p[12].strip()
                mail = p[13].strip()
                port = p[14].strip()
                char = p[15].strip()
                tariff = p[16].strip()
                ext = p[17].strip()
                t_tar = p[18].strip()
                s_sal = p[19].strip()
                t_sog = p[20].strip()
                stato = p[21].strip()
                note = p[22].strip()
                
                nome_completo = f"{cognome} {nome}".strip() if f"{cognome} {nome}".strip() != "" else "Ospite"
                allog_v = allog if allog.lower() != "nd" else "Da assegnare"
                tariff_v = tariff if tariff.lower() != "nd" else "0.00"
                
                if ricerca and ricerca not in f"{nome_completo} {port} {allog_v} {note} {mail} {id_p}".lower(): 
                    continue
                conteggio += 1
                
                st_l = stato.lower()
                if "conferma" in st_l or "corso" in st_l or "arrivato" in st_l:
                    c_badge, v_badge = "badge-verde", "Confermata / In Corso"
                elif "attesa" in st_l or "sospeso" in st_l:
                    c_badge, v_badge = "badge-giallo", "Lista d'attesa"
                elif "non contattabile" in st_l:
                    c_badge, v_badge = "badge-grigio", "Non Contattabile"
                else:
                    c_badge, v_badge = "badge-rosso", "Richiesta Scaduta"
                
                st.markdown(f"""
                <div class="card-ospite">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #edf2f7; padding-bottom: 8px;">
                        <span style="font-size: 18px; font-weight: 800;">#{id_p} | {nome_completo}</span>
                        <span class="badge {c_badge}">{v_badge}</span>
                    </div>
                    <div class="griglia-info">
                        <div>📅 <span style="color: #718096;">Soggiorno:</span> <span class="dato-evidenziato">{arr} ➔ {part}</span></div>
                        <div>🏠 <span style="color: #718096;">Unità:</span> <span class="dato-evidenziato" style="color: #4c51bf;">{allog_v}</span></div>
                        <div>💶 <span style="color: #718096;">Tariffa:</span> <span class="dato-evidenziato" style="color: #2f855a;">€ {tariff_v}</span></div>
                        <div>🌐 <span style="color: #718096;">Canale:</span> <span class="dato-evidenziato">{port}</span></div>
                    </div>
                    <div class="griglia-info" style="margin-top: 8px; border-top: 1px dashed #e2e8f0; padding-top: 8px; font-size: 13px;">
                        <div>👥 <span style="color: #718096;">Ospiti:</span> {o_tot} ({ad} Ad. + {bam} Bamb.) {min_n if min_n != "nd" else ""}</div>
                        <div>📧 <span style="color: #718096;">E-mail:</span> {mail}</div>
                        <div>🔍 <span style="color: #718096;">Info Alloggio:</span> {char if char != "nd" else "Standard"}</div>
                        <div>⏱ <span style="color: #718096;">Lead Time:</span> {l_t} gg</div>
                    </div>
                    <div style="margin-top: 14px; font-size: 13px; color: #4a5568; background-color: #f7fafc; padding: 10px; border-radius: 6px; border-left: 3px solid #cbd5e0;">
                        📌 <b>LOGISTICA E NOTE CRM:</b> {note} <span style="float: right; font-size: 11px; color: #a0aec0;">Contatto: {d_c} alle {o_c}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            if conteggio == 0: 
                st.warning("❌ Nessun record corrispondente trovato.")
        else: 
            st.info("📂 Il database ospiti risulta vuoto su GitHub.")
    else: 
        st.error("🛑 Impossibile connettersi a GitHub per prelevare il CSV.")
except Exception as e:
    st.error(f"🛑 Errore nel caricamento del database: {e}")
