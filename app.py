# ===== BLOCCO 1: CARICAMENTO DATI =====
import streamlit as st
import pandas as pd
import re
import urllib.parse
import time
from datetime import datetime, timedelta

st.set_page_config(
    page_title="CRM A Casa di Amici 2026",
    page_icon="🏠",
    layout="wide"
)

@st.cache_data(ttl=60)
def carica_database():
    try:
        # skiprows=[1] salta la riga fittizia descrittiva allineando le colonne
        df_raw = pd.read_csv("database_ospiti.csv", skiprows=[1])
        return df_raw
    except Exception as e:
        st.error(f"Errore nel caricamento del database CSV: {e}")
        return pd.DataFrame()

df = carica_database()

st.title("🏨 CRM A Casa di Amici - Gestione Stagionale 2026")
st.markdown("---")

# ===== BLOCCO 2: CRUSCOTTO STATISTICO KPI =====
if not df.empty:
    tot_contatti = len(df)
    confermati = len(df[df["Esit o"].str.contains("Confermata", na=False)])
    in_corso = len(df[df["Esit o"].str.contains("In corso|In sospeso|Pre-approvata", na=False)])
    lista_attesa = len(df[df["Esit o"].str.contains("Lista attesa", na=False)])
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Richieste Totali Gestite", tot_contatti)
    with kpi2:
        st.metric("Prenotazioni ✅ Confermate", confermati)
    with kpi3:
        st.metric("Trattative 🔄 Attive", in_corso)
    with kpi4:
        st.metric("Clienti in 📋 Lista Attesa", lista_attesa)
    st.markdown("---")

# ===== BLOCCO 3: ESTRATTORI RICORRENZE =====
def estrai_date_ricorrenze(campo_note, tag):
    """Estrae le stringhe formattate inserite all'interno delle parentesi quadre del campo Note."""
    pattern = rf"\[{tag}:\s*([^\]]+)\]"
    match = re.search(pattern, str(campo_note))
    return match.group(1) if match else ""

# ===== BLOCCO 4: CALCOLATORE SCADENZE =====
def verifica_scadenza_ricorrenza(stringa_date):
    """Verifica se una ricorrenza cade nei successivi 7 giorni rispetto alla data attuale."""
    oggi = datetime.now()
    anno_corrente = oggi.year
    alert_trovati = []
    
    elementi = [e.strip() for e in stringa_date.split(",") if e.strip()]
    for el in elementi:
        try:
            if " - " in el:
                data_str, nome = el.split(" - ", 1)
                giorno, mese = map(int, data_str.split("/"))
                data_ricorrenza = datetime(anno_corrente, mese, giorno)
                
                if data_ricorrenza < oggi - timedelta(days=1):
                    data_ricorrenza = datetime(anno_corrente + 1, mese, giorno)
                    
                differenza = (data_ricorrenza - oggi).days
                if 0 <= differenza <= 7:
                    alert_trovati.append({"nome": nome, "giorni": differenza, "data": data_str})
        except:
            continue
    return alert_trovati
# ===== BLOCCO 5: SCANNER INTERFACCIA ALERT (CORRETTO) =====
st.subheader("🚨 Scanner Ricorrenze e Compleanni Imminenti (CEO Dashboard)")

avvisi_compleanni = []
avvisi_onomastici = []

if not df.empty:
    for idx, row in df.iterrows():
        # Correzione: Gestione valori nulli (NaN) nel campo note
        note_campo = str(row["Note aggiuntiv e"]) if pd.notna(row["Note aggiuntiv e"]) else ""
        titolare = f"{row['Nom e']} {row['Cognom e']}"
        
        stringa_comp = estrai_date_ricorrenze(note_campo, "Compleanni")
        if stringa_comp:
            for c in verifica_scadenza_ricorrenza(stringa_comp):
                avvisi_compleanni.append(f"🎂 **{c['nome']}** (Gruppo: {titolare}) il {c['data']}!")
                
        stringa_ono = estrai_date_ricorrenze(note_campo, "Onomastici")
        if stringa_ono:
            for o in verifica_scadenza_ricorrenza(stringa_ono):
                avvisi_onomastici.append(f"🌟 **{o['nome']}** (Gruppo: {titolare}) il {o['data']}!")

