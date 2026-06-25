import streamlit as st
import csv
import re
import urllib.parse
import pandas as pd
from datetime import datetime

# CONFIGURAZIONE INIZIALE E GRAFICA DI CIMA
st.set_page_config(page_title="CRM A Casa di Amici", layout="wide", initial_sidebar_state="expanded")

# Controllo Password di Sicurezza in Italiano (Sicurezza CEO)
if "autenticato" not in st.session_state:
 st.session_state["autenticato"] = False

if not st.session_state["autenticato"]:
 st.image("logo-scritta.gif", use_container_width=False, width=280)
 st.subheader("🔒 Accesso Riservato — Direzione A Casa di Amici")
 pass_inserita = st.text_input("Inserisci la password di sblocco amministratore:", type="password")
 if st.button("Sblocca Pannello"):
 if "PASSWORD_CRM" in st.secrets and pass_inserita == st.secrets["PASSWORD_CRM"]:
 st.session_state["autenticato"] = True
 st.rerun()
 else:
 st.error("❌ Password errata! Accesso negato.")
 st.stop()

# Logo aziendale e Titoli principali
st.image("logo-scritta.gif", use_container_width=False, width=280)
st.title("📊 Pannello di Controllo CRM - A Casa di Amici")
st.caption("CEO Management System — Marco Antonio  De Pietro")

DB_FILE = "database_ospiti.csv"

# =========================================================================
# FUNZIONI DI SERVIZIO NATIVE (LETTURA, SCRITTURA E LINK)
# =========================================================================
def carica_database_nativo():
 colonne = [
 "numero progressiv o", "Data del contatt o", "Ora del contatt o", "Cognom e", "Nom e",
 "data presunta di Arriv o", "data presunta di Partenz a", "Numero Ospit i", "adult i",
 "minor i", "Emai l", "Portale di provenienz a", "Note aggiuntiv e", "Cane (Razza/Taglia)", "Esit o"
 ]
 righe = []
 try:
 with open(DB_FILE, mode="r", encoding="utf-8") as f:
 reader = csv.DictReader(f)
 for riga in reader:
 righe.append(dict(riga))
 except FileNotFoundError:
 st.error(f"⚠️ Errore: Il file {DB_FILE} non è stato trovato!")
 return colonne, righe

def salva_database_nativo(colonne, righe):
 with open(DB_FILE, mode="w", encoding="utf-8", newline="") as f:
 writer = csv.DictWriter(f, fieldnames=colonne)
 writer.writeheader()
 for riga in righe:
 writer.writerow(riga)

def genera_link_whatsapp(telefono, messaggio):
 telefono_pulito = "".join(filter(str.isdigit, str(telefono)))
 if telefono_pulito and not telefono_pulito.startswith("39") and len(telefono_pulito) == 10:
 telefono_pulito = "39" + telefono_pulito
    testo_link = urllib.parse.quote(messaggio)
    return f"https://wa.me{telefono_pulito}?text={testo_link}"

