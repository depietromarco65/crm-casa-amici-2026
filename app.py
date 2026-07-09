# ==============================================================================
# ===== BLOCCO 1: CARICAMENTO DATI LOCALE, CONFIGURAZIONE E LIBRERIE =====
# ==============================================================================
import datetime
import os
import re  # <--- IMPORTAZIONE FONDAMENTALE PER LO SCANNER RICORRENZE (Risolve NameError)
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
anno_corrente = datetime.datetime.now().year
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
# ===== FINE BLOCCO 1 (L'applicazione ora ha tutte le librerie caricate) =====
# ==============================================================================


# ===== BLOCCO 2: CRUSCOTTO STATISTICO KPI =====
if not df.empty:
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Richieste Totali", len(df))
    kpi2.metric("✅ Confermate", len(df[df["Stato Richiesta"].str.contains("Confermata|Arrivato", na=False, case=False)]))
    kpi3.metric("🔄 Attive", len(df[df["Stato Richiesta"].str.contains("In corso|In sospeso", na=False, case=False)]))
    kpi4.metric("📋 Lista Attesa", len(df[df["Stato Richiesta"].str.contains("Lista", na=False, case=False)]))
    st.markdown("---")

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