col_comp, col_ono = st.columns(2)
with col_comp:
    st.markdown("**🎂 Compleanni in arrivo (7 Giorni):**")
    if avvisi_compleanni:
        for a in avvisi_compleanni: st.info(a)
    else:
        st.caption("Nessun compleanno nei prossimi 7 giorni.")
        
with col_ono:
    st.markdown("**🌟 Onomastici in arrivo (7 Giorni):**")
    if avvisi_onomastici:
        for a in avvisi_onomastici: st.success(a)
    else:
        st.caption("Nessun onomastico nei prossimi 7 giorni.")

st.markdown("---")

# ===== BLOCCO 6: MOTORE REGEX PORTALI (CORRETTO) =====
st.header("🔄 Gestione Richieste, Modifiche e Comunicazioni")

if not df.empty:
    opzioni_ricerca = df.apply(
        lambda r: f"Reg. {r['numero progressiv o']} - {r['Cognom e']} {r['Nom e']} ({r['data presunta di Arriv o']})", 
        axis=1
    ).tolist()
    
    # Correzione Streamlit: passata la lista di pesi [1, 1] per la creazione delle colonne
    col_sel, col_reg = st.columns([1, 1])
    with col_sel:
        selezione = st.selectbox("Seleziona una scheda ospite da gestire:", opzioni_ricerca)
        idx_riga = opzioni_ricerca.index(selezione)
        riga_selezionata = df.iloc[idx_riga]
    with col_reg:
        st.markdown("<br>", unsafe_allow_html=True)
        abilita_regex = st.checkbox("⚡ Attiva Incolla Rapido (Regex)", value=False)

    if abilita_regex:
        st.subheader("📋 Incolla Testo Copiato dal Portale")
        testo_portale = st.text_area(
            "Incolla qui il testo (Booking, Airbnb, Vrbo, Lovely, UltMin, Agoda, Idealista):",
            height=120
        )
        if testo_portale:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', testo_portale)
            date_match = re.findall(r'\b\d{2}/\d{2}/\d{4}\b', testo_portale)
            ospiti_match = re.search(r'(\d+)\s*(?:Ospit|ospit|pax|Persone|persone)', testo_portale)
            adulti_match = re.search(r'(\d+)\s*(?:Adult|adult)', testo_portale)
            minori_match = re.search(r'(\d+)\s*(?:Bambin|bambin|Minor|minor)', testo_portale)
            
            st.info("🤖 **Dati rilevati automaticamente in sessione temporary:**")
            st.session_state["rx_em"] = email_match.group(0) if email_match else str(riga_selezionata["Emai l"])
            st.session_state["rx_arr"] = date_match[0] if len(date_match) > 0 else str(riga_selezionata["data presunta di Arriv o"])
            st.session_state["rx_part"] = date_match[1] if len(date_match) > 1 else str(riga_selezionata["data presunta di Partenz a"])
            st.session_state["rx_tot"] = ospiti_match.group(1) if ospiti_match else str(riga_selezionata["Numero Ospit i"])
            st.session_state["rx_ad"] = adulti_match.group(1) if adulti_match else str(riga_selezionata["adult i"])
            st.session_state["rx_min"] = minori_match.group(1) if minori_match else str(riga_selezionata["minor i"])
            st.caption("I campi sottostanti sono stati precompilati con i dati estratti!")
    else:
        # Prevenzione crash: pulizia session_state quando l'Incolla Rapido viene disattivato
        for key in ["rx_em", "rx_arr", "rx_part", "rx_tot", "rx_ad", "rx_min"]:
            if key in st.session_state:
                del st.session_state[key]