# =========================================================================
# FUNZIONE GENERATRICE TABELLA IN FORMATO TESTO PULITO
# =========================================================================
def mostra_tabella_pulita(lista_righe):
    if not lista_righe:
        st.write("Nessun dato da mostrare.")
        return
    df = pd.DataFrame(lista_righe)
    
    colonne_visibili_csv = [
        "numero progressiv o", "Data del contatt o", "Ora del contatt o", "Cognom e", 
        "Nom e", "data presunta di Arriv o", "Portale di provenienz a", "Esit o"
    ]
    colonne_presenti = [c for c in colonne_visibili_csv if c in df.columns]
    df_da_mostrare = df[colonne_presenti].copy()
    
    mappatura_nomi_belli = {
        "numero progressiv o": "Progressivo",
        "Data del contatt o": "Data contatto",
        "Ora del contatt o": "Ora contatto",
        "Cognom e": "Cognome",
        "Nom e": "Nome",
        "data presunta di Arriv o": "Data Arrivo",
        "Portale di provenienz a": "Portale provenienza",
        "Esit o": "Esito"
    }
    df_da_mostrare = df_da_mostrare.rename(columns=mappatura_nomi_belli)
    
    st.dataframe(df_da_mostrare, use_container_width=True, hide_index=True)
    st.write("🔍 **Apertura rapida scheda per modifica:**")
    
    lista_id = [str(r.get('numero progressiv o', '')).strip() for r in lista_righe if str(r.get('numero progressiv o', '')).strip()]
    
    id_scelto = st.selectbox(
        "Seleziona il numero di riga del cliente che vuoi modificare:", 
        [""] + lista_id, 
        key="selettore_rapido_tabella"
    )
    if id_scelto:
        st.session_state["id_da_modificare"] = str(id_scelto)
        st.success(f"👍 Record #{id_scelto} pronto! Clicca sulla scheda 'Gestione/Modifica Contatto' in alto per aprirlo.")
        st.rerun()

# =========================================================================
# STRUTTURA MENU ORIZZONTALE E DASHBOARD KPI + NOTIFICHE RICORRENZE
# =========================================================================
tab_dashboard, tab_archivio, tab_marketing, tab_gestione = st.tabs([
    "📊 CEO Dashboard", "📋 Archivio Ospiti", "🎯 Marketing Iper-Target", "➕ Gestione/Modifica Contatto"
])

colonne, righe = carica_database_nativo()

with tab_dashboard:
    st.subheader("📊 Andamento Business e KPI della Stagione")
    totale_contatti = len(righe)
    confermate = sum(1 for r in righe if "✅ confermata" in str(r.get("Esit o", "")).lower().strip())
    pet_friendly = sum(1 for r in righe if str(r.get("Cane (Razza/Taglia)", "")).strip() and str(r.get("Cane (Razza/Taglia)", "")).lower() not in ["no", "da chiedere", "none", ""])
    
    lista_giorni_anticipo = []
    for r in righe:
        data_c = str(r.get("Data del contatt o", "")).strip()
        data_a = str(r.get("data presunta di Arriv o", "")).strip()
        if data_c and data_a and data_c != "-" and data_a != "-":
            data_c_pulita = data_c.split()[0].replace("-", "/")
            data_a_pulita = data_a.split()[0].replace("-", "/")
            try:
                dt_contatto = datetime.strptime(data_c_pulita, "%d/%m/%Y")
                dt_arrivo = datetime.strptime(data_a_pulita, "%d/%m/%Y")
                giorni = (dt_arrivo - dt_contatto).days
                if giorni >= 0:
                    lista_giorni_anticipo.append(giorni)
            except ValueError:
                continue
                
    if lista_giorni_anticipo:
        lead_time_reale = int(sum(lista_giorni_anticipo) / len(lista_giorni_anticipo))
        lead_time_stringa = f"{lead_time_reale} Giorni"
    else:
        lead_time_stringa = "N/D"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Totale Lead (Richieste)", totale_contatti)
    col2.metric("Prenotazioni Confermate", confermate)
    col3.metric("Clienti con Animali", pet_friendly)
    col4.metric("Lead Time Medio Reale", lead_time_stringa)

    # 🚨 SCANNER AUTOMATICO DELLE RICORRENZE FAMILIARI
    st.markdown("---")
    st.subheader("🔔 Scadenze e Ricorrenze Ospiti (Prossimi 7 giorni)")
    
    oggi = datetime.now()
    compleanni_imminenti = []
    onomastici_imminenti = []
    
    for r in righe:
        note_campo = str(r.get("Note aggiuntiv e", ""))
        nome_cliente = f"{r.get('Nom e', '')} {r.get('Cognom e', '')}".replace("-", "").strip()
        
        # 1. Parsing Compleanni
        if "[Compleanni:" in note_campo:
            estratto_bday = note_campo.split("[Compleanni:")[1].split("]")[0]
            date_bday = re.findall(r'(\d{2}/\d{2})', estratto_bday)
            if date_bday:
                for d in date_bday:
                    try:
                        b_day = datetime.strptime(d, "%d/%m").replace(year=oggi.year)
                        differenza = (b_day - oggi.replace(hour=0, minute=0, second=0, microsecond=0)).days
                        if 0 <= differenza <= 7:
                            compleanni_imminenti.append(f"🎂 **{estratto_bday.strip()}** (Gruppo: {nome_cliente}) - tra {differenza} giorni")
                    except ValueError:
                        continue

        # 2. Parsing Onomastici
        if "[Onomastici:" in note_campo:
            estratto_onom = note_campo.split("[Onomastici:")[1].split("]")[0]
            date_onom = re.findall(r'(\d{2}/\d{2})', estratto_onom)
            if date_onom:
                for d in date_onom:
                    try:
                        o_day = datetime.strptime(d, "%d/%m").replace(year=oggi.year)
                        differenza = (o_day - oggi.replace(hour=0, minute=0, second=0, microsecond=0)).days
                        if 0 <= differenza <= 7:
                            onomastici_imminenti.append(f"😇 **{estratto_onom.strip()}** (Gruppo: {nome_cliente}) - tra {differenza} giorni")
                    except ValueError:
                        continue

    if compleanni_imminenti or onomastici_imminenti:
        col_comp, col_onom = st.columns(2)
        with col_comp:
            if compleanni_imminenti:
                st.info("🎁 **Compleanni in arrivo:**")
                for c in compleanni_imminenti:
                    st.write(c)
            else:
                st.write("✅ Nessun compleanno nei prossimi 7 giorni.")
        with col_onom:
            if onomastici_imminenti:
                st.warning("✨ **Onomastici in arrivo:**")
                for o in onomastici_imminenti:
                    st.write(o)
            else:
                st.write("✅ Nessun onomastico nei prossimi 7 giorni.")
    else:
        st.success("🎉 Nessuna ricorrenza familiare rilevata per i prossimi 7 giorni.")

