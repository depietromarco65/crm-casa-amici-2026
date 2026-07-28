import streamlit as st
import requests
import csv
import urllib.parse
import base64

# --- 1. CONFIGURAZIONE INTERFACCIA COMPATTA E FLUIDA ---
st.set_page_config(page_title="CRM BOARD - A Casa di Amici 2026", layout="wide", page_icon="🏨")

st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; max-width: 100% !important; }
    .metric-box { background-color: #ffffff; border: 1px solid #cbd5e0; padding: 12px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .card-ospite { background-color: #ffffff !important; border: 1px solid #cbd5e0 !important; padding: 16px; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 2px 8px rgba(148, 120, 80, 0.04); }
    .badge { padding: 4px 10px; border-radius: 9999px; font-size: 11px; font-weight: 700; text-transform: uppercase; display: inline-block; }
    .badge-verde { background-color: #e6fffa !important; color: #008767 !important; border: 1px solid #b2f5ea !important; }
    .badge-giallo { background-color: #fefcbf !important; color: #b7791f !important; border: 1px solid #faf089 !important; }
    .badge-rosso { background-color: #fed7d7 !important; color: #c53030 !important; border: 1px solid #feb2b2 !important; }
    .linea-dato { display: inline-block; margin-right: 18px; font-size: 14px; white-space: nowrap !important; }
    .dato-evidenziato { color: #1a202c !important; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# Coordinate Repository per salvataggio automatico
REPO = "depietromarco65/crm-casa-amici-2026"
PATH = "database_ospiti.csv"
URL_RAW = f"https://githubusercontent.com{REPO}/main/{PATH}"
API_URL = f"https://github.com{REPO}/contents/{PATH}"

# Funzione per inviare il file CSV corretto direttamente su GitHub
def salva_csv_su_github(nuovo_contenuto_testo):
    if "GITHUB_TOKEN" not in st.secrets:
        st.error("🛑 Errore: Token GitHub mancante nei Secrets di Streamlit.")
        return False
    token = st.secrets["GITHUB_TOKEN"]
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    
    # Recuperiamo il codice "sha" del vecchio file per poterlo sovrascrivere
    res = requests.get(API_URL, headers=headers)
    if res.status_code != 200: return False
    sha = res.json()["sha"]
    
    payload = {
        "message": "Aggiornamento e rettifica record database ospiti tramite CRM Web",
        "content": base64.b64encode(nuovo_contenuto_testo.encode("utf-8")).decode("utf-8"),
        "sha": sha
    }
    commit_res = requests.put(API_URL, json=payload, headers=headers)
    return commit_res.status_code == 200

# Controllo e pulizia automatica dei refusi e-mail
def correggi_email(email_grezza):
    em = email_grezza.strip().lower()
    if not em or em == "nd": return "nd"
    sub = {"@gmal.com": "@gmail.com", "@gmaill.com": "@gmail.com", "@libero.it": "@libero.it", "@alice.it": "@alice.it", "@hotmal.com": "@hotmail.com"}
    for k, v in sub.items():
        if em.endswith(k): em = em.replace(k, v)
    return em
try:
    risposta = requests.get(URL_RAW)
    if risposta.status_code == 200:
        linee = [l for l in risposta.text.splitlines() if l.strip()]
        if len(linee) > 1:
            lettore = csv.reader(linee)
            intestazione = next(lettore)
            righe = list(lettore)
            
            # 1. CALCOLO METRICHE GENERALI
            tot_fatturato, pratiche_attive = 0.0, 0
            for p in righe:
                if len(p) < 23: continue
                st_p = p[22].strip().lower()
                if any(x in st_p for x in ["conferma", "corso", "arrivato"]):
                    pratiche_attive += 1
                    try: tot_fatturato += float(p[16].strip().replace(",", "."))
                    except ValueError: pass
            
            c_m1, c_m2 = st.columns(2)
            with c_m1: st.markdown(f'<div class="metric-box"><span style="font-size:13px; color:#718096; font-weight:600;">💰 FATTURATO CONSOLIDATO</span><br><span style="font-size:22px; font-weight:800; color:#2f855a;">€ {tot_fatturato:,.2f}</span></div>', unsafe_allow_html=True)
            with c_m2: st.markdown(f'<div class="metric-box"><span style="font-size:13px; color:#718096; font-weight:600;">📈 PRATICHE ATTIVE</span><br><span style="font-size:22px; font-weight:800; color:#4c51bf;">{pratiche_attive} CONTATTI DIRETTI</span></div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 2. PANNELLO INSERIMENTO RAPIDO / CORREZIONE RIGHE
            st.subheader("🛠️ Pannello Editor di Modifica e Correzione Righe")
            id_selezionato = st.selectbox("Seleziona l'ID del record da correggere o modificare:", [r[0] for r in reversed(righe)])
            
            # Recuperiamo l'indice esatto della riga selezionata per popolare i campi
            idx_riga = next(i for i, r in enumerate(righe) if r[0] == id_selezionato)
            riga_da_modificare = righe[idx_riga]
            
            # Espandiamo solo i campi chiave per evitare sfasamenti, applicando la correzione email
            col1, col2, col3 = st.columns(3)
            with col1:
                nuovo_cognome = st.text_input("Cognome Ospite", value=riga_da_modificare[4])
                nuovo_alloggio = st.text_input("Alloggio Assegnato", value=riga_da_modificare[8])
            with col2:
                nuovo_nome = st.text_input("Nome Ospite", value=riga_da_modificare[5])
                email_corrente = correggi_email(riga_da_modificare[13])
                nuova_email = st.text_input("Indirizzo E-mail (Auto-corretto)", value=email_corrente)
            with col3:
                nuovo_stato = st.selectbox("Stato Pratica", ["Lista d'attesa", "In corso", "Confermata", "Richiesta Scaduta", "Non Contattabile"], index=["lista d'attesa", "in corso", "confermata", "richiesta scaduta", "non contattabile"].index(riga_da_modificare[21].lower()) if riga_da_modificare[21].lower() in ["lista d'attesa", "in corso", "confermata", "richiesta scaduta", "non contattabile"] else 0)
                nuova_tariffa = st.text_input("Tariffa Alloggio (€)", value=riga_da_modificare[16])

            nuove_note = st.text_area("Note Interne e Logistica CRM", value=riga_da_modificare[22])
            
            if st.button("💾 Applica Correzioni e Salva nel Database di GitHub"):
                # Aggiorniamo i campi della riga selezionata mantenendo inalterati gli altri indici tecnici
                righe[idx_riga][4] = nuovo_cognome
                righe[idx_riga][5] = nuovo_nome
                righe[idx_riga][8] = nuovo_alloggio
                righe[idx_riga][13] = nuova_email
                righe[idx_riga][16] = nuova_tariffa
                righe[idx_riga][21] = nuovo_stato
                righe[idx_riga][22] = nuove_note
                
                # Ricostruiamo la stringa CSV completa da trasmettere alle API
                output_stringa = ",".join(intestazione) + "\n"
                for r in righe:
                    output_stringa += ",".join([f'"{x}"' if ',' in str(x) else str(x) for x in r]) + "\n"
                
                if salva_csv_su_github(output_stringa):
                    st.success(f"🟢 Record #{id_selezionato} aggiornato con successo! I dati appariranno aggiornati tra pochi secondi.")
                    st.rerun()
                else:
                    st.error("🛑 Errore durante il salvataggio su GitHub. Verifica i Secrets ed il Token.")
            
            st.markdown("---")
            st.subheader("📋 Elenco Cronologico dei Lead e delle Liste d'attesa")
            
            # 3. VISUALIZZAZIONE COMPATTA DELLE CARD FLUIDE
            for p in reversed(righe):
                if len(p) < 23: continue
                id_p, d_c, o_c, l_t, cognome, nome, arr, part, allog = p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8]
                o_tot, ad, mail_grezza, port, tariff, stato, note = p[9], p[11], p[13], p[14], p[16], p[21], p[22]
                
                mail = correggi_email(mail_grezza)
                nome_completo = f"{cognome} {nome}".replace("nd ", "").strip() if f"{cognome} {nome}".strip() != "nd nd" else "Ospite"
                allog_v = allog if allog.lower() != "nd" else "Da assegnare"
                tariff_v = tariff if tariff.lower() != "nd" else "0.00"
                
                st_l = stato.lower()
                c_badge = "badge-verde" if any(x in st_l for x in ["conferma", "corso", "arrivato"]) else ("badge-giallo" if "attesa" in st_l else "badge-rosso")
                
                st.markdown(f"""
                <div class="card-ospite">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; border-bottom: 1px solid #edf2f7; padding-bottom: 4px;">
                        <span style="font-size: 16px; font-weight: 800;">#{id_p} | {nome_completo}</span>
                        <span class="badge {c_badge}">{stato}</span>
                    </div>
                    <div style="margin-bottom: 4px;">
                        <span class="linea-dato">📅 Soggiorno: <span class="dato-evidenziato">{arr} ➔ {part}</span></span>
                        <span class="linea-dato">🏠 Unità: <span class="dato-evidenziato" style="color:#4c51bf;">{allog_v}</span></span>
                        <span class="linea-dato">💶 Tariffa: <span class="dato-evidenziato" style="color:#2f855a;">€ {tariff_v}</span></span>
                        <span class="linea-dato">🌐 Canale: <span class="dato-evidenziato">{port}</span></span>
                    </div>
                    <div style="font-size: 13px; color: #718096; margin-bottom: 6px;">
                        👥 Ospiti: {o_tot} (Ad: {ad}) | 📧 E-mail: {mail} | ⏱ Lead Time: {l_t} gg
                    </div>
                    <div style="font-size: 13px; color: #4a5568; background-color: #f7fafc; padding: 8px; border-radius: 6px; border-left: 3px solid #cbd5e0;">
                        📌 <b>NOTE INTERNE:</b> {note} <span style="float: right; font-size: 11px; color: #a0aec0;">Ricevuto: {d_c} alle {o_c}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else: st.info("📂 Database vuoto su GitHub.")
    else: st.error("🛑 Errore di connessione a GitHub.")
except Exception as e: st.error(f"🛑 Errore generico: {e}")