# ===== BLOCCO 7: SCHEDA DI MODIFICA (CORRETTO) =====
st.markdown("### 📝 Scheda Anagrafica e Stato Prenotazione")

note_intere = str(riga_selezionata["Note aggiuntiv e"]).strip() if pd.notna(riga_selezionata["Note aggiuntiv e"]) else ""
if note_intere == "nan":
    note_intere = ""

compleanni_correnti = ""
onomastici_correnti = ""
note_pulite = note_intere

if "[Compleanni:" in note_intere:
    parts = note_intere.split("[Compleanni:")
    note_pulite = parts[0].strip()
    sub_parts = parts[1].split("[Onomastici:")
    compleanni_correnti = sub_parts[0].replace("]", "").strip()
    if len(sub_parts) > 1:
        onomastici_correnti = sub_parts[1].replace("]", "").strip()
elif "[Onomastici:" in note_intere:
    parts = note_intere.split("[Onomastici:")
    note_pulite = parts[0].strip()
    onomastici_correnti = parts[1].replace("]", "").strip()

with st.form("modulo_modifica_ospite"):
    c1, c2, c3 = st.columns(3)
    with c1:
        mod_cognome = st.text_input("Cognome", value=str(riga_selezionata["Cognom e"]))
        
        # Correzione: Estrazione sicura della stringa dal session_state per la data di arrivo
        val_arr = st.session_state.get("rx_arr")
        if isinstance(val_arr, list) and len(val_arr) > 0:
            val_arr = val_arr[0]
        elif not val_arr:
            val_arr = str(riga_selezionata["data presunta di Arriv o"])
        mod_arrivo = st.text_input("Data di Arrivo (GG/MM/AAAA)", value=str(val_arr))
        
        mod_adulti = st.text_input("Numero Adulti", value=str(st.session_state.get("rx_ad", riga_selezionata["adult i"])))
        
    with c2:
        mod_nome = st.text_input("Nome", value=str(riga_selezionata["Nom e"]))
        
        # Correzione: Estrazione sicura della stringa dal session_state per la data di partenza
        val_part = st.session_state.get("rx_part")
        if isinstance(val_part, list):
            val_part = val_part[1] if len(val_part) > 1 else (val_part[0] if len(val_part) > 0 else str(riga_selezionata["data presunta di Partenz a"]))
        elif not val_part:
            val_part = str(riga_selezionata["data presunta di Partenz a"])
        mod_partenza = st.text_input("Data di Partenza (GG/MM/AAAA)", value=str(val_part))
        
        mod_minori = st.text_input("Numero Minori", value=str(st.session_state.get("rx_min", riga_selezionata["minor i"])))
        
    with c3:
        mod_email = st.text_input("Email", value=str(st.session_state.get("rx_em", riga_selezionata["Emai l"])))
        mod_ospiti_tot = st.text_input("Totale Componenti Gruppo", value=str(st.session_state.get("rx_tot", riga_selezionata["Numero Ospit i"])))
        
        stato_attuale = str(riga_selezionata["Esit o"]).strip()
        lista_stati = ["🔄 In corso", "🔄 In sospeso", "🔄 Pre-approvata", "✅ Confermata", "📋 Lista attesa", "❌ Non disponibile", "❌ Cancellata", "❌ Annullata"]
        idx_stato = lista_stati.index(stato_attuale) if stato_attuale in lista_stati else 0
        mod_esito = st.selectbox("Stato Pratica (Esito)", lista_stati, index=idx_stato)

    c4, c5 = st.columns(2)
    with c4:
        mod_portale = st.text_input("Portale di Provenienza", value=str(riga_selezionata["Portale di provenienz a"]))
    with c5:
        mod_cane = st.text_input("Cane (Razza / Taglia / Nome)", value=str(riga_selezionata["Cane (Razza/Taglia)"]))

    st.markdown("#### 🎂 Gestione Ricorrenze Interne")
    col_ann1, col_ann2 = st.columns(2)
    with col_ann1:
        mod_compleanni = st.text_input("Compleanni del Gruppo (Es: 14/03 - Luigi, 22/07 - Anna)", value=compleanni_correnti)
    with col_ann2:
        mod_onomastici = st.text_input("Onomastici del Gruppo (Es: 21/06 - Luigi, 26/07 - Anna)", value=onomastici_correnti)

    mod_note_correnti = st.text_area("Note e Trattative Commerciali Extra", value=note_pulite, height=80)
    salva_premuto = st.form_submit_button("💾 Salva Modifiche Scheda Corrente", type="primary")