with tab_archivio:
    st.subheader("📋 Visualizzazione Registri Database")
    st.write("Questo è lo specchietto completo del tuo file database_ospiti.csv aggiornato in tempo reale.")
    mostra_tabella_pulita(righe)

# =========================================================================
# SEZIONE MARKETING TARGETIZZATO (ESTRAZIONE LISTE)
# =========================================================================
with tab_marketing:
    st.subheader("🎯 Estrazione Liste per Campagne Pubblicitarie")
    filtro_pet = st.checkbox("🐾 Mostra solo clienti con animali (Filtro Pet-Friendly)")
    if filtro_pet:
        lista_filtrata = [r for r in righe if str(r.get("Cane (Razza/Taglia)", "")).strip() and str(r.get("Cane (Razza/Taglia)", "")).lower() not in ["no", "da chiedere", "none", ""]]
        lista_da_profilare = [r for r in righe if "da chiedere" in str(r.get("Cane (Razza/Taglia)", "")).lower()]
        
        if lista_filtrata:
            st.success(f"🐾 Trovati {len(lista_filtrata)} clienti con animali già profilati nel database!")
            mostra_tabella_pulita(lista_filtrata)
            st.subheader("📋 Copia Rapida Contatti per Campagne 2027")
            
            emails_filtrate = [str(r.get("Emai l", "")).strip() for r in lista_filtrata if str(r.get("Emai l", "")).strip()]
            st.info("💡 Ricorda di inserire il codice CIN obbligatorio nelle tue comunicazioni: IT075066C200054604")
            st.text_area("Incolla questa lista nel campo 'CCN' della tua e-mail per l'invio massivo:", value="; ".join(emails_filtrate), height=70)
        else:
            st.info("Nessun cliente con animali già profilato trovato all'interno del database.")
            
        if lista_da_profilare:
            st.markdown("---")
            st.warning(f"⚠️ Ci sono {len(lista_da_profilare)} contatti caldi a cui devi ancora chiedere dettagli sul cane!")
            with st.expander("🔍 Visualizza l'elenco dei contatti da profilare subito:"):
                for cp in lista_da_profilare:
                    nome_t = cp.get('Nom e', '').strip()
                    cognome_t = cp.get('Cognom e', '').strip()
                    email_t = cp.get('Emai l', '').strip()
                    arrivo_t = cp.get('data presunta di Arriv o', '').strip()
                    note_t = cp.get('Note aggiuntiv e', '').strip()
                    st.write(f"- **{nome_t} {cognome_t}** ({email_t}) — Arrivo: {arrivo_t} | Nota: {note_t[:50]}...")
    else:
        st.write("💡 Seleziona il filtro sopra per estrarre la lista dei contatti mirata.")

