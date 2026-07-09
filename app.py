# ==============================================================================
# ===== BLOCCO 1: CARICAMENTO DATI LOCALE, CONFIGURAZIONE E LIBRERIE =====
# ==============================================================================
from datetime import datetime  # <--- IMPORT MIRATO (Risolve AttributeError alla riga 70)
import os
import re
import pandas as pd
import streamlit as st

# 1. Configurazione globale della pagina dell'applicazione Streamlit
st.set_page_config(
    page_title="CRM A Casa di Amici",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Renderizzazione del logo ufficiale caricato localmente nella cartella del progetto
logo_locale = "logo-scritta.gif"
if os.path.exists(logo_locale):
    st.image(logo_locale, width=300)
else:
    st.info("Logo aziendale non rilevato localmente nella root del progetto.")

# 3. Estrazione dell'anno corrente dal server per l'automazione del titolo stagionale
anno_corrente = datetime.now().year
st.title(f"🏨 CRM A Casa di Amici - Gestione Stagionale {anno_corrente}")

# 4. Definizione del percorso locale per il database degli ospiti
csv_locale = "database_ospiti.csv"

# 5. Esecuzione del caricamento sicuro da file system locale con gestione errori
try:
    if os.path.exists(csv_locale):
        df = pd.read_csv(
            csv_locale, 
            encoding="utf-8",
            engine="python",
            quoting=3,
            on_bad_lines="skip"
        )
    else:
        df = pd.DataFrame()
        st.warning(f"File '{csv_locale}' non trovato. Assicurati di averlo caricato nella stessa cartella di app.py.")
except Exception as e:
    df = pd.DataFrame()
    st.error(f"Errore critico di lettura nel file CSV locale: {e}")

# ==============================================================================
# ===== FINE BLOCCO 1 (L'applicazione ora gestisce nativamente i datetime) =====
# ==============================================================================



# ===== BLOCCO 2: CRUSCOTTO STATISTICO KPI =====
if not df.empty:
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Richieste Totali", len(df))
    kpi2.metric("✅ Confermate", len(df[df["Stato Richiesta"].str.contains("Confermata|Arrivato", na=False, case=False)]))
    kpi3.metric("🔄 Attive", len(df[df["Stato Richiesta"].str.contains("In corso|In sospeso", na=False, case=False)]))
    kpi4.metric("📋 Lista Attesa", len(df[df["Stato Richiesta"].str.contains("Lista", na=False, case=False)]))
    st.markdown("---")

# ==============================================================================
# ===== BLOCCO 3: INTERFACCIA GRAFICA DI INSERIMENTO NUOVE RICHIESTE =====
# ==============================================================================
import os
from datetime import datetime
import pandas as pd
import streamlit as st

st.markdown("---")
st.subheader("📝 Inserimento Nuova Richiesta / Log Ospite")

# Controllo preliminare di sicurezza sullo stato del database caricato nel Blocco 1
if 'df' in locals() and not df.empty:
    # Calcolo automatico del prossimo N. Progressivo (Evita sovrascritture)
    try:
        prossimo_id = int(df.iloc[:, 0].max()) + 1
    except:
        prossimo_id = 1
    
    # Lista delle email storiche per il controllo preventivo dei duplicati
    email_esistenti = df.iloc[:, 13].dropna().astype(str).str.lower().str.strip().tolist()
else:
    prossimo_id = 1
    email_esistenti = []

# Creazione del Form Streamlit per raggruppare i campi di input
with st.form(key="form_nuova_richiesta", clear_on_submit=True):
    st.info(f"ID Progressivo Assegnato Automaticamente: **{prossimo_id}**")
    
    # Suddivisione grafica dei campi in colonne per massimizzare la scansionabilità
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cognome = st.text_input("Cognome Capofamiglia *").strip()
        nome = st.text_input("Nome Capofamiglia *").strip()
        email = st.text_input("Email Cliente *").strip()
        alloggio = st.selectbox("Alloggio Assegnato", ["nd", "Monolocale Marina", "Monolocale Margherita", "Pajara Lucy"])
        
    with col2:
        data_arrivo_dt = st.date_input("Data Arrivo", value=None)
        data_partenza_dt = st.date_input("Data Partenza", value=None)
        portale = st.selectbox("Portale di Provenienza *", ["UltimissimoMinuto", "LovelyITALIA", "Octorate Direct", "Agoda", "Prenotazione Diretta", "nd"])
        stato_prenotazione = st.selectbox("Stato Richiesta *", ["Lista d'attesa", "In corso", "Confermata", "Arrivato"])

    with col3:
        ospiti_tot = st.number_input("Numero Ospiti Totale", min_value=0, value=0, step=1)
        adulti = st.number_input("Di cui Adulti", min_value=0, value=0, step=1)
        minori = st.number_input("Di cui Minori", min_value=0, value=0, step=1)
        lead_time = st.number_input("Lead Time (Giorni)", min_value=0, value=0, step=1)

    # Campi estesi e note posizionati in righe intere a fondo maschera
    nominativo_dettaglio = st.text_input("Nominativo Ospiti Dettaglio (Nomi, Date Nascita, Documenti, Residenza)").strip()
    
    st.markdown("**💰 Dati Economici e Logistici (Impostare a 0 o lasciar vuoti se non applicabili):**")
    col_eco1, col_eco2, col_eco3, col_eco4, col_eco5, col_eco6 = st.columns(6)
    with col_eco1: acconto = st.text_input("Acconto (€)", value="0")
    with col_eco2: tariffa_tot = st.text_input("Tariffa Totale (€)", value="nd")
    with col_eco3: imposta_sogg = st.text_input("Imposta Soggiorno (€)", value="nd")
    with col_eco4: tipo_tariffa = st.selectbox("Tipo Tariffa", ["nd", "Standard", "Non Rimb."])
    with col_eco5: stato_pagamento = st.selectbox("Stato Pagamento", ["nd", "Saldato", "In attesa"])
    with col_eco6: mezzo_trasporto = st.text_input("Mezzo e Ora Arrivo", value="nd")

    note_aggiuntive = st.text_area("Note Aggiuntive e Storico Interazioni (ATTENZIONE: Non inserire virgole nel testo) *").strip()

    # Pulsante di sottomissione del form
    submit_button = st.form_submit_button(label="💾 Salva Richiesta nel Database")

# Logica di Validazione e Salvataggio dei Dati al Click
if submit_button:
    # Controllo dei campi obbligatori di struttura
    if not cognome or not nome or not email or not note_aggiuntive:
        st.error("❌ Errore: I campi Cognome, Nome, Email e Note Aggiuntive sono obbligatori per la stesura del log.")
    
    # Applicazione della Regola Rigida 1: Controllo Preventivo dei Duplicati Email
    elif email.lower() in email_esistenti:
        st.warning(f"⚠️ VIOLAZIONE REGOLA 1 (DUPLICATI): L'email '{email}' è già presente nello storico. È VIETATO generare una nuova riga di log. Cerca la riga esistente nel database e accorpa i nuovi dettagli nel campo Note Aggiuntive.")
    
    # Controllo di sicurezza sintattico per impedire la corruzione del parser CSV
    elif "," in note_aggiuntive:
        st.error("❌ Errore di Formattazione: Non puoi utilizzare la virgola ( , ) all'interno delle Note Aggiuntive perché corrompe il tracciato delle colonne del file CSV. Sostituisci tutte le virgole con punti ( . ) o trattini ( - ).")
        
    else:
        # Generazione automatica dei metadati temporali di inserimento
        ora_attuale = datetime.now().strftime("%H:%M")
        data_oggi = datetime.now().strftime("%d/%m/%Y")
        
        # Conversione e normalizzazione delle date nel formato standard DD/MM/YYYY
        data_arrivo = data_arrivo_dt.strftime("%d/%m/%Y") if data_arrivo_dt else "nd"
        data_partenza = data_partenza_dt.strftime("%d/%m/%Y") if data_partenza_dt else "nd"
        
        # Gestione automatica del valore predefinito "nd" per le stringhe vuote
        nominativo_dettaglio = nominativo_dettaglio if nominativo_dettaglio else "nd"
        alloggio = alloggio if alloggio else "nd"
        
        # Costruzione della stringa record CSV rispettando l'ordine esatto delle 23 colonne
        nuovo_record = f"{prossimo_id},{data_oggi},{ora_attuale},{lead_time},{cognome},{nome},{data_arrivo},{data_partenza},{alloggio},{ospiti_tot},{nominativo_dettaglio},{adulti},{minori},{email},{portale},{acconto},{tariffa_tot},{imposta_sogg},{tipo_tariffa},{stato_pagamento},{mezzo_trasporto},{stato_prenotazione},{note_aggiuntive}\n"
        
        # Scrittura fisica sul file system locale (database_ospiti.csv)
        csv_locale = "database_ospiti.csv"
        try:
            with open(csv_locale, "a", encoding="utf-8") as f:
                f.write(nuovo_record)
            st.success(f"✅ Riga {prossimo_id} inserita con successo! Modifiche salvate localmente nel file '{csv_locale}'.")
            st.info("Fai un refresh della pagina del browser per aggiornare i contatori della dashboard.")
        except Exception as e:
            st.error(f"Errore tecnico durante la scrittura sul file CSV: {e}")

# ==============================================================================
# ===== FINE BLOCCO 3 =====
# ==============================================================================


# ===== BLOCCO 3: ESTRATTORI RICORRENZE (REGEX) =====
def estrai_date_ricorrenze(campo_note, tipo):
    pattern = r"Cpl(\d{2}-\d{2})" if tipo == "Compleanni" else r"On(\d{2}-\d{2})"
    matches = re.findall(pattern, str(campo_note))
    return ", ".join(matches) if matches else ""

# ===== BLOCCO 4: CALCOLATORE SCADENZE =====
def verifica_scadenza_7gg(stringa_date):
    oggi, anno = datetime.now(), datetime.now().year
    alert = []
    for el in [e.strip() for e in stringa_date.split(",") if e.strip()]:
        try:
            g, m = map(int, el.split("-"))
            data_ric = datetime(anno, m, g)
            if data_ric < oggi - timedelta(days=1): data_ric = datetime(anno + 1, m, g)
            diff = (data_ric - oggi).days
            if 0 <= diff <= 7: alert.append(f"{g:02d}/{m:02d} ({diff} gg)")
        except: continue
    return alert

# ===== BLOCCO 5: SCANNER ALERT (CEO DASHBOARD) =====
st.subheader("🚨 Scanner Ricorrenze (7 Giorni)")
if not df.empty:
    avvisi_c, avvisi_o = [], []
    for _, row in df.iterrows():
        note = str(row["Note Aggiuntive"])
        titolare = f"{row['Nome Capofamiglia']} {row['Cognome Capofamiglia']}"
        for c in verifica_scadenza_7gg(estrai_date_ricorrenze(note, "Compleanni")):
            avvisi_c.append(f"🎂 {titolare}: {c}")
    c1, c2 = st.columns(2)
    c1.markdown("**🎂 Compleanni**"); [c1.info(a) for a in avvisi_c]
    c2.markdown("**🌟 Onomastici**"); st.caption("Nessun onomastico imminente.")
st.markdown("---")

# ===== BLOCCO 6: MOTORE REGEX PORTALI =====
st.header("🔄 Gestione e Modifiche")
if not df.empty:
    opzioni = df.apply(lambda r: f"{r['N. Progressivo']} - {r['Cognome Capofamiglia']}", axis=1).tolist()
    selezione = st.selectbox("Seleziona ospite:", opzioni)
    idx_scelto = opzioni.index(selezione)
    riga_corrente = df.iloc[idx_scelto]
    st.session_state["riga_attiva_id"] = idx_scelto
else:
    riga_corrente = None

# ===== BLOCCO 7: SCHEDA DI MODIFICA E SALVATAGGIO =====
if riga_corrente is not None:
    with st.form("form_modifica"):
        c1, c2 = st.columns(2)
        m_cognome = c1.text_input("Cognome", value=str(riga_corrente["Cognome Capofamiglia"]))
        m_nome = c2.text_input("Nome", value=str(riga_corrente["Nome Capofamiglia"]))
        m_stato = st.selectbox("Stato", ["Confermata", "Arrivato", "In corso", "Lista d'attesa", "Scaduta"], index=2)
        m_note = st.text_area("Note (le virgole verranno rimosse automaticamente)", value=str(riga_corrente["Note Aggiuntive"]))
        salva = st.form_submit_button("💾 Salva Modifiche")

    if salva:
        df.at[riga_corrente.name, "Cognome Capofamiglia"] = m_cognome
        df.at[riga_corrente.name, "Nome Capofamiglia"] = m_nome
        df.at[riga_corrente.name, "Stato Richiesta"] = m_stato
        df.at[riga_corrente.name, "Note Aggiuntive"] = m_note.replace(",", " ")
        df.to_csv("database_ospiti.csv", index=False)
        st.success("Salvato con successo!")
        time.sleep(0.5)
        st.rerun()

# ===== BLOCCO 8: MODULO COMUNICAZIONE =====
st.markdown("### 📞 Modulo Comunicazione")
messaggio = st.text_area("Testo:", "Ciao, ecco l'aggiornamento...")
if riga_corrente is not None:
    phone_match = re.search(r'Tel\s*(\d+)', str(riga_corrente["Note Aggiuntive"]))
    if phone_match:
        st.markdown(f"[💬 Invia su WhatsApp](https://wa.me{phone_match.group(1)}?text={urllib.parse.quote(messaggio)})")
