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
 if pass_inserita == st.secrets["PASSWORD_CRM"]:
 st.session_state["autenticato"] = True
 st.rerun()
 else:
 st.error("❌ Password errata! Accesso negato.")
 st.stop()

# Logo aziendale e Titoli principali (Visibili solo dopo il Login)
st.image("logo-scritta.gif", use_container_width=False, width=280)
st.title("📊 Pannello di Controllo CRM - A Casa di Amici")
st.caption("CEO Management System — Marco De Pietro")

DB_FILE = "database_ospiti.csv"

# =========================================================================
# FUNZIONI DI SERVIZIO NATIVE (LETTURA, SCRITTURA E LINK)
# =========================================================================
def carica_database_nativo():
 colonne = [
 "progressivo", "Data contatto", "Ora contatto", "Cognome Titolare", "Nome Titolare", 
 "data presunta di Arrivo", "data presunta di Partenza", "Numero Ospiti", "Nominativi Ospiti", 
 "adulti", "minori", "Email", "Portale di provenienza", "Note aggiuntive", 
 "Cane (Razza/Taglia/Nome)", "Compleanni Gruppo", "Onomastici Gruppo", "Esito"
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
    colonne_visibili = [
        "progressivo", "Data contatto", "Ora contatto", "Cognome Titolare", 
        "Nome Titolare", "data presunta di Arrivo", "Portale di provenienza", "Esito"
    ]
    colonne_presenti = [c for c in colonne_visibili if c in df.columns]
    st.dataframe(df[colonne_presenti], use_container_width=True, hide_index=True)
    st.write("🔍 **Apertura rapida scheda per modifica:**")
    lista_id = [str(r.get('progressivo', '')) for r in lista_righe]
    id_scelto = st.selectbox("Seleziona il numero di riga del cliente che vuoi modificare:", [""] + lista_id, key="selettore_rapido_tabella")
    if id_scelto:
        st.session_state["id_da_modificare"] = str(id_scelto)
        st.success(f"👍 Record #{id_scelto} pronto! Clicca sulla scheda 'Gestione/Modifica Contatto' in alto per aprirlo.")
        st.rerun()

# =========================================================================
# STRUTTURA MENU ORIZZONTALE E DASHBOARD KPI
# =========================================================================
tab_dashboard, tab_archivio, tab_marketing, tab_gestione = st.tabs([
    "📊 CEO Dashboard", "📋 Archivio Ospiti", "🎯 Marketing Iper-Target", "➕ Gestione/Modifica Contatto"
])

colonne, righe = carica_database_nativo()

with tab_dashboard:
    st.subheader("📊 Andamento Business e KPI della Stagione")
    totale_contatti = len(righe)
    confermate = sum(1 for r in righe if "✅ confermata" in str(r.get("Esito", "")).lower().strip())
    pet_friendly = sum(1 for r in righe if str(r.get("Cane (Razza/Taglia/Nome)", "")).strip() and str(r.get("Cane (Razza/Taglia/Nome)", "")).lower() not in ["no", "da chiedere", "none", ""])
    
    lista_giorni_anticipo = []
    for r in righe:
        data_c = str(r.get("Data contatto", "")).strip()
        data_a = str(r.get("data presunta di Arrivo", "")).strip()
        if data_c and data_a:
            data_c_pulita = data_c.replace("-", "/")
            data_a_pulita = data_a.replace("-", "/")
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
        lista_filtrata = [r for r in righe if str(r.get("Cane (Razza/Taglia/Nome)", "")).strip() and str(r.get("Cane (Razza/Taglia/Nome)", "")).lower() not in ["no", "da chiedere", "none", ""]]
        lista_da_profilare = [r for r in righe if "da chiedere" in str(r.get("Cane (Razza/Taglia/Nome)", "")).lower()]
        if lista_filtrata:
            st.success(f"🐾 Trovati {len(lista_filtrata)} clienti con animali già profilati nel database!")
            mostra_tabella_pulita(lista_filtrata)
            st.subheader("📋 Copia Rapida Contatti per Campagne 2027")
            emails_filtrate = [str(r.get("Email", "")).strip() for r in lista_filtrata if str(r.get("Email", "")).strip()]
            st.info("💡 Ricorda di inserire il codice CIN obbligatorio nelle tue comunicazioni: IT075066C200054604")
            st.text_area("Incolla questa lista nel campo 'CCN' della tua e-mail per l'invio massivo:", value="; ".join(emails_filtrate), height=70)
        else:
            st.info("Nessun cliente con animali già profilato trovato all'interno del database.")
        if lista_da_profilare:
            st.markdown("---")
            st.warning(f"⚠️ Ci sono {len(lista_da_profilare)} contatti caldi a cui devi ancora chiedere Razza e Nome del cane!")
            with st.expander("🔍 Visualizza l'elenco dei contatti da profilare subito:"):
                for cp in lista_da_profilare:
                    st.write(f"- **{cp.get('Nome Titolare', '')} {cp.get('Cognome Titolare', '')}** ({cp.get('Email', '')}) — Arrivo: {cp.get('data presunta di Arrivo', '')} | Nota: {cp.get('Note aggiuntive', '')[:50]}...")
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
        ora_contatto = st.text_input("Ora del contatto (es. 12:15):", value="")
        check_cognome = st.text_input("Inserisci Cognome per controllo storico rapido:", value="")
        if st.button("Analizza ed Estrai Automaticamente"):
            st.success("Funzione estrattore simulata con successo!")
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
                prog = str(r.get("progressivo", "")).lower()
                cognome = str(r.get("Cognome Titolare", "")).lower()
                email = str(r.get("Email", "")).lower()
                note = str(r.get("Note aggiuntive", "")).lower()
                if (chiave_ricerca == prog or chiave_ricerca in cognome or chiave_ricerca in email or chiave_ricerca in note):
                    riga_trovata = r
                    break
            if riga_trovata:
                cognome_target = str(riga_trovata.get("Cognome Titolare", "")).lower()
                email_target = str(riga_trovata.get("Email", "")).lower()
                for r in righe:
                    if (cognome_target and str(r.get("Cognome Titolare", "")).lower() == cognome_target) or (email_target and str(r.get("Email", "")).lower() == email_target):
                        storico_cliente.append(r)
        if riga_trovata:
            st.success(f"Scheda Ospite Rilevata: Record #{riga_trovata.get('progressivo')} — {riga_trovata.get('Nome Titolare')} {riga_trovata.get('Cognome Titolare')}")
            col_sinistra, col_destra = st.columns(2)
            with col_sinistra:
                nuovo_cognome = st.text_input("Cognome Titolare:", riga_trovata.get("Cognome Titolare"))
                nuovo_nome = st.text_input("Nome Titolare:", riga_trovata.get("Nome Titolare"))
                nuovo_arrivo = st.text_input("Data Arrivo:", riga_trovata.get("data presunta di Arrivo"))
                nuovo_partenza = st.text_input("Data Partenza:", riga_trovata.get("data presunta di Partenza"))
                nuovo_nominativi = st.text_area("Nominativi Completi Ospiti del Gruppo (Mappatura Arrivi):", riga_trovata.get("Nominativi Ospiti", ""))
            with col_destra:
                nuovo_email = st.text_input("Email Titolare:", riga_trovata.get("Email"))
                nota_per_tel = riga_trovata.get("Note aggiuntive", "")
                match_tel_iniziale = re.search(r'(?:Telefono|Tel|tel|Telefono:)\s*([0-9\+\s]{8,15})', nota_per_tel)
                tel_iniziale = match_tel_iniziale.group(1).strip() if match_tel_iniziale else ""
                nuovo_telefono = st.text_input("Telefono / cellulare:", value=tel_iniziale)
                nuovo_cane = st.text_input("Cane (Razza/Taglia/Nome):", riga_trovata.get("Cane (Razza/Taglia/Nome)", ""))
                nuovo_esito = st.selectbox("Esito Prenotazione:", ["📋 Lista attesa", "🔄 In corso", "✅ Confermata", "❌ Cancellata"], index=["📋 Lista attesa", "🔄 In corso", "✅ Confermata", "❌ Cancellata"].index(riga_trovata.get("Esito")) if riga_trovata.get("Esito") in ["📋 Lista attesa", "🔄 In corso", "✅ Confermata", "❌ Cancellata"] else 0)

            st.markdown("---")
            st.subheader("🎂 Anagrafica Ospiti per Campagne di Fidelizzazione")
            st.caption("Compila questi spazi durante le operazioni di check-in per memorizzare le leve di marketing diretto.")
            col_bday, col_onomastico = st.columns(2)
            with col_bday:
                nuovo_compleanni = st.text_area("Date dei Compleanni (Nome + Giorno/Mese):", value=riga_trovata.get("Compleanni Gruppo", ""), help="Es: Marco (12/05) - Maria (24/10)")
            with col_onomastico:
                nuovo_onomastici = st.text_area("Date degli Onomastici (Nome + Giorno/Mese):", value=riga_trovata.get("Onomastici Gruppo", ""), help="Es: San Marco (25/04) - Sant Anna (26/07)")
            nuove_note = st.text_area("Note Aggiuntive e Dettagli Soggiorno:", value=riga_trovata.get("Note aggiuntive", ""), height=100)
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
                    st.markdown(f'<a href="{link_mail}"><button style="background-color:#0078d4;color:white;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;font-weight:bold;">📧 APRI E COMPILA EMAIL AUTOMATICA</button></a>', unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Impossibile generare l'email: indirizzo e-mail non presente per questo ospite.")

            if st.button("💾 Salva Modifiche nel Database"):
                riga_trovata["Cognome Titolare"] = nuovo_cognome
                riga_trovata["Nome Titolare"] = nuovo_nome
                riga_trovata["data presunta di Arrivo"] = nuovo_arrivo
                riga_trovata["data presunta di Partenza"] = nuovo_partenza
                riga_trovata["Nominativi Ospiti"] = nuovo_nominativi
                riga_trovata["Email"] = nuovo_email
                riga_trovata["Cane (Razza/Taglia/Nome)"] = nuovo_cane
                riga_trovata["Compleanni Gruppo"] = nuovo_compleanni
                riga_trovata["Onomastici Gruppo"] = nuovo_onomastici
                riga_trovata["Note aggiuntive"] = nuove_note
                riga_trovata["Esito"] = nuovo_esito
                salva_database_nativo(colonne, righe)
                st.success("Modifiche salvate con successo in database_ospiti.csv!")
                st.session_state["id_da_modificare"] = ""
                st.rerun()
            st.markdown("---")
            st.subheader("📜 Cronologia Storica dei Soggiorni del Cliente")
            mostra_tabella_pulita(storico_cliente)
        elif chiave_ricerca:
            st.warning("Nessun ospite trovato con i criteri inseriti.")