# ===== BLOCCO 8: MOTORE SCRITTURA CSV (CORRETTO) =====
if salva_premuto:
    nota_unificata = mod_note_correnti.strip()
    if mod_compleanni.strip():
        nota_unificata += f" [Compleanni: {mod_compleanni.strip()}]"
    if mod_onomastici.strip():
        nota_unificata += f" [Onomastici: {mod_onomastici.strip()}]"
        
    # Identificazione univoca e sicura dell'indice originale della riga
    idx_reale = riga_selezionata.name
        
    df.at[idx_reale, "Cognom e"] = mod_cognome
    df.at[idx_reale, "Nom e"] = mod_nome
    df.at[idx_reale, "Emai l"] = mod_email
    df.at[idx_reale, "data presunta di Arriv o"] = mod_arrivo
    df.at[idx_reale, "data presunta di Partenz a"] = mod_partenza
    df.at[idx_reale, "Numero Ospit i"] = mod_ospiti_tot
    df.at[idx_reale, "adult i"] = mod_adulti
    df.at[idx_reale, "minor i"] = mod_minori
    df.at[idx_reale, "Portale di provenienz a"] = mod_portale
    df.at[idx_reale, "Cane (Razza/Taglia)"] = mod_cane
    df.at[idx_reale, "Esit o"] = mod_esito
    df.at[idx_reale, "Note aggiuntiv e"] = nota_unificata
    
    # Salva il file su disco mantenendo la struttura allineata
    df.to_csv("database_ospiti.csv", index=False)
    
    # Svuota la cache di Streamlit per forzare la lettura dei nuovi dati aggiornati
    st.cache_data.clear()
    
    st.success(f"✅ Scheda progressivo N. {riga_selezionata['numero progressiv o']} salvata correttamente!")
    time.sleep(1)
    st.rerun()

# ===== BLOCCO 9: MODULO COMUNICAZIONE (CORRETTO) =====
st.markdown("### 📞 Modulo di Comunicazione e Fidelizzazione")

scelta_modello = st.radio(
    "Seleziona il testo commerciale da generare:",
    ["Nessuno", "Modello Tutto Esaurito (15% Sconto)", "Fidelizzazione Invernale: Buon Compleanno (10% Sconto)", "Fidelizzazione Mattutina: Buon Onomastico"]
)

testo_finale_comunicazione = ""
oggetto_email = ""
nome_titolare = str(mod_nome) if mod_nome and mod_nome != "-" else "Gentile Ospite"
cin_obbligatorio = "CIN: IT075066C200054604"

if scelta_modello == "Modello Tutto Esaurito (15% Sconto)":
    oggetto_email = "Aggiornamento richiesta di soggiorno - A Casa di Amici Salento"
    testo_finale_comunicazione = (
        f"Ciao {nome_titolare}, ti ringraziamo molto per aver pensato alla nostra struttura per le tue vacanze! "
        f"Purtroppo nel periodo richiesto siamo al completo su tutti i nostri alloggi a Torre Pali. "
        f"Ci dispiace molto non poterti ospitare questa volta. Per farci perdonare, abbiamo il piacere di offrirti "
        f"un Voucher Sconto del 15% valido per una tua futura prenotazione diretta con noi da riscattare comodamente via WhatsApp. "
        f"Ti inseriamo inoltre nella nostra lista d'attesa prioritaria in caso di cancellazioni dell'ultimo minuto. "
        f"Ti invitiamo a scoprire i dettagli dei nostri appartamenti sul portale ufficiale https://acasadamici.it\n\n"
        f"Un caro saluto da Marco De Pietro.\n{cin_obbligatorio}"
    )
    
