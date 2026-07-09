# ==============================================================================
# ===== BLOCCO 1: CARICAMENTO DATI LOCALE, CONFIGURAZIONE E LIBRERIE =====
# ==============================================================================
from datetime import datetime
import os
import re                      # Libreria fondamentale per lo Scanner Ricorrenze
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
# ===== FINE BLOCCO 1 =====
# ==============================================================================

# ==============================================================================
# ===== BLOCCO 2: CRUSCOTTO STATISTICO KPI (VECCHIO CODICE ORIGINALE) =====
# ==============================================================================
# NOTA PER L'OPERATORE: Incolla qui sotto la tua logica originale che genera
# i contatori numerici a schermo (Richieste totali, confermate, attive, ecc.)
# basati sull'elaborazione delle righe del DataFrame 'df'.


# ==============================================================================
# ===== FINE BLOCCO 2 =====
# ==============================================================================

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
        alloggio = st.selectbox("Alloggio Assegnato", ["nd", "Appartamento Girasole", "Casale Lucia", "Villa Tulipano", "Pajara Lucy", "Monolocale Marina", "Monolocale Margherita", "Monolocale Glicine"])
        
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
    if not cognome or not nome or not email or not note_aggiuntive:
        st.error("❌ Errore: I campi Cognome, Nome, Email e Note Aggiuntive sono obbligatori per la stesura del log.")
    
    elif email.lower() in email_esistenti:
        st.warning(f"⚠️ VIOLAZIONE REGOLA 1 (DUPLICATI): L'email '{email}' è già presente nello storico. È VIETATO generare una nuova riga di log. Cerca la riga esistente nel database e accorpa i nuovi dettagli nel campo Note Aggiuntive.")
    
    elif "," in note_aggiuntive:
        st.error("❌ Errore di Formattazione: Non puoi utilizzare la virgola ( , ) all'interno delle Note Aggiuntive perché corrompe il tracciato delle colonne del file CSV. Sostituisci tutte le virgole con punti ( . ) o trattini ( - ).")
        
    else:
        ora_attuale = datetime.now().strftime("%H:%M")
        data_oggi = datetime.now().strftime("%d/%m/%Y")
        
        data_arrivo = data_arrivo_dt.strftime("%d/%m/%Y") if data_arrivo_dt else "nd"
        data_partenza = data_partenza_dt.strftime("%d/%m/%Y") if data_partenza_dt else "nd"
        
        nominativo_dettaglio = nominativo_dettaglio if nominativo_dettaglio else "nd"
        alloggio = alloggio if alloggio else "nd"
        
        nuovo_record = f"{prossimo_id},{data_oggi},{ora_attuale},{lead_time},{cognome},{nome},{data_arrivo},{data_partenza},{alloggio},{ospiti_tot},{nominativo_dettaglio},{adulti},{minori},{email},{portale},{acconto},{tariffa_tot},{imposta_sogg},{tipo_tariffa},{stato_pagamento},{mezzo_trasporto},{stato_prenotazione},{note_aggiuntive}\n"
        
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

# ==============================================================================
# ===== BLOCCO 4: SINCRONIZZAZIONE CALENDARI ICAL E DISPONIBILITÀ =====
# ==============================================================================
import urllib.request
from icalendar import Calendar
import pandas as pd
import streamlit as st

st.markdown("---")
st.subheader("📅 Disponibilità Alloggi in Tempo Reale (Sync iCal Octorate)")

# Mapping ufficiale ed aggiornato dei feed reali di Octorate
ICAL_FEEDS = {
    "Appartamento Girasole": "https://admin.octorate.com/cron/ICS/calendar/ics.php?ics=873815_",
    "Casale Lucia": "https://admin.octorate.com/cron/ICS/calendar/ics.php?ics=873817_",
    "Villa Tulipano": "https://admin.octorate.com/cron/ICS/calendar/ics.php?ics=873819_",
    "Pajara Lucy": "https://admin.octorate.com/cron/ICS/calendar/ics.php?ics=874479_",
    "Monolocale Marina": "https://admin.octorate.com/cron/ICS/calendar/ics.php?ics=873826_",
    "Monolocale Margherita": "https://admin.octorate.com/cron/ICS/calendar/ics.php?ics=873824_",
    "Monolocale Glicine": "https://admin.octorate.com/cron/ICS/calendar/ics.php?ics=873821_"
}

def leggi_impegni_ical(url_feed):
    eventi_bloccati = []
    try:
        req = urllib.request.Request(url_feed, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=7) as response:
            ical_data = response.read()
        
        gcal = Calendar.from_ical(ical_data)
        for component in gcal.walk('VEVENT'):
            summary = component.get('summary', 'Occupato / Bloccato')
            dtstart = component.get('dtstart').dt if component.get('dtstart') else None
            dtend = component.get('dtend').dt if component.get('dtend') else None
            
            if dtstart and dtend:
                inizio_str = dtstart.strftime("%d/%m/%Y") if hasattr(dtstart, 'strftime') else str(dtstart)
                fine_str = dtend.strftime("%d/%m/%Y") if hasattr(dtend, 'strftime') else str(dtend)
                eventi_bloccati.append({
                    "Stato/Nota": str(summary), 
                    "Check-in (Dal)": inizio_str, 
                    "Check-out (Al)": fine_str
                })
    except Exception as errore:
        return [{"Stato/Nota": f"Errore sincro: link temporaneamente irraggiungibile ({errore})", "Check-in (Dal)": "-", "Check-out (Al)": "-"}]
    return eventi_bloccati

