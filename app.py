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

# 4. Definizione del percorso locale (Offline) per il database degli ospiti
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
        st.success(f"📊 Database locale caricato correttamente. Record totali rilevati: {len(df)}")
    else:
        df = pd.DataFrame()
        st.warning(f"File '{csv_locale}' non trovato nella cartella principale del progetto.")
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
# ===== BLOCCO 3 - PARTE 1: INTERFACCIA RAPIDA INTELLIGENTE (PARSER) =====
# ==============================================================================
import os
import re
from datetime import datetime
import pandas as pd
import streamlit as st

st.markdown("---")
st.subheader("🚀 Inserimento Rapido Intelligente (Incolla Email Grezza)")
st.info("Incolla qui sotto il testo copiato dalla notifica email per estrarre e mapparne i dati in modo avanzato.")

# Calcolo del progressivo dinamico basato sull'ultima riga reale del file di GitHub
if 'df' in locals() and not df.empty:
    try:
        # Forziamo la conversione in numerico della prima colonna pulendola da intestazioni
        id_puliti = pd.to_numeric(df.iloc[:, 0], errors='coerce').dropna()
        prossimo_id = int(id_puliti.max()) + 1
    except:
        prossimo_id = 609  # Fallback di sicurezza basato sullo storico attuale
    email_esistenti = df.iloc[:, 13].dropna().astype(str).str.lower().str.strip().tolist()
else:
    prossimo_id = 609
    email_esistenti = []

# Casella di testo unica ad alta capacità per il testo della mail
testo_email_grezzo = st.text_area("Incolla qui il testo della mail ricevuta:", height=220, placeholder="Incolla la notifica di UltimissimoMinuto o LovelyITALIA...")

