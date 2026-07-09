import streamlit as st
import pandas as pd
import re
import os
from datetime import datetime

# Configurazione della pagina Streamlit
st.set_page_config(page_title="CRM - A Casa di Amici 2026", layout="wide", page_icon="🏨")
st.title("🏨 CRM Gestionale Istituzionale - A Casa di Amici (2026)")
st.markdown("---")

# Creazione fisica del file database CSV se non presente nella cartella di lavoro
if not os.path.exists("database_ospiti.csv"):
    with open("database_ospiti.csv", "w", encoding="utf-8") as f:
        f.write("ID,Data Contatto,Ora Contatto,Lead Time,Data Inserimento,Nome Ospite,Data Arrivo,Data Partenza,Notti,Ospiti Totali,Alloggio Selezionato,Adulti,Minori,Email,Portale Origine,Presenza Cane,Tariffa Totale,Tassa Soggiorno,Acconto Versato,Saldo da Pagare,Metodo Pagamento,Stato Prenotazione,Note Commerciali\n")

# Calcolo ID incrementale per il nuovo record
prossimo_id = 1
if os.path.exists("database_ospiti.csv"):
    try:
        df_id = pd.read_csv("database_ospiti.csv", encoding="utf-8")
        if not df_id.empty:
            prossimo_id = int(df_id.iloc[:, 0].max()) + 1
    except:
        prossimo_id = 1

# Definizione dei pannelli di navigazione
tab_inserimento, tab_ricerca = st.tabs(["📥 Inserimento Veloce e Screening AI", "🔍 Centrale di Ricerca e Archivio Storico"])