# =========================================================================
# PANNELLO GESTIONE DATI, MODIFICA E MODULO WHATSAPP
# =========================================================================
with tab_gestione:
    tipo_operazione = st.radio("Seleziona tipo di attività:", ["Inserisci un Nuovo Ospite", "Modifica un Record Esistente"])
    
    if tipo_operazione == "Inserisci un Nuovo Ospite":
        st.subheader("🚀 Incolla Rapido (Copia l'intera email del portale qui sotto):")
        testo_richiesta = st.text_area("Incolla qui l'intero testo della richiesta:", value="", height=150)
        ora_contatto = st.text_input("Ora del contatto (es. 12:15):", value=datetime.now().strftime("%H:%M"))
        check_cognome = st.text_input("Inserisci Cognome per controllo storico rapido:", value="")
        
        if st.button("Analizza ed Estrai Automaticamente"):
            if testo_richiesta.strip():
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', testo_richiesta)
                email_estratta = email_match.group(0) if email_match else ""
                
                date_trovate = re.findall(r'\b\d{2}[/\-]\d{2}[/\-]\d{4}\b', testo_richiesta)
                arrivo_estratto = date_trovate[0] if len(date_trovate) > 0 else datetime.now().strftime("%d/%m/%Y")
                partenza_estratta = date_trovate[1] if len(date_trovate) > 1 else ""
                
                ospiti_match = re.search(r'(?:Ospiti|Persone|Numero Ospiti):\s*(\d+)', testo_richiesta, re.IGNORECASE)
                adulti_match = re.search(r'(?:Adulti):\s*(\d+)', testo_richiesta, re.IGNORECASE)
                minori_match = re.search(r'(?:Minori|Bambini):\s*(\d+)', testo_richiesta, re.IGNORECASE)
                
                ospiti_estratto = ospiti_match.group(1) if ospiti_match else "2"
                adulti_estratto = adulti_match.group(1) if adulti_match else ospiti_estratto
                minori_estratto = minori_match.group(1) if minori_match else "0"
                
                portale_estratto = "Sito Diretto"
                for p in ["Booking", "Airbnb", "Vrbo", "Lovely", "UltMin", "Agoda", "Idealista"]:
                    if p.lower() in testo_richiesta.lower():
                        portale_estratto = p
                        break
                
                nuovo_progressivo = str(len(righe) + 1)
                nuovo_record = {
                    "numero progressiv o": nuovo_progressivo,
                    "Data del contatt o": datetime.now().strftime("%d/%m/%Y"),
                    "Ora del contatt o": ora_contatto,
                    "Cognom e": check_cognome if check_cognome else "-",
                    "Nom e": "-",
                    "data presunta di Arriv o": arrivo_estratto,
                    "data presunta di Partenz a": partenza_estratta,
                    "Numero Ospit i": ospiti_estratto,
                    "adult i": adulti_estratto,
                    "minor i": minori_estratto,
                    "Emai l": email_estratta,
                    "Portale di provenienz a": portale_estratto,
                    "Note aggiuntiv e": f"Estratto automaticamente da e-mail: {testo_richiesta[:200]}",
                    "Cane (Razza/Taglia)": "Da chiedere",
                    "Esit o": "🔄 In corso"
                }
                
                righe.append(nuovo_record)
                salva_database_nativo(colonne, righe)
                
                st.success(f"🎉 Fantastico! Record #{nuovo_progressivo} inserito con successo!")
                st.session_state["id_da_modificare"] = nuovo_progressivo
                st.rerun()
            else:
                st.error("❌ Il campo di testo è vuoto! Incolla prima il testo dell'email.")
                
    elif tipo_operazione == "Modifica un Record Esistente":
        st.subheader("🔍 Gestione e Modifica Scheda Cliente")
        valore_promemoria = ""
        if "id_da_modificare" in st.session_state and st.session_state["id_da_modificare"]:
            valore_promemoria = str(st.session_state["id_da_modificare"])
            st.info(f"👉 NUMERO SELEZIONATO DALL'ARCHIVIO: {valore_promemoria}")
            
        chiave_ricerca = st.text_input("Cerca cliente (Inserisci Telefono, Email, Cognome o Numero di riga):", value=valore_promemoria).strip().lower()
        riga_trovata = None
        storico_cliente = []
        
        if chiave_ricerca:
            for r in righe:
                prog = str(r.get("numero progressiv o", "")).strip().lower()
                cognome = str(r.get("Cognom e", "")).strip().lower()
                email = str(r.get("Emai l", "")).strip().lower()
                note = str(r.get("Note aggiuntiv e", "")).strip().lower()
                if (chiave_ricerca == prog or chiave_ricerca in cognome or chiave_ricerca in email or chiave_ricerca in note):
                    riga_trovata = r
                    break
                    
            if riga_trovata:
                cognome_target = str(riga_trovata.get("Cognom e", "")).strip().lower()
                email_target = str(riga_trovata.get("Emai l", "")).strip().lower()
                for r in righe:
                    if (cognome_target and str(r.get("Cognom e", "")).strip().lower() == cognome_target) or (email_target and str(r.get("Emai l", "")).strip().lower() == email_target):
                        storico_cliente.append(r)
                        
        if riga_trovata:
            prog_id = riga_trovata.get('numero progressiv o', '').strip()
            nome_id = riga_trovata.get('Nom e', '').strip()
            cognome_id = riga_trovata.get('Cognom e', '').strip()
            st.success(f"Scheda Ospite Rilevata: Record #{prog_id} — {nome_id} {cognome_id}")
            
            col_sinistra, col_destra = st.columns(2)
            with col_sinistra:
                nuovo_cognome = st.text_input("Cognome Titolare:", riga_trovata.get("Cognom e", "").strip())
                nuovo_nome = st.text_input("Nome Titolare:", riga_trovata.get("Nom e", "").strip())
                nuovo_arrivo = st.text_input("Data Arrivo:", riga_trovata.get("data presunta di Arriv o", "").strip())
                nuovo_partenza = st.text_input("Data Partenza:", riga_trovata.get("data presunta di Partenz a", "").strip())
                nuovo_nominativi = st.text_area("Nominativi Completi Ospiti del Gruppo (Mappatura Arrivi):", value="")
            with col_destra:
                nuovo_email = st.text_input("Email Titolare:", riga_trovata.get("Emai l", "").strip())
                nota_per_tel = riga_trovata.get("Note aggiuntiv e", "")
                match_tel_iniziale = re.search(r'(?:Telefono|Tel|tel|Telefono:)\s*([0-9\+\s]{8,15})', nota_per_tel)
                tel_iniziale = match_tel_iniziale.group(1).strip() if match_tel_iniziale else ""
                nuovo_telefono = st.text_input("Telefono / cellulare:", value=tel_iniziale)
                nuovo_cane = st.text_input("Cane (Razza/Taglia):", riga_trovata.get("Cane (Razza/Taglia)", "").strip())
                
                esito_attuale = riga_trovata.get("Esit o", "").strip()
                lista_esiti = ["📋 Lista attesa", "🔄 In corso", "✅ Confermata", "❌ Cancellata", "🔄 Pre-approvata", "❌ Non disponibile", "⚠ Alert attivo", "🗄 Storico 2024", "🗄 Storico 2025"]
                indice_esito = lista_esiti.index(esito_attuale) if esito_attuale in lista_esiti else 0
                nuovo_esito = st.selectbox("Esito Prenotazione:", lista_esiti, index=indice_esito)

            st.markdown("---")
            st.subheader("🎂 Anagrafica Ospiti per Campagne di Fidelizzazione")
            st.caption("Compila questi spazi durante le operazioni di check-in per memorizzare le leve di marketing diretto di tutto il gruppo familiare.")
            
            col_bday, col_onomastico = st.columns(2)
            with col_bday:
                nuovo_compleanni = st.text_area(
                    "Date dei Compleanni della Famiglia (Nome Cognome - GG/MM/AAAA):", 
                    value="", 
                    help="Es: Marco Rossi (12/05/1980) - Luca Rossi (24/10/2015)"
                )
            with col_onomastico:
                nuovo_onomastici = st.text_area(
                    "Date degli Onomastici della Famiglia (Nome - Giorno/Mese):", 
                    value="", 
                    help="Es: San Marco (25/04) - Sant'Anna (26/07)"
                )
                
            nuove_note = st.text_area("Note Aggiuntive e Dettagli Soggiorno:", value=riga_trovata.get("Note aggiuntiv e", "").strip(), height=100)
            st.markdown("---")

            st.subheader("📱 Seleziona Canale e Invia Comunicazione")
            canale_scelto = st.radio("Come preferisci contattare l'ospite?", ["Invia tramite WhatsApp", "Invia tramite E-mail"])
            oggetto_mail = urllib.parse.quote(f"Aggiornamento vacanza A Casa di Amici - {nuovo_nome} {nuovo_cognome}")
            corpo_messaggio = f"Ciao {nuovo_nome}, ci tenevo a informarti che abbiamo aggiornato i dettagli per il vostro soggiorno presso la nostra tenuta. Un saluto a tutta la famiglia e una carezza a {nuovo_cane}! Ci vediamo presto, un caro saluto, Marco - A Casa di Amici\n\nCodice CIN Nazionale: IT075066C200054604"
            
            if canale_scelto == "Invia tramite WhatsApp":
                if nuovo_telefono:
                    messaggio_wa = st.text_area("Testo del messaggio WhatsApp pronto da inviare:", value=corpo_messaggio, key="wa_text")
                    link_wa = genera_link_whatsapp(nuovo_telefono, messaggio_wa)
                    st.markdown(f'<a href="{link_wa}" target="_blank"><button style="background-color:#25D366;color:white;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;font-weight:bold;">🚀 INVIA MESSAGGIO RAPIDO WHATSAPP</button></a>', unsafe_allow_html=True)
else:
st.warning("⚠️ Impossibile generare il link: inserisci un numero di telefono valido nel campo sopra.")
elif canale_scelto == "Invia tramite E-mail":
if nuovo_email:
messaggio_mail = st.text_area("Testo dell'e-mail pronto da inviare:", value=corpo_messaggio, key="mail_text")
corpo_mail_encoded = urllib.parse.quote(messaggio_mail)
link_mail = f"mailto:{nuovo_email}?subject={oggetto_mail}&body={corpo_mail_encoded}"
st.markdown(f'? APRI E COMPILA EMAIL AUTOMATICA', unsafe_allow_html=True)
else:
st.warning("⚠️ Impossibile generare l'email: indirizzo e-mail non presente per questo ospite.") 
