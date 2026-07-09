# ==============================================================================
# ===== BLOCCO A: CONFIGURAZIONE GENERALE E IMPORTAZIONI =====
# ==============================================================================
from datetime import datetime
import os
import re                      # Necessario per lo Scanner Ricorrenze
import urllib.request
from icalendar import Calendar
import pandas as pd
import streamlit as st

# Impostazione della visualizzazione orizzontale e del titolo della scheda browser
st.set_page_config(
    page_title="CRM A Casa di Amici",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ==============================================================================
# ===== BLOCCO B: LOGO AZIENDALE E TITOLO DINAMICO =====
# ==============================================================================
# Posizionamento del logo aziendale salvato nella root del progetto
logo_locale = "logo-scritta.gif"
if os.path.exists(logo_locale):
    st.image(logo_locale, width=300)
else:
    st.info("Logo aziendale non rilevato localmente nella root del progetto.")

# Calcolo dell'anno automatico senza manutenzione futura del codice
anno_corrente = datetime.now().year
st.title(f"🏨 CRM A Casa di Amici - Gestione Stagionale {anno_corrente}")
# ==============================================================================
# ===== BLOCCO C: CARICAMENTO PROTETTO DEL DATABASE CSV =====
# ==============================================================================
csv_locale = "database_ospiti.csv"
try:
    if os.path.exists(csv_locale):
        df = pd.read_csv(
            csv_locale, 
            encoding="utf-8",
            engine="python",
            quoting=3,
            on_bad_lines="skip"
        )
        st.success(f"📊 Database locale caricato correttamente. Record totali: {len(df)}")
    else:
        df = pd.DataFrame()
        st.warning(f"File '{csv_locale}' non trovato nella cartella principale.")
except Exception as e:
    df = pd.DataFrame()
    st.error(f"Errore critico di lettura nel file CSV locale: {e}")

st.markdown("---")
# ==============================================================================
# ===== BLOCCO D: STRUTTURAZIONE INTERFACCIA A SCHEDE (TABS) =====
# ==============================================================================
# Creazione dei menu per organizzare le funzioni ed evitare disordine visivo
tab_kpi, tab_inserimento, tab_ricerca, tab_ical = st.tabs([
    "📊 Dashboard & Ricorrenze", 
    "🚀 Inserimento Rapido Email", 
    "🔍 Centrale di Ricerca & Filtri", 
    "📅 Calendari iCal Chiusure"
])
# ==============================================================================
# ===== BLOCCO E: CONTENUTO TAB 1 - STATISTICHE E COMPLEANNI =====
# ==============================================================================
with tab_kpi:
    st.subheader("📋 Stato Struttura e Contatori Globali")
    
    # [VECCHIO CODICE ORIGINALE DEL TUO CRUSCOTTO KPI]
    # Incolla qui la tua logica originale che mostrava i contatori grafici delle camere
    
    st.markdown("---")
    st.subheader("🎂 Scanner Compleanni e Onomastici Ospiti (Prossimi 7 giorni)")
    
    # [INCOLLA QUI LE RIGHE DEL TUO VECCHIO SCANNER RICORRENZE DEI COMPLEANNI]
# ==============================================================================
# ===== BLOCCO F: CONTENUTO TAB 2 - INSERIMENTO INTELLIGENTE (PARTE 1) =====
# ==============================================================================
with tab_inserimento:
    st.subheader("📝 Inserimento Istantaneo da Notifiche Email")
    st.info("Incolla l'intero testo della notifica email per mappare automaticamente ogni campo.")

    # Analisi dinamica del prossimo ID coerente per non sovrascrivere i dati
    if 'df' in locals() and not df.empty:
        try:
            id_puliti = pd.to_numeric(df.iloc[:, 0], errors='coerce').dropna()
            prossimo_id = int(id_puliti.max()) + 1
        except: prossimo_id = 609
        email_esistenti = df.iloc[:, 13].dropna().astype(str).str.lower().str.strip().tolist()
    else:
        prossimo_id = 609
        email_esistenti = []

    testo_email_grezzo = st.text_area("Incolla qui il testo della mail ricevuta:", height=200, key="ta_inserimento_scheda")
# ==============================================================================
# ===== BLOCCO G: CONTENUTO TAB 2 - ESTRAZIONE DATI AVANZATA (PARTE 2) =====
# ==============================================================================
    if st.button("⚡ Parsifica e Salva Istantaneamente", key="btn_save_scheda"):
        if not testo_email_grezzo.strip():
            st.error("❌ Il campo di testo è vuoto.")
        else:
            testo_pulito = re.sub(r'\s+', ' ', testo_email_grezzo) 
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', testo_pulito)
            estratto_email = email_match.group(0).strip() if email_match else "nd"
            
            tel_match = re.search(r'(?:Telefono|Tel\.?|Cell\.?)\s*:?\s*([0-9\s\-]{8,15})', testo_pulito, re.IGNORECASE)
            estratto_tel = tel_match.group(1).strip() if tel_match else ""
            if not estratto_tel:
                tel_match_libero = re.search(r'\b(3\d{2}[0-9\s\-]{6,8})\b', testo_pulito)
                estratto_tel = tel_match_libero.group(1).strip() if tel_match_libero else "nd"
                
            nome_match = re.search(r'Nome\s+([A-Za-zÀ-ú\s]+?)(?=\s+Num|\s+Adulti|\s+Email|$)', testo_pulito, re.IGNORECASE)
            estratto_nome = nome_match.group(1).strip() if nome_match else "Ospite"
# ==============================================================================
# ===== BLOCCO H: CONTENUTO TAB 2 - CALCOLO PARSER PAX E DATE (PARTE 3) =====
# ==============================================================================
            adulti_match = re.search(r'(?:Num\.\s*Adulti|Adulti)\s*(\d+)', testo_pulito, re.IGNORECASE)
            estratto_adulti = int(adulti_match.group(1)) if adulti_match else 2
            
            minori_match = re.search(r'(\d+)\s*(?:bambini|minori|ragazzi|figli)', testo_pulito, re.IGNORECASE)
            estratto_minori = int(minori_match.group(1)) if minori_match else 0
            estratto_ospiti_tot = estratto_adulti + estratto_minori
            
            dettaglio_eta = ""
            eta_match = re.search(r'(bambini\s*di\s*[\d\s,e]+anni)', testo_pulito, re.IGNORECASE)
            if eta_match: dettaglio_eta = eta_match.group(1).strip()

            estratto_portale = "UltimissimoMinuto" if "prop105499" in testo_pulito or "ultimissimo" in testo_pulito.lower() else "nd"
            if estratto_portale == "nd" and "lovely" in testo_pulito.lower(): estratto_portale = "LovelyITALIA"

            date_trovate = re.findall(r'(\d{1,2})\s*[\/\-]\s*(\d{1,2})\s*[\/\-]\s*(\d{4})', testo_pulito)
            data_contatto_str = datetime.now().strftime("%d/%m/%Y")
            estratto_arrivo, estratto_partenza, lead_time = "nd", "nd", 0
# ==============================================================================
# ===== BLOCCO I: CONTENUTO TAB 2 - SCRITTURA RECORD E LOGISTICA (PARTE 4) =====
# ==============================================================================
            if len(date_trovate) >= 2:
                d_arr, d_part = date_trovate[-2], date_trovate[-1]
                estratto_arrivo = f"{int(d_arr):02d}/{int(d_arr):02d}/{d_arr}"
                estratto_partenza = f"{int(d_part):02d}/{int(d_part):02d}/{d_part}"
                try:
                    dt_contatto = datetime.strptime(data_contatto_str, "%d/%m/%Y")
                    dt_arrivo = datetime.strptime(estratto_arrivo, "%d/%m/%Y")
                    lead_time = max(0, (dt_arrivo - dt_contatto).days)
                except: lead_time = 0
                    
            localita_match = re.search(r'(?:Localita\'?\s*richiesta\s*:?)\s*([A-Za-zÀ-ú\s]+(?:dintorni)?)', testo_pulito, re.IGNORECASE)
            estratto_localita = localita_match.group(1).strip() if localita_match else "nd"
            
            cane_match = re.search(r'(\d*\s*(?:cane|cani|gatto|gatti|animale|animali)\s*(?:taglia|piccola|media|grande|nd|\w+)*)', testo_pulito, re.IGNORECASE)
            estratto_cane = cane_match.group(1).strip() if cane_match else "nd"
            
            ora_attuale = datetime.now().strftime("%H:%M")
            note_pulite = f"Telefono: {estratto_tel}. Ricevuto tramite {estratto_portale}. Localita richiesta: {estratto_localita}."
            if dettaglio_eta: note_pulite += f" Segmentazione marketing: {dettaglio_eta}."
            note_pulite = note_pulite.replace(",", " -")
# ==============================================================================
# ===== BLOCCO J: CONTENUTO TAB 2 - SALVATAGGIO FISICO ED EMAIL (PARTE 5) =====
# ==============================================================================
            if estratto_email.lower() in email_esistenti and estratto_email != "nd":
                st.warning(f"⚠️ VIOLAZIONE REGOLA 1: L'email '{estratto_email}' è già presente.")
            else:
                nuovo_record = f"{prossimo_id},{data_contatto_str},{ora_attuale},{lead_time},nd,{estratto_nome},{estratto_arrivo},{estratto_partenza},nd,{estratto_ospiti_tot},nd,{estratto_adulti},{estratto_minori},{estratto_email},{estratto_portale},{estratto_cane},nd,nd,nd,nd,nd,Lista d'attesa,{note_pulite}\n"
                try:
                    with open("database_ospiti.csv", "a", encoding="utf-8") as f:
                        f.write(nuovo_record)
                    st.success(f"✅ Record inserito correttamente nel file CSV! ID Assegnato: **{prossimo_id}**")
                    
                    c_sh1, c_sh2 = st.columns(2)
                    with c_sh1:
                        st.markdown("**📋 Campi Mappati:**")
                        st.write(f"• **Ospite:** {estratto_nome} | **Email:** {estratto_email}")
                        st.write(f"• **Date:** {estratto_arrivo} - {estratto_partenza}")
                        st.write(f"• **Pax:** {estratto_adulti} Adulti + {estratto_minori} Minori | **Animali:** {estratto_cane}")
                    with c_sh2:
                        st.markdown("**✉️ Risposta Istituzionale Generata:**")
                        corpo_email_veloce = (
                            f"Gentile {estratto_nome},\n\nLa ringraziamo per l'interesse verso \"A Casa di Amici\".\n\nIn merito alla sua richiesta via {estratto_portale}, precisiamo che la nostra struttura si trova a Torre Pali (Marina di Salve), sul litorale ionico, celebre per le sue spiagge dorate e acque cristalline.\n\nPer le date indicate ({estratto_arrivo} - {estratto_partenza}), siamo purtroppo al completo per via dell'altissima stagione. L'abbiamo inserita nella nostra Lista d'Attesa prioritaria.\n\nPer ringraziarla, le assegniamo un Buono Sconto del 15% con la Formula Fiduciaria (nessun acconto anticipato, pagamento interamente in loco all'arrivo dopo aver visto la stanza).\n\nRestiamo a disposizione.\n\nCordiali saluti,\nLo Staff - A Casa di Amici\nhttps://acasadiamici.info"
                        )
                        st.code(corpo_email_veloce, language="text")
                except Exception as e:
                    st.error(f"Errore di scrittura: {e}")
# ==============================================================================
# ===== BLOCCO K: CONTENUTO TAB 3 - FILTRI DI RICERCA STRATEGICI =====
# ==============================================================================
with tab_ricerca:
    st.subheader("🔍 Filtri di Ricerca Avanzati e Scansione Telefoni")
    if 'df' in locals() and not df.empty:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            chiave_ricerca = st.text_input("✍️ Ricerca per Cognome, Email, Telefono o Note:", key="ti_ricerca_scheda").strip().lower()
        with col_c2:
            schema_filtro = st.selectbox("🎯 Filtri di Segmentazione Rapida:", ["Nessun filtro", "Ospiti con Cane/Animali", "Famiglie con Figli", "Solo Coppie (2 Adulti, 0 Minori)", "Gruppi Numerosi (da 5 persone in su)"], key="sb_filtro_scheda")
        
        df_filtrato = df.copy()
        if schema_filtro == "Ospiti con Cane/Animali":
            df_filtrato = df_filtrato[(df_filtrato.iloc[:, 15].astype(str).str.lower() != "nd") & (df_filtrato.iloc[:, 15].astype(str).str.lower() != "0") | (df_filtrato.iloc[:, 22].astype(str).str.lower().str.contains("cane|cani|cocker|pincer|animali"))]
        elif schema_filtro == "Famiglie con Figli":
            df_filtrato = df_filtrato[(pd.to_numeric(df_filtrato.iloc[:, 12], errors='coerce').fillna(0) > 0) | (df_filtrato.iloc[:, 22].astype(str).str.lower().str.contains("bambin|minore|ragazz|figli"))]
        elif schema_filtro == "Solo Coppie (2 Adulti, 0 Minori)":
            df_filtrato = df_filtrato[(pd.to_numeric(df_filtrato.iloc[:, 11], errors='coerce').fillna(0) == 2) & (pd.to_numeric(df_filtrato.iloc[:, 12], errors='coerce').fillna(0) == 0)]
        elif schema_filtro == "Gruppi Numerosi (da 5 persone in su)":
            df_filtrato = df_filtrato[pd.to_numeric(df_filtrato.iloc[:, 9], errors='coerce').fillna(0) >= 5]

        if chiave_ricerca:
            df_filtrato = df_filtrato[df_filtrato.iloc[:, 4].astype(str).str.lower().str.contains(chiave_ricerca) | df_filtrato.iloc[:, 5].astype(str).str.lower().str.contains(chiave_ricerca) | df_filtrato.iloc[:, 13].astype(str).str.lower().str.contains(chiave_ricerca) | df_filtrato.iloc[:, 22].astype(str).str.lower().str.contains(chiave_ricerca)]
        
        if not df_filtrato.empty:
            st.success(f"🎯 Corrispondenze trovate: {len(df_filtrato)} record.")
            st.dataframe(df_filtrato, use_container_width=True)
        else:
            st.warning("❌ Nessun record corrispondente.")
# ==============================================================================
# ===== BLOCCO L: CONTENUTO TAB 4 - LETTURA FEED ICAL OCTORATE =====
# ==============================================================================
with tab_ical:
    st.subheader("📅 Sincronizzazione iCal Octorate in Tempo Reale")
    ICAL_FEEDS = {
        "Appartamento Girasole": "https://octorate.com_",
        "Casale Lucia": "https://octorate.com_",
        "Villa Tulipano": "https://octorate.com_",
        "Pajara Lucy": "https://octorate.com_",
        "Monolocale Marina": "https://octorate.com_",
        "Monolocale Margherita": "https://octorate.com_",
        "Monolocale Glicine": "https://octorate.com_"
    }

    def leggi_impegni_ical(url_feed):
        eventi_bloccati = []
        try:
            req = urllib.request.Request(url_feed, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=7) as response:
                gcal = Calendar.from_ical(response.read())
            for component in gcal.walk('VEVENT'):
                summary = component.get('summary', 'Occupato / Bloccato')
                dtstart = component.get('dtstart').dt if component.get('dtstart') else None
                dtend = component.get('dtend').dt if component.get('dtend') else None
                if dtstart and dtend:
                    eventi_bloccati.append({"Stato/Nota": str(summary), "Check-in (Dal)": dtstart.strftime("%d/%m/%Y") if hasattr(dtstart, 'strftime') else str(dtstart), "Check-out (Al)": dtend.strftime("%d/%m/%Y") if hasattr(dtend, 'strftime') else str(dtend)})
        except Exception as e: return [{"Stato/Nota": f"Errore sincro: {e}", "Check-in (Dal)": "-", "Check-out (Al)": "-"}]
        return eventi_bloccati

    scelta_alloggio = st.selectbox("Seleziona l'alloggio da controllare:", list(ICAL_FEEDS.keys()), key="sb_alloggio_ical")
    if st.button("🔄 Sincronizza Octorate Now", key="btn_sync_ical"):
        blocchi = leggi_impegni_ical(ICAL_FEEDS[scelta_alloggio])
        if blocchi and blocchi[0]["Check-in (Dal)"] != "-":
            st.dataframe(pd.DataFrame(blocchi), use_container_width=True)
        else: st.success("✅ Libero nei calendari remoti!")