with tab_inserimento:
    st.subheader("📋 Screening AI: Incolla la notifica o la scheda del portale")
    testo_grezzo_portale = st.text_area("Incolla qui il testo integrale ricevuto:", height=250, key="ta_notifica_grezza")

    if testo_grezzo_portale:
        testo_pulito = testo_grezzo_portale.strip()
        data_contatto_str = datetime.now().strftime("%d/%m/%Y")

        # --- MOTORE DI ESTRAZIONE ANAGRAFICA ED ELEMENTI CHIAVE (RegEx) ---
        nome_match = re.search(r'(?:Nome|Ospite|Cliente|Gentile)\s*:?\s*([A-Za-zÀ-ú\s]+)', testo_pulito, re.IGNORECASE)
        estratto_nome = nome_match.group(1).strip() if nome_match else "Ospite"
        if len(estratto_nome) > 40: estratto_nome = estratto_nome[:40].strip()

        portale_match = re.search(r'(?:LovelyITALIA|Ultimissimo\s*Minuto|Sito|Direct|Booking|Airbnb)', testo_pulito, re.IGNORECASE)
        estratto_portale = portale_match.group(0).strip() if portale_match else "Richiesta Diretta"

        tel_match = re.search(r'(?:Telefono|Tel\.?|Cell\.?)\s*:?\s*([\+\d\s\-]+)', testo_pulito, re.IGNORECASE)
        estratto_tel = tel_match.group(1).strip() if tel_match else "nd"

        # --- RILEVAMENTO DEI PARTECIPANTI (Adulti e Minori) ---
        adulti_match = re.search(r'(\d+)\s*(?:adulti|adulto)', testo_pulito, re.IGNORECASE)
        estratto_adulti = int(adulti_match.group(1)) if adulti_match else 2

        minori_match = re.search(r'(\d+)\s*(?:bambini|bambino|minori|minore|ragazzi|ragazzo)', testo_pulito, re.IGNORECASE)
        estratto_minori = int(minori_match.group(1)) if minori_match else 0
        estratto_ospiti_tot = estratto_adulti + estratto_minori

        dettaglio_eta = ""
        eta_match = re.findall(r'(?:età|anni)\s*:?\s*(\d+)', testo_pulito, re.IGNORECASE)
        if eta_match: dettaglio_eta = f"Età minori rilevate: {', '.join(eta_match)}"

        # --- ASSOCIAZIONE AUTOMATICA TIPOLOGIA ALLOGGIO ---
        estratto_alloggio_selezionato = "Struttura Generica"
        alloggi_mappa = {
            "Girasole": ["girasole"], "Lucy": ["pajara", "lucy"], "Glicine": ["glicine"],
            "Tulipano": ["tulipano"], "Margherita": ["margherita"], "Buganville": ["buganville"],
            "Marina": ["marina"], "Lucia": ["casale", "lucia"], "Lido Marini": ["lido marini"]
        }
        for nome_alloggio, parole_chiave in alloggi_mappa.items():
            if any(p_ch in testo_pulito.lower() for p_ch in parole_chiave):
                estratto_alloggio_selezionato = nome_alloggio
                break

        date_trovate = re.findall(r'(\d{1,2}/\d{1,2}/\d{4})', testo_pulito)
        
        # --- ESTRAZIONE EMAIL INTELLIGENTE CON SCUDO AZIENDALE E PERSONALE ESTESO ---
        tutte_le_email = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', testo_pulito)
        email_da_escludere = [
            "vacanze@acasadiamici.info", "info@acasadiamici.info",
            "postmaster@acasadiamici.info", "depietromarco65@gmail.com"
        ]
        email_filtrate = [
            email for email in tutte_le_email 
            if email.lower().strip() not in [e.lower().strip() for e in email_da_escludere]
        ]

        if email_filtrate:
            estratto_email = email_filtrate[0].strip()
        else:
            estratto_email = "nd"
            
        num_tel_visivo = estratto_tel
        # ==============================================================================
        # ===== BLOCCO I: CONTENUTO TAB 2 - SCRITTURA RECORD E LOGISTICA (PARTE 4) =====
        # ==============================================================================
        if len(date_trovate) >= 2:
            d_arr, d_part = date_trovate[-2], date_trovate[-1]
            
            def _formatta_data_stringa(data_grezza):
                d_str = str(data_grezza).strip()
                if "/" in d_str:
                    parti = d_str.split("/")
                    if len(parti) == 3:
                        try:
                            giorno = f"{int(parti[0]):02d}"
                            mese = f"{int(parti[1]):02d}"
                            anno = parti[2]
                            return f"{giorno}/{mese}/{anno}"
                        except ValueError:
                            return d_str
                return d_str

            estratto_arrivo = _formatta_data_stringa(d_arr)
            estratto_partenza = _formatta_data_stringa(d_part)
            
            try:
                dt_contatto = datetime.strptime(data_contatto_str, "%d/%m/%Y")
                dt_arrivo = datetime.strptime(estratto_arrivo, "%d/%m/%Y")
                lead_time = max(0, (dt_arrivo - dt_contatto).days)
            except: 
                lead_time = 0
        else:
            estratto_arrivo = "nd"
            estratto_partenza = "nd"
            lead_time = 0
                
        localita_match = re.search(r'(?:Localita\'?\s*richiesta\s*:?)\s*([A-Za-zÀ-ú\s]+(?:dintorni)?)', testo_pulito, re.IGNORECASE)
        estratto_localita = localita_match.group(1).strip() if localita_match else "nd"
        
        cane_match = re.search(r'(\d*\s*(?:cane|cani|gatto|gatti|animale|animali)\s*(?:taglia|piccola|media|grande|nd|\w+)*)', testo_pulito, re.IGNORECASE)
        estratto_cane = cane_match.group(1).strip() if cane_match else "nd"
        
        ora_attuale = datetime.now().strftime("%H:%M")

        # ==============================================================================
        # ===== CONTROLLO E RECUPERO DATI MANCANTI (EMAIL E TELEFONO) =====
        # ==============================================================================
        if estratto_email == "nd" or num_tel_visivo == "Rilevabile nelle note" or num_tel_visivo == "nd" or num_tel_visivo == "":
            st.warning("⚠️ **Attenzione:** Alcuni dati di contatto fondamentali non sono stati rilevati automaticamente.")
            
            col_input1, col_input2 = st.columns(2)
            with col_input1:
                if estratto_email == "nd" or estratto_email == "":
                    estratto_email = st.text_input("📧 Inserisci l'Email dell'ospite:", key="manual_email").strip()
                else:
                    st.success(f"📧 Email rilevata: {estratto_email}")
                    
            with col_input2:
                if num_tel_visivo == "Rilevabile nelle note" or num_tel_visivo == "nd" or num_tel_visivo == "":
                    num_tel_visivo = st.text_input("📞 Inserisci il Telefono dell'ospite:", key="manual_tel").strip()
                else:
                    st.success(f"📞 Telefono rilevato: {num_tel_visivo}")
            
            estratto_tel = num_tel_visivo

        note_pulite = f"Telefono: {estratto_tel}. Ricevuto tramite {estratto_portale}. Localita richiesta: {estratto_localita}."
        if 'dettaglio_eta' in locals() and dettaglio_eta: 
            note_pulite += f" Segmentazione marketing: {dettaglio_eta}."
        note_pulite = note_pulite.replace(",", " -")

        # Controllo blocco di sicurezza prima di sbloccare il modulo di salvataggio
        if estratto_email == "" or estratto_email == "nd":
            st.error("🛑 Impossibile procedere: L'indirizzo Email è obbligatorio per generare la comunicazione e salvare il record.")
        elif num_tel_visivo == "" or num_tel_visivo == "nd":
            st.error("🛑 Impossibile procedere: Il numero di telefono è obbligatorio per la gestione delle schede contatto.")
        else:
            st.markdown("---")
            
            # ==============================================================================
            # ===== BLOCCO J: CONTENUTO TAB 2 - SALVATAGGIO FISICO ED EMAIL RIGIDA =====
            # ==============================================================================
            stato_prenotazione = st.radio(
                "🎯 Azione commerciale per questa richiesta:",
                ["Non Disponibile (Lista d'attesa)", "Accetta e Conferma (Prenotazione Diretta)"],
                index=0,
                key="radio_stato_prenotazione"
            )

            email_esistenti = []
            if os.path.exists("database_ospiti.csv"):
                try:
                    with open("database_ospiti.csv", "r", encoding="utf-8") as f:
                        for line in f:
                            parti_linea = line.split(",")
                            if len(parti_linea) > 13:
                                email_esistenti.append(parti_linea[13].lower().strip())
                except:
                    pass

            if estratto_email.lower() in email_esistenti and estratto_email != "nd":
                st.warning(f"⚠️ VIOLAZIONE REGOLA 1: L'email '{estratto_email}' è già presente nel database aziendale.")
            else:
                if st.button("💾 Conferma Scrittura Database e Genera Comunicazione"):
                    stato_csv = "Confermato" if "Conferma" in stato_prenotazione else "Lista d'attesa"
                    
                    nuovo_record = f"{prossimo_id},{data_contatto_str},{ora_attuale},{lead_time},nd,{estratto_nome},{estratto_arrivo},{estratto_partenza},nd,{estratto_ospiti_tot},nd,{estratto_adulti},{estratto_minori},{estratto_email},{estratto_portale},{estratto_cane},nd,nd,nd,nd,nd,{stato_csv},{note_pulite}\n"
                    
                    try:
                        with open("database_ospiti.csv", "a", encoding="utf-8") as f:
                            f.write(nuovo_record)
                        st.success(f"✅ Record inserito nel file CSV! ID Assegnato: **{prossimo_id}** | Stato d'esercizio: **{stato_csv}**")
                        
                        c_sh1, c_sh2 = st.columns(2)
                        with c_sh1:
                            st.markdown("**📋 Campi Mappati ed Estratti:**")
                            st.write(f"• **Ospite:** {estratto_nome} | **Email:** {estratto_email}")
                            st.write(f"• **Date:** {estratto_arrivo} - {estratto_partenza}")
                            st.write(f"• **Alloggio:** {estratto_alloggio_selezionato} | **Origine:** {estratto_portale}")
                            st.write(f"• **Pax:** {estratto_adulti} Adulti + {estratto_minori} Minori | **Animali:** {estratto_cane}")
                        
                        with c_sh2:
                            riga_geo = ""
                            loc_bassa = estratto_localita.lower()
                            if "pali" not in loc_bassa and loc_bassa != "nd" and loc_bassa != "":
                                riga_geo = f"In merito alla sua richiesta per {estratto_localita}, desideriamo innanzitutto precisare che la nostra struttura si trova a Torre Pali (Marina di Salve), a pochissimi minuti di auto dalla località da lei indicata e in una posizione ideale per godersi il mare del Salento. "
                            
                            # --- SCENARIO 1: PRENOTAZIONE DIRETTA CONFERMATA ---
                            if stato_csv == "Confermato":
                                st.markdown("**✉️ Risposta di Conferma Generata (Formula Fiduciaria):**")
                                conf_A = (
                                    f"Gentile {estratto_nome},\n\n"
                                    f"La ringraziamo per aver espresso il suo interesse verso la nostra struttura e per aver scelto di convertire la richiesta proveniente dal portale {estratto_portale} in una prenotazione diretta sul nostro sito ufficiale.\n\n"
                                    f"{riga_geo}Siamo lieti di confermare ufficialmente il vostro soggiorno presso l'\"{estratto_alloggio_selezionato}\" per il periodo indicato dal {estratto_arrivo} al {estratto_partenza}.\n\n"
                                )
                                blocco_C_fiduciario = "Le ricordiamo che la nostra formula fiduciaria è pensata proprio per instaurare un rapporto di trasparenza e fiducia reciproca con l'ospite, eliminando ogni preoccupazione. Per questo motivo, la nostra politica non prevede l'invio di acconti o caparre: il pagamento avverrà direttamente in struttura al vostro arrivo. Questa scelta nasce per tutelarvi dal rischio di truffe online e per garantirvi che nessuno della nostra struttura vi contatterà mai via email o telefono per richiedere denaro o pagamenti anticipati prima del vostro soggiorno.\n\n"
                                blocco_D_chiusura = "Restiamo a sua completa disposizione con l'augurio che possa trovare un soggiorno adeguato alle sue aspettative al fine di passare una splendida vacanza nel Salento.\n\n"
                                blocco_E_firma = "Cordiali saluti,\n\nMarco De Pietro - CEO \"A Casa di Amici\"\nTenuta Salento: Sp 206 Località Torre Pali, 73050 Salve (LE)\nSito Web: https://acasadiamici.info\nContatto Assistenza Direct WhatsApp: https://wa.me"
                                
                                st.code(conf_A + blocco_C_fiduciario + blocco_D_chiusura + blocco_E_firma, language="text")
                            
                            # --- SCENARIO 2: STRUTTURA AL COMPLETO (LISTA D'ATTESA RIGIDA) ---
                            else:
                                st.markdown("**✉️ Risposta Istituzionale Generata (Struttura Rigida):**")
                                parte_A = (
                                    f"Gentile {estratto_nome},\n\n"
                                    f"La ringraziamo per aver espresso il suo interesse verso la nostra struttura per le sue vacanze in Puglia attraverso la richiesta inviata dal portale {estratto_portale}.\n\n"
                                    f"{riga_geo}Desideriamo informarla chiaramente che per il periodo indicato ({estratto_arrivo} - {estratto_partenza}) la nostra struttura è interamente al completo. Abbiamo tuttavia provveduto a inserire i suoi dati nel nostro database in \"lista d'attesa\" per la gestione di eventuali cancellazioni improvvise. Ci teniamo a esplicitare subito che, trattandosi di alta stagione, la disdetta è da considerarsi un evento \"molto improbabile\".\n\n"
                                )
                                parte_B = "Sperando di avervi come nostri ospiti in futuro, abbiamo il piacere di riservarvi un buono di benvenuto con uno sconto del 15% valido per un soggiorno da consumare in qualsiasi periodo dell'anno in corso (2026) o degli anni successivi, vi basterà ricordarci di aver perduto un'occasione di prenotare da noi per mancanza di disponibilità per ottenere lo sconto per una prenotazione diretta sul nostro sito https://acasadiamici.info usufruendo della nostra formula fiduciaria.\n\n"
                                parte_C = "Le ricordiamo che la nostra formula fiduciaria è pensata proprio per instaurare un rapporto di trasparenza e fiducia reciproca con l'ospite, eliminando ogni preoccupazione. Per questo motivo, la nostra politica non prevede l'invio di acconti o caparre: il pagamento avverrà direttamente in struttura al vostro arrivo. Questa scelta nasce per tutelarvi dal rischio di truffe online e per garantirvi che nessuno della nostra struttura vi contatterà mai via email o telefono per richiedere denaro o pagamenti anticipati prima del vostro soggiorno.\n\n"
                                parte_D = "Restiamo a sua completa disposizione con l'augurio che, se decidesse di scegliere un'altra soluzione, possa trovare un soggiorno adeguato alle sue aspettative al fine di passare una splendida vacanza nel Salento.\n\n"
                                parte_E = "Cordiali saluti,\n\nMarco De Pietro - CEO \"A Casa di Amici\"\nTenuta Salento: Sp 206 Località Torre Pali, 73050 Salve (LE)\nSito Web: https://acasadiamici.info\nContatto Assistenza Direct WhatsApp: https://wa.me"
                                
                                st.code(parte_A + parte_B + parte_C + parte_D + parte_E, language="text")
                    except Exception as e:
                        st.error(f"Errore tecnico di scrittura sul file CSV: {e}")