if st.button("⚡ Parsifica e Mostra Anteprima Ricca"):
    if not testo_email_grezzo.strip():
        st.error("❌ Il campo di testo è vuoto. Incolla una notifica prima di procedere.")
    else:
        # --- ALGORITMO DI ESTRAZIONE AUTOMATICA AVANZATA ---
        testo_pulito = re.sub(r'\s+', ' ', testo_email_grezzo) 
        
        # 1. Estrazione Email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', testo_pulito)
        estratto_email = email_match.group(0).strip() if email_match else "nd"
        
        # 2. Estrazione Telefono
        tel_match = re.search(r'(?:Telefono|Tel\.?|Cell\.?)\s*:?\s*([0-9\s\-]{8,15})', testo_pulito, re.IGNORECASE)
        estratto_tel = tel_match.group(1).strip() if tel_match else ""
        if not Talk or not estratto_tel:
            tel_match_libero = re.search(r'\b(3\d{2}[0-9\s\-]{6,8})\b', testo_pulito)
            estratto_tel = tel_match_libero.group(1).strip() if tel_match_libero else "nd"
            
        # 3. Estrazione Nome/Nominativo senza troncamenti erratici
        nome_match = re.search(r'Nome\s+([A-Za-zÀ-ú\s]+?)(?=\s+Num|\s+Adulti|\s+Email|$)', testo_pulito, re.IGNORECASE)
        estratto_nome = nome_match.group(1).strip() if nome_match else "nd"
        
        # 4. Estrazione Ospiti, Adulti, Minori
        adulti_match = re.search(r'(?:Num\.\s*Adulti|Adulti)\s*(\d+)', testo_pulito, re.IGNORECASE)
        estratto_adulti = int(adulti_match.group(1)) if adulti_match else 2
        
        # Conteggio intelligente dei minori dalle righe aggiuntive delle email
        minori_match = re.search(r'(\d+)\s*(?:bambini|minori|ragazzi|figli)', testo_pulito, re.IGNORECASE)
        estratto_minori = int(minori_match.group(1)) if minori_match else 0
        estratto_ospiti_tot = estratto_adulti + estratto_minori
        
        # Estrazione dettagliata dell'età dei bambini per le note di marketing mirato
        dettaglio_eta = ""
        eta_match = re.search(r'(bambini\s*di\s*[\d\s,e]+anni)', testo_pulito, re.IGNORECASE)
        if eta_match: dettaglio_eta = eta_match.group(1).strip()



                # --- BLOCCO 3 - PARTE 2: PROSEGUIMENTO ESTRATTORI E SALVATAGGIO ---
        # 5. Identificazione Portale
        estratto_portale = "UltimissimoMinuto" if "prop105499" in testo_pulito or "ultimissimo" in testo_pulito.lower() else "nd"
        if estratto_portale == "nd" and "lovely" in testo_pulito.lower(): estratto_portale = "LovelyITALIA"

        # 6. Estrazione Date (Arrivo e Partenza)
        date_trovate = re.findall(r'(\d{1,2})\s*[\/\-]\s*(\d{1,2})\s*[\/\-]\s*(\d{4})', testo_pulito)
        data_contatto_str = datetime.now().strftime("%d/%m/%Y")
        estratto_arrivo, estratto_partenza, lead_time = "nd", "nd", 0
        
        if len(date_trovate) >= 2:
            d_arr, d_part = date_trovate[-2], date_trovate[-1]
            estratto_arrivo = f"{int(d_arr):02d}/{int(d_arr):02d}/{d_arr}"
            estratto_partenza = f"{int(d_part):02d}/{int(d_part):02d}/{d_part}"
            try:
                dt_contatto = datetime.strptime(data_contatto_str, "%d/%m/%Y")
                dt_arrivo = datetime.strptime(estratto_arrivo, "%d/%m/%Y")
                lead_time = max(0, (dt_arrivo - dt_contatto).days)
            except: lead_time = 0
                
        # 7. Estrazione Località Richiesta
        localita_match = re.search(r'(?:Localita\'?\s*richiesta\s*:?)\s*([A-Za-zÀ-ú\s]+(?:dintorni)?)', testo_pulito, re.IGNORECASE)
        estratto_localita = localita_match.group(1).strip() if localita_match else "nd"
        
        # 8. Estrazione Cani ed Animali (Mappatura Colonna 16 del database)
        cane_match = re.search(r'(\d*\s*(?:cane|cani|gatto|gatti|animale|animali)\s*(?:taglia|piccola|media|grande|nd|\w+)*)', testo_pulito, re.IGNORECASE)
        estratto_cane = cane_match.group(1).strip() if cane_match else "nd"
        
        # Creazione note senza colonna extra (scudo anti-virgola totale)
        ora_attuale = datetime.now().strftime("%H:%M")
        note_pulite = f"Telefono: {estratto_tel}. Ricevuto tramite {estratto_portale}. Localita richiesta: {estratto_localita}."
        if dettaglio_eta: note_pulite += f" Segmentazione marketing: {dettaglio_eta}."
        note_pulite = note_pulite.replace(",", " -")

        # Controllo preventivo duplicati ed emissione output grafico ricco a schermo
        if estratto_email.lower() in email_esistenti and estratto_email != "nd":
            st.warning(f"⚠️ VIOLAZIONE REGOLA 1: L'email '{estratto_email}' è già presente. Record bloccato.")
        else:
            st.summary = f"✅ Dati elaborati! ID Assegnato coerente con lo storico: **{prossimo_id}**"
            st.success(st.summary)
            
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.markdown("**📊 Tabella Campi Estratti:**")
                st.write(f"• **Ospite:** {estratto_nome} | **Email:** {estratto_email}")
                st.write(f"• **Periodo:** {estratto_arrivo} - {estratto_partenza} ({lead_time}gg Lead Time)")
                st.write(f"• **Nucleo:** {estratto_adulti} Adulti e {estratto_minori} Minori ({dettaglio_eta})")
                st.write(f"• **Località originaria:** {estratto_localita}")
                
                # Stringa record pronta per l'inserimento in coda al file database_ospiti.csv
                stringa_csv = f"{prossimo_id},{data_contatto_str},{ora_attuale},{lead_time},nd,{estratto_nome},{estratto_arrivo},{estratto_partenza},nd,{estratto_ospiti_tot},nd,{estratto_adulti},{estratto_minori},{estratto_email},{estratto_portale},{estratto_cane},nd,nd,nd,nd,nd,Lista d'attesa,{note_pulite}"
                st.markdown("**📝 Riga di log generata (Pronta da inserire in fondo al tuo file CSV):**")
                st.code(stringa_csv, language="text")
                
            with col_r2:
                st.markdown("**✉️ E-mail Istituzionale Completa ed Estesa:**")
                corpo_email_veloce = (
                    f"Gentile {estratto_nome},\n\n"
                    f"La ringraziamo sinceramente per aver espresso il suo interesse verso la nostra struttura \"A Casa di Amici\" per il vostro prossimo soggiorno in Puglia.\n\n"
                    f"In merito alla sua richiesta inviata tramite il portale {estratto_portale} per il periodo dal {estratto_arrivo} al {estratto_partenza}, ci teniamo innanzitutto a precisare che le nostre soluzioni abitative (tra cui l'Appartamento Girasole, Villa Tulipano, Casale Lucia, la caratteristica Pajara Lucy e i nostri Monolocali Marina, Margherita e Glicine) si trovano nella splendida località balneare di Torre Pali (Marina di Salve), sul litorale ionico salentino, famosa per le spiagge di sabbia fine e le acque cristalline.\n\n"
                    f"Abbiamo verificato i nostri registri: trattandosi di un periodo di altissima stagione, le nostre unità risultano al momento interamente occupate per le date richieste dal vostro nucleo familiare di {estratto_ospiti_tot} persone.\n\n"
                    f"Abbiamo tuttavia provveduto a inserire il suo nominativo all'interno della nostra Lista d'Attesa prioritaria per la gestione delle cancellazioni. Qualora dovesse verificarsi una disdetta imprevista, sarà nostra premura contattarla immediatamente ai recapiti forniti.\n\n"
                    f"Per ringraziarla della fiducia e scusarci della mancanza di alloggi liberi immediati, siamo lieti di assegnarle un Buono Sconto speciale del 15% valido per la nostra exclusive \"Formula Fiduciaria\", utilizzabile sia per un'eventuale apertura di questo periodo sia per qualsiasi soggiorno futuro presso di noi.\n\n"
                    f"Ci teniamo a sottolineare la massima trasparenza della nostra politica di prenotazione: la Formula Fiduciaria non richiede MAI il versamento di alcun acconto, caparra confirmatoria o transazione bancaria anticipata all'atto del blocco delle date. Si tratta di un vero e proprio scudo antifrode a tutela totale del cliente: l'accordo si basa sulla reciproca parola e il pagamento del soggiorno verrà effettuato interamente in loco, al momento del vostro arrivo in struttura, solo dopo aver preso visione dell'alloggio ed averne confermato il gradimento.\n\n"
                    f"Restiamo a sua completa disposizione per qualsiasi chiarimento. Ci auguriamo di potervi accogliere presto come nostri graditi ospiti nel Salento.\n\n"
                    f"Cordiali saluti,\n"
                    f"Lo Staff - A Casa di Amici\n"
                    f"https://acasadiamici.info"
                )
                st.code(corpo_email_veloce, language="text")
# ==============================================================================
# ===== FINE BLOCCO 3 - PARTE 2 =====
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

