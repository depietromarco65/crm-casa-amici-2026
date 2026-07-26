import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione iniziale della pagina
st.set_page_config(page_title="CRM A Casa di Amici", layout="wide", initial_sidebar_state="expanded")

st.title("? Pannello di Controllo CRM - A Casa di Amici")
st.caption("CEO Management System — Marco De Pietro")

# Funzione per caricare il database in sicurezza
def carica_database():
    try:
        df = pd.read_csv("https://github.com/depietromarco65/crm-casa-amici-2026/blob/main/database_ospiti.csv")
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        # Se il file non esiste, crea una struttura base con le tue colonne
        colonne = ["numero progressivo", "Data del contatto", "Cognome", "Nome", "Nominativi Ospiti", 
                   "data presunta di Arrivo", "data presunta di Partenza", "Numero Ospiti", "adulti", 
                   "minori", "Email", "Portale di provenienza", "Note aggiuntive", "Cane (Razza/Taglia)", "Esito"]
        return pd.DataFrame(columns=colonne)

df = carica_database()

# Logica di calcolo automatico del Lead Time
def calcola_lead_time(row):
    try:
        contatto = pd.to_datetime(row['Data del contatto'], format='%d/%m/%Y')
        arrivo = pd.to_datetime(row['data presunta di Arrivo'], format='%d/%m/%Y')
        return (arrivo - contatto).days
    except:
        return None

if not df.empty:
    df['Lead Time (Giorni)'] = df.apply(calcola_lead_time, axis=1)

# --- CREAZIONE DELLE SCHEDE INTERFACCIA ---
tab1, tab2, tab3, tab4 = st.tabs(["? CEO Dashboard", "? Archivio Ospiti", "? Marketing Iper-Target", "? Nuovo Contatto"])

# --- TAB 1: DASHBOARD STATISTICA ---
with tab1:
    st.header("Andamento Business e KPI")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Totale Contatti Archivio", len(df))
    with c2:
        confermati = len(df[df['Esito'].str.contains('?|Confermata', na=False)])
        st.metric("Prenotazioni Confermate", confermati)
    with c3:
        pet_friendly = len(df[~df['Cane (Razza/Taglia)'].str.lower().str.contains('no|-|nessuno', na=False)])
        st.metric("Clienti Pet-Friendly", pet_friendly)
    with c4:
        lt_medio = df['Lead Time (Giorni)'].mean()
        st.metric("Lead Time Medio (Anticipo)", f"{int(lt_medio) if pd.notna(lt_medio) else 0} Giorni")

# --- TAB 2: ARCHIVIO RICERCABILE ---
with tab2:
    st.header("Ricerca Avanzata e Filtri")
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        cerca_cognome = st.text_input("Cerca per Cognome")
    with f_col2:
        cerca_alloggio = st.text_input("Cerca per Alloggio nelle Note (es. Marina, Girasole)")
    with f_col3:
        filtro_pet = st.checkbox("Mostra solo clienti con Animali")
    
    # Applicazione dei filtri
    df_view = df.copy()
    if cerca_cognome:
        df_view = df_view[df_view['Cognome'].str.contains(cerca_cognome, case=False, na=False)]
    if cerca_alloggio:
        df_view = df_view[df_view['Note aggiuntive'].str.contains(cerca_alloggio, case=False, na=False)]
    if filtro_pet:
        df_view = df_view[~df_view['Cane (Razza/Taglia)'].str.lower().str.contains('no|-|nessuno', na=False)]
        
    st.dataframe(df_view, use_container_width=True)