# ==============================================================================
# ==================== TAB 3: CENTRALE DI RICERCA ED ARCHIVIO ==================
# ==============================================================================
with tab_ricerca:
    st.subheader("🔍 Filtri di Ricerca Avanzati e Scansione Telefoni")
    
    if os.path.exists("database_ospiti.csv"):
        try:
            df = pd.read_csv("database_ospiti.csv", encoding="utf-8")
        except:
            df = pd.DataFrame()
            
        if not df.empty:
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                chiave_ricerca = st.text_input("✍️ Ricerca per Nome, Email, Telefono o Note:", key="ti_ricerca_scheda").strip().lower()
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
                df_filtrato = df_filtrato[df_filtrato.iloc[:, 5].astype(str).str.lower().str.contains(chiave_ricerca) | df_filtrato.iloc[:, 13].astype(str).str.lower().str.contains(chiave_ricerca) | df_filtrato.iloc[:, 22].astype(str).str.lower().str.contains(chiave_ricerca)]
            
            if not df_filtrato.empty:
                st.success(f"🎯 Corrispondenze trovate: {len(df_filtrato)} record storici.")
                st.dataframe(df_filtrato, use_container_width=True)
                
                index_scelto = st.selectbox("Seleziona l'ospite specifico per vedere i dettagli:", df_filtrato.index, key="sb_ricerca_avanzata")
                riga_scelta = df.loc[index_scelto]
                
                testo_note_riga = str(riga_scelta.iloc[22])
                tel_estratto_match = re.search(r'(?:Telefono|Tel\.?):?\s*([0-9\s\-]+)', testo_note_riga, re.IGNORECASE)
                num_tel_visivo = tel_estratto_match.group(1).strip() if tel_estratto_match else "Rilevabile nelle note"
                
                st.warning(f"📞 Numero di Telefono Ospite: **{num_tel_visivo}**")
                
                # --- COMPOSIZIONE EMAIL RIGIDA DA CENTRALE RICERCA ---
                ospite_nome = riga_scelta.iloc[5] if pd.notna(riga_scelta.iloc[5]) and str(riga_scelta.iloc[5]) != "nd" else "Ospite"
                portale_origine = riga_scelta.iloc[14] if pd.notna(riga_scelta.iloc[14]) and str(riga_scelta.iloc[14]) != "nd" else "nostri sistemi"
                d_arr_s = riga_scelta.iloc[6] if pd.notna(riga_scelta.iloc[6]) else "nd"
                d_part_s = riga_scelta.iloc[7] if pd.notna(riga_scelta.iloc[7]) else "nd"
                
                riga_geo = ""
                if "pali" not in testo_note_riga.lower():
                    riga_geo = "In merito alla sua richiesta, desideriamo innanzitutto precisare che la nostra struttura si trova a Torre Pali (Marina di Salve), a pochissimi minuti di auto dalla località da lei indicata e in una posizione ideale per godersi il mare del Salento. "
                
                parte_A = (
                    f"Gentile {ospite_nome},\n\n"
                    f"La ringraziamo per aver espresso il suo interesse verso la nostra struttura per le sue vacanze in Puglia attraverso la richiesta inviata dal portale {portale_origine}.\n\n"
                    f"{riga_geo}Desideriamo informarla chiaramente che per il periodo indicato ({d_arr_s} - {d_part_s}) la nostra struttura è interamente al completo. Abbiamo tuttavia provveduto a inserire i suoi dati nel nostro database in \"lista d'attesa\" per la gestione di eventuali cancellazioni improvvise. Ci teniamo a esplicitare subito che, trattandosi di alta stagione, la disdetta è da considerarsi un evento \"molto improbabile\".\n\n"
                )
                
                parte_B = "Sperando di avervi come nostri ospiti in futuro, abbiamo il piacere di riservarvi un buono di benvenuto con uno sconto del 15% valido per un soggiorno da consumare in qualsiasi periodo dell'anno in corso (2026) o degli anni successivi, vi basterà ricordarci di aver perduto un'occasione di prenotare da noi per mancanza di disponibilità per ottenere lo sconto per una prenotazione diretta sul nostro sito https://acasadiamici.info usufruendo della nostra formula fiduciaria.\n\n"
                parte_C = "Le ricordiamo che la nostra formula fiduciaria è pensata proprio per instaurare un rapporto di trasparenza e fiducia reciproca con l'ospite, eliminando ogni preoccupazione. Per questo motivo, la nostra politica non prevede l'invio di acconti o caparre: il pagamento avverrà direttamente in struttura al vostro arrivo. Questa scelta nasce per tutelarvi dal rischio di truffe online e per garantirvi che nessuno della nostra struttura vi contatterà mai via email o telefono per richiedere denaro o pagamenti anticipati prima del vostro soggiorno.\n\n"
                parte_D = "Restiamo a sua completa disposizione con l'augurio che, se decidesse di scegliere un'altra soluzione, possa trovare un soggiorno adeguato alle sue aspettative al fine di passare una splendida vacanza nel Salento.\n\n"
                parte_E = "Cordiali saluti,\n\nMarco De Pietro - CEO \"A Casa di Amici\"\nTenuta Salento: Sp 206 Località Torre Pali, 73050 Salve (LE)\nSito Web: https://acasadiamici.info\nContatto Assistenza Direct WhatsApp: https://wa.me"
                
                st.markdown("### ✉️ Modello E-mail Istituzionale Invariabile:")
                st.code(parte_A + parte_B + parte_C + parte_D + parte_E, language="text")
            else:
                st.warning("❌ Nessun record corrispondente trovato con i parametri digitati.")
        else:
            st.info("📂 Il database CSV è attualmente vuoto. Incolla la tua prima richiesta nel Tab precedente.")