elif scelta_modello == "Fidelizzazione Invernale: Buon Compleanno (10% Sconto)":
    oggetto_email = "Buon compleanno da A Casa di Amici! 🎂 Il Salento ti aspetta..."
    testo_finale_comunicazione = (
        f"Ciao {nome_titolare}, tantissimi auguri di buon compleanno da me e da tutta la famiglia di A Casa di Amici! 🎉 "
        f"Speriamo che questo giorno speciale ti porti tanta felicità. Per festeggiare insieme a te, abbiamo pensato di farti "
        f"un piccolo regalo: un codice sconto esclusivo del 10% valido per tornare a trovarci a Torre Pali nel 2027, "
        f"estendibile anche a tutti gli ospiti che hanno soggiornato con te. Puoi bloccare la tua struttura preferita "
        f"semplicemente rispondendo a questa comunicazione o su WhatsApp, senza alcun acconto iniziale tramite la nostra Formula Fiducia! "
        f"Un grande abbraccio e ancora buon compleanno!\n\nMarco De Pietro - https://acasadamici.it\n{cin_obbligatorio}"
    )
    
elif scelta_modello == "Fidelizzazione Mattutina: Buon Onomastico":
    oggetto_email = "Oggi è la tua festa! Buon onomastico da A Casa di Amici 🌟"
    testo_finale_comunicazione = (
        f"Ciao {nome_titolare}, oggi si festeggia il tuo nome e noi non potevamo dimenticarcelo! 🌟 "
        f"Tanti auguri di buon onomastico da Marco di A Casa di Amici. Speriamo di strapparti un sorriso e di portarti con il pensiero "
        f"un po' del calore, del mare e del sole del nostro Salento. Un caro saluto a te e a tutto il vostro fantastico gruppo di vacanze, "
        f"vi aspettiamo a Torre Pali!\n\nhttps://acasadamici.it\n{cin_obbligatorio}"
    )

if scelta_modello != "Nessuno":
    st.markdown("**Anteprima testo generato:**")
    st.text_area("Contenuto del messaggio:", value=testo_finale_comunicazione, height=150)
    
    testo_url_encoded = urllib.parse.quote(testo_finale_comunicazione)
    
    # Recupero dinamico del numero di telefono dalle note se presente (es. Tel: 333123456)
    note_intere_str = str(riga_selezionata["Note aggiuntiv e"])
    phone_match = re.search(r'(?:Telefono|Tel):\s*\+?(\d+)', note_intere_str)
    whatsapp_number = phone_match.group(1) if phone_match else ""
    
    # Correzione del link di reindirizzamento delle API di WhatsApp
    link_whatsapp = f"https://wa.me{whatsapp_number}?text={testo_url_encoded}"
    link_mail = f"mailto:{mod_email}?subject={urllib.parse.quote(oggetto_email)}&body={testo_url_encoded}"
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.markdown(
            f'<a href="{link_whatsapp}" target="_blank" style="text-decoration:none;">'
            f'<div style="background-color:#25D366;color:white;padding:10px;border-radius:5px;text-align:center;font-weight:bold;cursor:pointer;">'
            f'💬 Apri e Invia su WhatsApp'
            f'</div></a>', 
            unsafe_allow_html=True
        )
    with col_btn2:
        st.markdown(
            f'<a href="{link_mail}" target="_blank" style="text-decoration:none;">'
            f'<div style="background-color:#0078D4;color:white;padding:10px;border-radius:5px;text-align:center;font-weight:bold;cursor:pointer;">'
            f'✉️ Spedisci via Email Ufficiale'
            f'</div></a>', 
            unsafe_allow_html=True
        )
# Chiusura corretta dell'if principale "if not df.empty:" iniziato nei blocchi precedenti
else:
    st.warning("⚠️ Database vuoto o file non trovato.")