# --- TAB 3: GENERATORE EMAIL IPER-PERSONALIZZATE ---
with tab3:
    st.header("? Strategia Direct Marketing 2027")
    st.subheader("Seleziona un cliente storico per generare la mail su misura basata sui suoi dati:")
    
    lista_clienti = df[df['Cognome'].notna()]['Cognome'].unique()
    cliente_selezionato = st.selectbox("Scegli il Cognome dell'ospite da ricontattare:", lista_clienti)
    
    if cliente_selezionato:
        riga_cliente = df[df['Cognome'] == cliente_selezionato].iloc[0]
        note = str(riga_cliente['Note aggiuntive']).lower()
        cane = str(riga_cliente['Cane (Razza/Taglia)'])
        nome_ospite = riga_cliente['Nome'] if pd.notna(riga_cliente['Nome']) else ""
        
        st.info(f"**Storico Rilevato:** {riga_cliente['Note aggiuntive']}")
        
        # Algoritmo di Intelligenza Artificiale locale per la scelta del gancio commerciale
        oggetto_mail = "Un saluto da Torre Pali - A Casa di Amici"
        corpo_mail = ""
        
        if "burraco" in note or "machiavelli" in note:
            corpo_mail = f"Gentile {cliente_selezionato},\n\nle carte sul tavolo a Torre Pali sono già pronte per le nostre sfide a Burraco e Machiavelli fino a tardi! Volevamo ricordarLe che i calendari per la nuova stagione si stanno aprendo e ci farebbe immenso piacere avervi nuovamente nostri ospiti nel vostro Monolocale Marina del cuore.\n\nContattandoci direttamente, la Vostra tariffa speciale senza commissioni è bloccata."
        elif "barboncino" in note.lower() or "maltese" in note.lower():
            corpo_mail = f"Gentile {cliente_selezionato},\n\nil nostro prato verde di 15.000 mq è pronto per le corse del Vostro splendido {cane}! Sappiamo quanto sia importante la sicurezza dei nostri amici a quattro zampe, e le nostre recinzioni sono pronte ad accogliervi a Torre Pali per una nuova estate di totale relax."
        elif "gatto" in note:
            corpo_mail = f"Gentile {cliente_selezionato},\n\nle nostre ville interamente recintate e sicure sono pronte ad accogliere nuovamente la Vostra famiglia e il Vostro gatto per una vacanza a zero stress logistico a pochissimi minuti dalle spiagge di sabbia di Torre Pali."
        else:
            corpo_mail = f"Gentile {nome_ospite} {cliente_selezionato},\n\nè stato un vero piacere avervi ospiti presso la nostra tenuta 'A Casa di Amici' a Torre Pali (Marina di Salve). Volevamo informarLe in anteprima che stiamo aprendo le prenotazioni dirette per la nuova stagione, offrendo tariffe esclusive ed evitando le commissioni dei portali online."

        st.subheader("? Mail personalizzata generata (Pronta da copiare):")
        st.text_input("Oggetto dell'email:", oggetto_mail)
        st.text_area("Corpo del messaggio (Senza blocchi, seleziona tutto e copia):", corpo_mail, height=250)

# --- TAB 4: INSERIMENTO RAPIDO DATI ---
with tab4:
    st.header("? Aggiungi un nuovo contatto al volo")
    with st.form("nuovo_ospite_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            data_c = st.text_input("Data Contatto (GG/MM/AAAA)", datetime.now().strftime("%d/%m/%Y"))
            cognome = st.text_input("Cognome")
            nome = st.text_input("Nome")
            ospiti_nomi = st.text_area("Nominativi completi ospiti (Divisi da +)")
            data_arr = st.text_input("Data Arrivo (GG/MM/AAAA)")
            data_par = st.text_input("Data Partenza (GG/MM/AAAA)")
        with col_b:
            num_o = st.number_input("Numero Ospiti Totali", min_value=1, value=2)
            ad = st.number_input("Adulti", min_value=1, value=2)
            mn = st.number_input("Minori", min_value=0, value=0)
            email = st.text_input("Email")
            portale = st.selectbox("Portale", ["Sito Diretto", "UltMin", "Lovely", "Booking", "Vrbo", "Airbnb"])
            cane_razza = st.text_input("Cane (Razza/Taglia)", "No")
            esito = st.selectbox("Esito iniziale", ["? In sospeso", "? Confermata", "? Lista attesa", "? Non disponibile"])
            note_agg = st.text_area("Note aggiuntive (Evita l'uso di virgole)")
            
        submitted = st.form_submit_button("Salva ed Esporta nel CSV")
        
        if submitted:
            nuovo_id = len(df) + 1
            nuova_riga = {
                "numero progressivo": nuovo_id, "Data del contatto": data_c, "Cognome": cognome, "Nome": nome,
                "Nominativi Ospiti": ospiti_nomi, "data presunta di Arrivo": data_arr, "data presunta di Partenza": data_par,
                "Numero Ospiti": num_o, "adulti": ad, "minori": mn, "Email": email, "Portale di provenienza": portale,
                "Note aggiuntive": note_agg, "Cane (Razza/Taglia)": cane_razza, "Esito": esito
            }
            df_nuovo = pd.concat([df, pd.DataFrame([nuova_riga])], ignore_index=True)
            df_nuovo.to_csv("database_ospiti.csv", index=False)
            st.success(f"Ospite registrato con successo con ID progressivo n. {nuovo_id}! Riavvia l'app per aggiornare le tabelle.")
