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
                        if riga_trovata:
            # ... [Codice di interfaccia Streamlit (st.columns, input, selezioni, invio messaggi) omesso per brevità] ...
            # ... [Gestione di salvataggio modifiche e storico] ...
            
            # --- SEZIONE SALVATAGGIO ---
            if st.button("💾 Salva Modifiche nel Database"):
                # Aggiornamento campi base
                riga_trovata["Cognom e"] = nuovo_cognome
                riga_trovata["Nom e"] = nuovo_nome
                riga_trovata["data presunta di Arriv o"] = nuovo_arrivo
                riga_trovata["data presunta di Partenz a"] = nuovo_partenza
                riga_trovata["Emai l"] = nuovo_email
                riga_trovata["Cane (Razza/Taglia)"] = nuovo_cane
                riga_trovata["Esit o"] = nuovo_esito
                
                # Formattazione e salvataggio note
                testo_fidelizzazione = f" [Compleanni: {nuovo_compleanni.strip()}]" if nuovo_compleanni.strip() else ""
                testo_fidelizzazione += f" [Onomastici: {nuovo_onomastici.strip()}]" if nuovo_onomastici.strip() else ""
                testo_fidelizzazione += f" [Ospiti: {nuovo_nominativi.strip()}]" if nuovo_nominativi.strip() else ""
                
                riga_trovata["Note aggiuntiv e"] = nuove_note + testo_fidelizzazione
                
                salva_database_nativo(colonne, righe)
                st.success("🎯 Dati familiari e scadenze salvati con successo!")
                st.session_state["id_da_modificare"] = ""
                st.rerun()
                
            st.markdown("---")
            st.subheader("📜 Cronologia Storica dei Soggiorni del Cliente")
            mostra_tabella_pulita(storico_cliente)
        elif chiave_ricerca:
            st.warning("Nessun ospite trovato con i criteri inseriti.")