scelta_alloggio = st.selectbox("Seleziona l'alloggio da monitorare per scaricare le chiusure:", list(ICAL_FEEDS.keys()))

if st.button("🔄 Sincronizza e Verifica Chiusure Octorate"):
    with st.spinner(f"Interrogazione server Octorate per {scelta_alloggio}..."):
        link_selezionato = ICAL_FEEDS[scelta_alloggio]
        blocchi_rilevati = leggi_impegni_ical(link_selezionato)
        
        if blocchi_rilevati and len(blocchi_rilevati) > 0:
            # Corretto l'accesso posizionale per intercettare gli errori di rete senza crash
            if blocchi_rilevati[0]["Check-in (Dal)"] == "-":
                st.error(blocchi_rilevati[0]["Stato/Nota"])
            else:
                df_blocchi = pd.DataFrame(blocchi_rilevati)
                st.dataframe(df_blocchi, use_container_width=True)
                st.info(f"Trovati **{len(df_blocchi)}** periodi di occupazione estratti dal feed remoto.")
        else:
            st.success("✅ Libero! Nessuna prenotazione attiva o blocco impostato su questo calendario.")

# ==============================================================================
# ===== FINE BLOCCO 4 =====
# ==============================================================================



# ==============================================================================
# ===== BLOCCO 5: MODULO DI RICERCA OSPITI ED E-MAIL AUTOMATICHE =====
# ==============================================================================
st.markdown("---")
st.subheader("🔍 Ricerca Storico Ospiti e Generatore E-mail")

if 'df' in locals() and not df.empty:
    chiave_ricerca = st.text_input("Inserisci il Cognome o l'Email dell'ospite da cercare:").strip().lower()
    
    if chiave_ricerca:
        risultati = df[
            df.iloc[:, 4].astype(str).str.lower().str.contains(chiave_ricerca) | 
            df.iloc[:, 13].astype(str).str.lower().str.contains(chiave_ricerca)
        ]
        
        if not risultati.empty:
            st.success(f"Trovati {len(risultati)} record corrispondenti nello storico:")
            st.dataframe(risultati, use_container_width=True)
            
            index_scelto = st.selectbox("Seleziona la riga specifica per generare l'e-mail di risposta:", risultati.index)
            riga_scelta = df.loc[index_scelto]
            
            ospite_nome = riga_scelta.iloc[5] if pd.notna(riga_scelta.iloc[5]) else "Ospite"
            ospite_email = riga_scelta.iloc[13]
            note_storiche = str(riga_scelta.iloc[22]).lower()
            
            st.markdown("### ✉️ Modello E-mail Precompilato")
            st.info(f"Inviare a: **{ospite_email}**")
            
            nota_ritardo = ""
            if "ritard" in note_storiche or "tardiv" in note_storiche:
                nota_ritardo = "Ci scusiamo sinceramente per il ritardo nel risponderle, dovuto a un carico straordinario di richieste in questi giorni.\n\n"
            
            corpo_email = (
                f"Gentile {ospite_nome},\n\n"
                f"{nota_ritardo}"
                f"In merito alla sua richiesta, desideriamo innanzitutto precisare che la nostra struttura si trova a Torre Pali (Marina di Salve), "
                f"nel cuore del Salento ionico, in una posizione ottimale per godersi il mare e le spiagge della zona.\n\n"
                f"Al momento attuale, per il periodo da lei indicato, la struttura è purtroppo al completo. Abbiamo tuttavia provveduto a inserirla "
                f"nella nostra Lista d'Attesa prioritaria: in questo modo, qualora dovesse verificarsi una cancellazione dell'ultimo minuto, "
                f"sarà nostra cura ricontattarla immediatamente.\n\n"
                f"Per ringraziarla dell'interesse e scusarci della mancata disponibilità immediata, siamo lieti di assegnarle un Buono Sconto del 15% "
                f"valido per la Formula Fiduciaria (utilizzabile per un soggiorno futuro o qualora si liberasse il posto).\n\n"
                f"Vi ricordiamo la nostra politica di Trasparenza e Sicurezza: la Formula Fiduciaria non richiede MAI il versamento di alcun acconto o caparra "
                f"all'atto della prenotazione. Si tratta di uno scudo antifrode a tutela totale del cliente: il pagamento del soggiorno verrà effettuato "
                f"interamente in loco al momento del vostro arrivo, dopo aver preso visione dell'alloggio.\n\n"
                f"Restiamo a sua completa disposizione per qualsiasi ulteriore informazione e ci auguriamo di averla presto come nostro gradito ospite.\n\n"
                f"Cordiali saluti,\n"
                f"Lo Staff - A Casa di Amici\n"
                f"https://acasadiamici.info"
            )
            st.code(corpo_email, language="text")
        else:
            st.warning("❌ Nessun ospite trovato con i criteri inseriti.")

st.markdown("---")
# ==============================================================================
# ===== FINE BLOCCO 5 - DA QUI IN POI COMINCIA IL TUO SCANNER RICORRENZE =====
# ==============================================================================

