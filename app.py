# =============================================================================
# CRM CASA DI AMICI 2026
# File: app.py
# Versione: 1.0
# Autore: Marco De Pietro / ChatGPT
# =============================================================================

import streamlit as st
import pandas as pd
import sqlite3
import os
import logging
from pathlib import Path
from datetime import datetime, date, timedelta

# =============================================================================
# CONFIGURAZIONE STREAMLIT
# =============================================================================

st.set_page_config(
    page_title="CRM Casa di Amici",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CARTELLE DEL PROGETTO
# =============================================================================

BASE_DIR = Path(__file__).parent

DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backup"
LOG_DIR = BASE_DIR / "log"
EXPORT_DIR = BASE_DIR / "export"

for directory in [DATA_DIR, BACKUP_DIR, LOG_DIR, EXPORT_DIR]:
    directory.mkdir(exist_ok=True)

DB_FILE = DATA_DIR / "crm.db"
CSV_FILE = DATA_DIR / "database_ospiti.csv"

# =============================================================================
# LOG
# =============================================================================

logging.basicConfig(
    filename=LOG_DIR / "crm.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
# =============================================================================
# COSTANTI CRM
# =============================================================================

CRM_NAME = "CRM Casa di Amici"

VERSION = "1.0"

DATA_RIFERIMENTO = date(2026, 7, 18)

STATI_PRENOTAZIONE = [
    "In corso",
    "Confermata",
    "Lista d'attesa",
    "Richiesta Scaduta",
    "Non Contattabile"
]

PORTALI = [
    "Diretto",
    "Booking",
    "Airbnb",
    "Vrbo",
    "LovelyItalia",
    "UltimissimoMinuto",
    "Traum Ferienwohnungen",
    "Altro"
]

# =============================================================================
# SESSIONE STREAMLIT
# =============================================================================

if "db" not in st.session_state:
    st.session_state.db = None

if "utente" not in st.session_state:
    st.session_state.utente = "Amministratore"

if "pagina" not in st.session_state:
    st.session_state.pagina = "Dashboard"

# =============================================================================
# CONNESSIONE DATABASE SQLITE
# =============================================================================

def get_connection():

    conn = sqlite3.connect(DB_FILE)

    conn.row_factory = sqlite3.Row

    return conn
    # =============================================================================
# CREAZIONE DATABASE
# =============================================================================

def inizializza_database():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ospiti (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            data_contatto TEXT,
            ora_contatto TEXT,
            lead_time INTEGER,

            cognome TEXT,
            nome TEXT,

            arrivo TEXT,
            partenza TEXT,

            alloggio_assegnato TEXT,

            ospiti_totali INTEGER,
            note_alloggio TEXT,

            adulti INTEGER,
            bambini INTEGER,

            email TEXT,

            canale TEXT,

            prezzo_alloggio REAL,

            fatturato_consolidato REAL,

            caparra REAL,

            tariffa TEXT,

            extra REAL
                        sconto_salvato REAL,

            tassa_soggiorno REAL,

            stato_pratica TEXT,

            recensione_ospite TEXT,

            risposta_struttura TEXT,

            canale_messaggio TEXT,

            stato_messaggio TEXT

        )
    """)

    conn.commit()
    conn.close()

# =============================================================================
# VERIFICA ESISTENZA DATABASE
# =============================================================================

if not DB_FILE.exists():
    inizializza_database()
    logging.info("Database CRM creato.")

# =============================================================================
# CARICAMENTO DATABASE CSV
# =============================================================================

def carica_csv():

    if not CSV_FILE.exists():
        return pd.DataFrame()

    try:

        df = pd.read_csv(
            CSV_FILE,
            encoding="utf-8",
            sep=","
        )

        return df

    except Exception as errore:

        logging.error(f"Errore lettura CSV: {errore}")

        return pd.DataFrame()
        # =============================================================================
# SALVATAGGIO DATABASE CSV
# =============================================================================

def salva_csv(df):

    try:

        df.to_csv(
            CSV_FILE,
            index=False,
            encoding="utf-8-sig"
        )

        logging.info("Database CSV aggiornato.")

        return True

    except Exception as errore:

        logging.error(f"Errore salvataggio CSV: {errore}")

        return False

# =============================================================================
# LETTURA TABELLA SQLITE
# =============================================================================

def leggi_database():

    conn = get_connection()

    try:

        df = pd.read_sql_query(
            "SELECT * FROM ospiti",
            conn
        )

    finally:

        conn.close()

    return df

# =============================================================================
# SCRITTURA DATAFRAME SU SQLITE
# =============================================================================

def salva_database(df):

    conn = get_connection()

    try:

        df.to_sql(
            "ospiti",
            conn,
            if_exists="replace",
            index=False
        )

        conn.commit()
            except Exception as errore:

        logging.error(f"Errore SQLite: {errore}")

    finally:

        conn.close()

# =============================================================================
# SINCRONIZZAZIONE SQLITE → CSV
# =============================================================================

def sincronizza_csv():

    df = leggi_database()

    if len(df) > 0:

        salva_csv(df)

        logging.info("Sincronizzazione SQLite -> CSV completata.")

# =============================================================================
# SINCRONIZZAZIONE CSV → SQLITE
# =============================================================================

def sincronizza_sqlite():

    if not CSV_FILE.exists():
        return

    try:

        df = pd.read_csv(
            CSV_FILE,
            encoding="utf-8"
        )

        salva_database(df)

        logging.info("Sincronizzazione CSV -> SQLite completata.")

    except Exception as errore:

        logging.error(
            f"Errore sincronizzazione: {errore}"
        )

# =============================================================================
# AVVIO CRM
# =============================================================================

sincronizza_sqlite()
# =============================================================================
# DASHBOARD PRINCIPALE
# =============================================================================

def dashboard():

    st.title("🏡 CRM Casa di Amici")

    st.caption(f"Versione {VERSION}")

    df = leggi_database()

    totale_ospiti = len(df)

    if totale_ospiti == 0:

        st.warning("Nessun ospite presente nel database.")

        return

    fatturato = df["fatturato_consolidato"].fillna(0).sum()

    prenotazioni = df["stato_pratica"].fillna("")

    confermate = len(
        df[prenotazioni == "Confermata"]
    )

    in_corso = len(
        df[prenotazioni == "In corso"]
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Ospiti",
        totale_ospiti
    )

    col2.metric(
        "Prenotazioni",
        confermate
    )

    col3.metric(
        "Richieste",
        in_corso
    )

    col4.metric(
        "Fatturato (€)",
        f"{fatturato:,.2f}"
    )
    # =========================================================================
    # EVENTI DEL GIORNO
    # =========================================================================

    oggi = date.today().strftime("%Y-%m-%d")

    arrivi = df[df["arrivo"].astype(str) == oggi]

    partenze = df[df["partenza"].astype(str) == oggi]

    c1, c2 = st.columns(2)

    c1.success(f"🟢 Arrivi di oggi: {len(arrivi)}")

    c2.info(f"🔵 Partenze di oggi: {len(partenze)}")

    # =========================================================================
    # LEAD DA CONTATTARE
    # =========================================================================

    if "lead_time" in df.columns:

        lead_urgenti = len(
            df[
                (df["lead_time"] <= 2) &
                (df["stato_pratica"] == "In corso")
            ]
        )

        if lead_urgenti > 0:

            st.warning(
                f"⚠️ Sono presenti {lead_urgenti} lead da contattare subito."
            )

    # =========================================================================
    # ULTIME PRENOTAZIONI
    # =========================================================================

    st.subheader("Ultime prenotazioni")

    colonne = [
        "cognome",
        "nome",
        "arrivo",
        "partenza",
        "alloggio_assegnato",
        "stato_pratica"
    ]

    st.dataframe(
        df[colonne].tail(10),
        use_container_width=True,
        hide_index=True
    )
# =============================================================================
# MENU LATERALE
# =============================================================================

def menu_laterale():

    st.sidebar.image(
        "assets/logo.png",
        use_container_width=True
    )

    st.sidebar.title("CRM Casa di Amici")

    pagina = st.sidebar.radio(

        "Seleziona funzione",

        [

            "Dashboard",

            "Ospiti",

            "Prenotazioni",

            "Calendario",

            "Preventivi",

            "Email",

            "WhatsApp",

            "Report",

            "Configurazione"

        ]

    )

    st.session_state.pagina = pagina

    st.sidebar.divider()

    st.sidebar.write(
        f"Utente: {st.session_state.utente}"
    )

    st.sidebar.write(
        datetime.now().strftime("%d/%m/%Y %H:%M")
    )

    return pagina
    # =============================================================================
# GESTIONE OSPITI
# =============================================================================

def pagina_ospiti():

    st.title("👥 Gestione Ospiti")

    df = leggi_database()

    if df.empty:

        st.info("Il database ospiti è vuoto.")

        return

    ricerca = st.text_input(
        "Ricerca (Cognome, Nome, Email)"
    )

    if ricerca.strip() != "":

        filtro = ricerca.lower()

        df = df[
            df["cognome"].astype(str).str.lower().str.contains(filtro) |
            df["nome"].astype(str).str.lower().str.contains(filtro) |
            df["email"].astype(str).str.lower().str.contains(filtro)
        ]

    st.write(f"Ospiti trovati: {len(df)}")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    if st.button("🔄 Aggiorna archivio"):

        sincronizza_sqlite()

        st.success("Archivio aggiornato.")
            st.divider()

    st.subheader("➕ Nuovo Ospite")

    with st.form("nuovo_ospite"):

        cognome = st.text_input("Cognome")

        nome = st.text_input("Nome")

        email = st.text_input("Email")

        telefono = st.text_input("Telefono")

        arrivo = st.date_input("Data Arrivo")

        partenza = st.date_input("Data Partenza")

        alloggio = st.selectbox(

            "Alloggio",

            [
                "",
                "Villa Tulipano",
                "Casale Lucia",
                "Appartamento Girasole",
                "Monolocale Marina",
                "Monolocale Margherita",
                "Monolocale Glicine",
                "Pajara Lucy",
                "Lido Marini Anacleto"
            ]

        )

        salva = st.form_submit_button("Salva Ospite")

    if salva:

        conn = get_connection()

        cur = conn.cursor()
                cur.execute("""

            INSERT INTO ospiti (

                data_contatto,
                ora_contatto,
                cognome,
                nome,
                email,
                arrivo,
                partenza,
                alloggio_assegnato,
                stato_pratica

            )

            VALUES (?,?,?,?,?,?,?,?,?)

        """, (

            date.today().isoformat(),
            datetime.now().strftime("%H:%M"),
            cognome,
            nome,
            email,
            arrivo.isoformat(),
            partenza.isoformat(),
            alloggio,
            "In corso"

        ))

        conn.commit()

        conn.close()

        sincronizza_csv()

        logging.info(
            f"Nuovo ospite inserito: {cognome} {nome}"
        )

        st.success(
            "Ospite registrato correttamente."
        )

        st.rerun()

# =============================================================================
# FINE GESTIONE OSPITI
# =============================================================================
# =============================================================================
# PAGINA PRENOTAZIONI
# =============================================================================

def pagina_prenotazioni():

    st.title("📅 Gestione Prenotazioni")

    df = leggi_database()

    if df.empty:

        st.info("Nessuna prenotazione presente.")

        return

    stati = ["Tutte"] + STATI_PRENOTAZIONE

    filtro = st.selectbox(
        "Filtra per stato",
        stati
    )

    if filtro != "Tutte":

        df = df[
            df["stato_pratica"] == filtro
        ]

    colonne = [

        "cognome",

        "nome",

        "arrivo",

        "partenza",

        "alloggio_assegnato",

        "stato_pratica",

        "prezzo_alloggio"

    ]

    st.dataframe(

        df[colonne],

        use_container_width=True,

        hide_index=True

    )
        st.divider()

    st.subheader("Gestione Stato Prenotazione")

    elenco = (
        df["cognome"].fillna("") + " " +
        df["nome"].fillna("") + " | " +
        df["arrivo"].astype(str)
    ).tolist()

    if elenco:

        indice = st.selectbox(
            "Seleziona prenotazione",
            range(len(elenco)),
            format_func=lambda x: elenco[x]
        )

        nuovo_stato = st.selectbox(
            "Nuovo stato",
            STATI_PRENOTAZIONE,
            key="stato_prenotazione"
        )

        if st.button("Aggiorna Stato"):

            conn = get_connection()

            cur = conn.cursor()

            cur.execute("""

                UPDATE ospiti

                SET stato_pratica = ?

                WHERE id = ?

            """, (

                nuovo_stato,

                int(df.iloc[indice]["id"])

            ))

            conn.commit()

            conn.close()

            sincronizza_csv()

            logging.info(
                f"Prenotazione {int(df.iloc[indice]['id'])} aggiornata."
            )

            st.success("Stato aggiornato correttamente.")

            st.rerun()
                st.divider()

    st.subheader("🗑 Elimina Prenotazione")

    elimina = st.checkbox(
        "Confermo di voler eliminare la prenotazione"
    )

    if elimina:

        if st.button(
            "Elimina definitivamente",
            type="primary"
        ):

            id_prenotazione = int(
                df.iloc[indice]["id"]
            )

            conn = get_connection()

            cur = conn.cursor()

            cur.execute(
                "DELETE FROM ospiti WHERE id=?",
                (id_prenotazione,)
            )

            conn.commit()

            conn.close()

            sincronizza_csv()

            logging.info(
                f"Prenotazione eliminata ID={id_prenotazione}"
            )

            st.success(
                "Prenotazione eliminata con successo."
            )

            st.rerun()

# =============================================================================
# FINE PAGINA PRENOTAZIONI
# =============================================================================
# =============================================================================
# CALENDARIO PRENOTAZIONI
# =============================================================================

def pagina_calendario():

    st.title("📆 Calendario Prenotazioni")

    df = leggi_database()

    if df.empty:

        st.info("Nessuna prenotazione presente.")

        return

    df["arrivo"] = pd.to_datetime(
        df["arrivo"],
        errors="coerce"
    )

    df["partenza"] = pd.to_datetime(
        df["partenza"],
        errors="coerce"
    )

    calendario = df.sort_values(
        by="arrivo"
    )[
        [
            "arrivo",
            "partenza",
            "cognome",
            "nome",
            "alloggio_assegnato",
            "stato_pratica"
        ]
    ]

    st.dataframe(

        calendario,

        use_container_width=True,

        hide_index=True

    )

    st.caption(
        "Calendario ordinato cronologicamente."
    )
# =============================================================================
# CALENDARIO FILTRI
# =============================================================================

    st.divider()

    alloggi = sorted(
        df["alloggio_assegnato"]
        .fillna("")
        .unique()
        .tolist()
    )

    alloggi.insert(0, "Tutti")

    filtro_alloggio = st.selectbox(
        "Alloggio",
        alloggi
    )

    if filtro_alloggio != "Tutti":

        calendario = calendario[
            calendario["alloggio_assegnato"] ==
            filtro_alloggio
        ]

    periodo = st.radio(

        "Visualizzazione",

        [

            "Tutte",

            "Prossimi 30 giorni",

            "Prossimi 90 giorni"

        ],

        horizontal=True

    )

    oggi = pd.Timestamp.today().normalize()

    if periodo == "Prossimi 30 giorni":

        calendario = calendario[
            calendario["arrivo"] <= oggi + pd.Timedelta(days=30)
        ]

    elif periodo == "Prossimi 90 giorni":

        calendario = calendario[
            calendario["arrivo"] <= oggi + pd.Timedelta(days=90)
        ]

    st.dataframe(
        calendario,
        use_container_width=True,
        hide_index=True
    )
# =============================================================================
# FORMULA FIDUCIARIA
# =============================================================================

def verifica_formula_fiduciaria(record):

    stato = str(
        record.get("stato_pratica", "")
    ).strip()

    caparra = float(
        record.get("caparra", 0) or 0
    )

    if stato != "Confermata":

        return "Non Applicabile"

    if caparra == 0:

        return "Formula Fiduciaria"

    return "Caparra Versata"

# =============================================================================
# CALCOLO LEAD TIME
# =============================================================================

def calcola_lead_time(arrivo):

    try:

        data_arrivo = pd.to_datetime(arrivo)

        oggi = pd.Timestamp.today().normalize()

        return (data_arrivo - oggi).days

    except Exception:

        return None

# =============================================================================
# AGGIORNAMENTO LEAD TIME
# =============================================================================

def aggiorna_lead_time(df):

    if "arrivo" not in df.columns:

        return df
            df["lead_time"] = df["arrivo"].apply(
        calcola_lead_time
    )

    if "formula_fiduciaria" not in df.columns:

        df["formula_fiduciaria"] = ""

    for indice in df.index:

        df.at[
            indice,
            "formula_fiduciaria"
        ] = verifica_formula_fiduciaria(
            df.loc[indice]
        )

    return df

# =============================================================================
# LEAD IN SCADENZA
# =============================================================================

def lead_da_contattare(df):

    if "lead_time" not in df.columns:

        return pd.DataFrame()

    return df[
        (df["lead_time"] >= 0) &
        (df["lead_time"] <= 7) &
        (df["stato_pratica"] == "In corso")
    ].sort_values(
        by="lead_time"
    )

# =============================================================================
# PRATICHE CONFERMATE SENZA CAPARRA
# =============================================================================

def pratiche_fiduciarie(df):

    return df[
        df["formula_fiduciaria"] ==
        "Formula Fiduciaria"
    ]
# =============================================================================
# WORKFLOW AUTOMATICI CRM
# =============================================================================

def controlla_workflow():

    df = leggi_database()

    if df.empty:
        return

    df = aggiorna_lead_time(df)

    da_contattare = lead_da_contattare(df)

    if len(da_contattare) > 0:

        st.sidebar.warning(
            f"⚠ {len(da_contattare)} lead da contattare"
        )

    fiduciarie = pratiche_fiduciarie(df)

    if len(fiduciarie) > 0:

        st.sidebar.success(
            f"🤝 {len(fiduciarie)} prenotazioni Formula Fiduciaria"
        )

    sincronizza_csv()

# =============================================================================
# DASHBOARD - AVVISI
# =============================================================================

def dashboard_avvisi():

    df = leggi_database()

    if df.empty:
        return

    controlla_workflow()

    st.subheader("Avvisi CRM")

    lead = lead_da_contattare(df)

    if len(lead) > 0:

        st.error(
            f"Sono presenti {len(lead)} richieste da ricontattare."
        )
    fiduciarie = pratiche_fiduciarie(df)

    if len(fiduciarie) > 0:

        st.info(
            f"Formula Fiduciaria attiva per "
            f"{len(fiduciarie)} prenotazioni."
        )

    scadute = df[
        (df["lead_time"] < 0) &
        (df["stato_pratica"] == "In corso")
    ]

    if len(scadute) > 0:

        st.warning(
            f"{len(scadute)} richieste risultano scadute."
        )

# =============================================================================
# BLACKLIST INTERNA
# =============================================================================

def cliente_in_blacklist(email):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""

        SELECT COUNT(*)

        FROM blacklist

        WHERE email=?

    """, (email,))

    presente = cur.fetchone()[0]

    conn.close()

    return presente > 0
# =============================================================================
# CREAZIONE TABELLA BLACKLIST
# =============================================================================

def inizializza_blacklist():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""

        CREATE TABLE IF NOT EXISTS blacklist (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            cognome TEXT,

            nome TEXT,

            email TEXT,

            telefono TEXT,

            motivo TEXT,

            data_inserimento TEXT,

            note TEXT

        )

    """)

    conn.commit()

    conn.close()

# =============================================================================
# INIZIALIZZAZIONE TABELLE CRM
# =============================================================================

inizializza_blacklist()

logging.info(
    "Tabella blacklist verificata."
)

# =============================================================================
# AGGIUNTA CLIENTE IN BLACKLIST
# =============================================================================

def aggiungi_blacklist(
    cognome,
    nome,
    email,
    telefono,
    motivo,
    note=""
):
        conn = get_connection()

    cur = conn.cursor()

    cur.execute("""

        INSERT INTO blacklist (

            cognome,
            nome,
            email,
            telefono,
            motivo,
            data_inserimento,
            note

        )

        VALUES (?,?,?,?,?,?,?)

    """, (

        cognome,
        nome,
        email,
        telefono,
        motivo,
        date.today().isoformat(),
        note

    ))

    conn.commit()

    conn.close()

    logging.warning(
        f"Cliente inserito in blacklist: {cognome} {nome}"
    )

# =============================================================================
# ELENCO BLACKLIST
# =============================================================================

def leggi_blacklist():

    conn = get_connection()

    df = pd.read_sql_query(

        "SELECT * FROM blacklist ORDER BY cognome",

        conn

    )

    conn.close()

    return df
# =============================================================================
# RIMOZIONE CLIENTE DALLA BLACKLIST
# =============================================================================

def rimuovi_blacklist(id_blacklist):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(

        "DELETE FROM blacklist WHERE id=?",

        (id_blacklist,)

    )

    conn.commit()

    conn.close()

    logging.info(
        f"Cliente rimosso dalla blacklist ID={id_blacklist}"
    )

# =============================================================================
# PAGINA BLACKLIST
# =============================================================================

def pagina_blacklist():

    st.title("🚫 Blacklist Clienti")

    df = leggi_blacklist()

    if df.empty:

        st.success(
            "Nessun cliente presente in blacklist."
        )

        return

    st.dataframe(

        df,

        use_container_width=True,

        hide_index=True

    )
# =============================================================================
# GESTIONE NO SHOW
# =============================================================================

def registra_no_show(id_pratica):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""

        SELECT *

        FROM ospiti

        WHERE id=?

    """, (id_pratica,))

    record = cur.fetchone()

    if record is None:

        conn.close()

        return False

    cur.execute("""

        UPDATE ospiti

        SET stato_pratica=?

        WHERE id=?

    """, (

        "No Show",

        id_pratica

    ))

    conn.commit()

    conn.close()

    aggiungi_blacklist(

        record["cognome"],

        record["nome"],

        record["email"],

        "",

        "NO SHOW",

        "Inserimento automatico dal CRM"

    )

    logging.warning(
        f"No Show registrato ID={id_pratica}"
    )

    sincronizza_csv()

    return True
# =============================================================================
# ELENCO CAMPI DATABASE CRM
# =============================================================================

CAMPI_DATABASE = [

    "ID",

    "Data_Contatto",
    "Ora_Contatto",
    "Lead_Time",

    "Cognome",
    "Nome",

    "Telefono_Fisso",
    "Cellulare",
    "WhatsApp",

    "Email",

    "Lingua",
    "Nazionalita",

    "Arrivo",
    "Partenza",

    "Alloggio_Assegnato",

    "Adulti",
    "Bambini",
    "Ospiti_Totali",

    "Canale",
    "Portale_Origine",

    "Codice_Prenotazione",
    "ID_OTA",

    "Tariffa",

    "Prezzo_Alloggio",

    "Extra",

    "Sconto_Salvato",

    "Caparra",

    "Fatturato_Consolidato",

    "Tassa_Soggiorno",

    "Stato_Pratica",

]
    "Formula_Fiduciaria",

    "Consenso_GDPR",

    "Data_Consenso_GDPR",

    "Stato_Email",

    "Data_Email",

    "Stato_WhatsApp",

    "Data_WhatsApp",

    "Data_Ultimo_Contatto",

    "Ora_Ultimo_Contatto",

    "Workflow_Attivo",

    "Priorita_Lead",

    "Data_Invio_Recensione",

    "Esito_Recensione",

    "Recensione_Booking",

    "Recensione_Google",

    "Recensione_Airbnb",

    "Voucher",

    "Codice_Voucher",

    "Metodo_Pagamento",

    "Data_Pagamento",

    "Numero_Fattura",

    "Check_In_Effettuato",

    "Check_Out_Effettuato",

    "Documenti_Ricevuti",

    "Care4UHotel",

    "Scadenza_Care4UHotel",

    "No_Show",

    "Blacklist",

    "Data_Blacklist",
    "Motivo_Blacklist",

    "Operatore",

    "Data_Ultima_Modifica",

    "Ora_Ultima_Modifica",

    "Note_Interne",

    "Storico_Comunicazioni"

]

# =============================================================================
# VERIFICA STRUTTURA DATABASE
# =============================================================================

def verifica_struttura_database(df):

    modificato = False

    for campo in CAMPI_DATABASE:

        if campo not in df.columns:

            df[campo] = ""

            modificato = True

    df = df[CAMPI_DATABASE]

    if modificato:

        salva_csv(df)

        logging.info(
            "Struttura database aggiornata automaticamente."
        )

    return df

# =============================================================================
# CARICAMENTO DATABASE DEFINITIVO
# =============================================================================

def carica_database():

    df = carica_csv()

    if df.empty:

        return pd.DataFrame(columns=CAMPI_DATABASE)

    return verifica_struttura_database(df)
# =============================================================================
# SALVATAGGIO DATABASE DEFINITIVO
# =============================================================================

def salva_database_crm(df):

    df = verifica_struttura_database(df)

    try:

        df.to_csv(

            CSV_FILE,

            index=False,

            encoding="utf-8-sig"

        )

        logging.info(
            "Database CRM salvato."
        )

        return True

    except Exception as errore:

        logging.error(
            f"Errore salvataggio database: {errore}"
        )

        st.error(
            "Errore durante il salvataggio."
        )

        return False

# =============================================================================
# RICERCA GLOBALE
# =============================================================================

def ricerca_globale(df, testo):

    if testo.strip() == "":

        return df
    testo = testo.lower().strip()

    colonne = [

        "Cognome",

        "Nome",

        "Email",

        "Cellulare",

        "WhatsApp",

        "Codice_Prenotazione",

        "Portale_Origine",

        "Alloggio_Assegnato"

    ]

    filtro = False

    for colonna in colonne:

        if colonna in df.columns:

            risultato = (

                df[colonna]

                .fillna("")

                .astype(str)

                .str.lower()

                .str.contains(testo)

            )

            filtro = risultato if isinstance(
                filtro, bool
            ) else filtro | risultato

    return df[filtro]
# =============================================================================
# PRIORITA' AUTOMATICA LEAD
# =============================================================================

def calcola_priorita_lead(record):

    try:

        lead = int(record["Lead_Time"])

    except:

        return "Bassa"

    stato = str(record["Stato_Pratica"])

    if stato != "In corso":

        return "Chiusa"

    if lead <= 2:

        return "URGENTE"

    if lead <= 7:

        return "Alta"

    if lead <= 30:

        return "Media"

    return "Bassa"

# =============================================================================
# AGGIORNA PRIORITA'
# =============================================================================

def aggiorna_priorita(df):

    df["Priorita_Lead"] = df.apply(

        calcola_priorita_lead,

        axis=1

    )

    return df
# =============================================================================
# DASHBOARD LEAD
# =============================================================================

def dashboard_lead(df):

    st.subheader("🎯 Priorità Lead")

    urgenti = len(

        df[
            df["Priorita_Lead"] == "URGENTE"
        ]

    )

    alte = len(

        df[
            df["Priorita_Lead"] == "Alta"
        ]

    )

    medie = len(

        df[
            df["Priorita_Lead"] == "Media"
        ]

    )

    basse = len(

        df[
            df["Priorita_Lead"] == "Bassa"
        ]

    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "🔴 Urgenti",
        urgenti
    )

    c2.metric(
        "🟠 Alte",
        alte
    )

    c3.metric(
        "🟡 Medie",
        medie
    )

    c4.metric(
        "🟢 Basse",
        basse
    )

    st.divider()

    elenco = df[
        df["Priorita_Lead"] == "URGENTE"
    ]

    if len(elenco) > 0:

        st.error(
            "Lead da contattare immediatamente"
        )

        st.dataframe(

            elenco[

                [
                    "Cognome",
                    "Nome",
                    "Cellulare",
                    "Arrivo",
                    "Lead_Time",
                    "Portale_Origine"
                ]

            ],

            hide_index=True,

            use_container_width=True

        )
# =============================================================================
# CONTROLLO OVERBOOKING
# =============================================================================

def controlla_overbooking(df):

    anomalie = []

    confermate = df[
        df["Stato_Pratica"] == "Confermata"
    ]

    for alloggio in confermate[
        "Alloggio_Assegnato"
    ].dropna().unique():

        dati = confermate[
            confermate["Alloggio_Assegnato"] ==
            alloggio
        ].sort_values("Arrivo")

        for i in range(len(dati) - 1):

            partenza = pd.to_datetime(
                dati.iloc[i]["Partenza"]
            )

            arrivo = pd.to_datetime(
                dati.iloc[i + 1]["Arrivo"]
            )

            if arrivo < partenza:

                anomalie.append(

                    {

                        "Alloggio": alloggio,

                        "Prenotazione 1":
                        dati.iloc[i]["Cognome"],

                        "Prenotazione 2":
                        dati.iloc[i + 1]["Cognome"]

                    }

                )
    return pd.DataFrame(anomalie)

# =============================================================================
# DASHBOARD OVERBOOKING
# =============================================================================

def dashboard_overbooking(df):

    st.subheader("🚨 Controllo Overbooking")

    anomalie = controlla_overbooking(df)

    if anomalie.empty:

        st.success(
            "Nessun overbooking rilevato."
        )

        return

    st.error(
        f"Trovati {len(anomalie)} possibili overbooking."
    )

    st.dataframe(

        anomalie,

        hide_index=True,

        use_container_width=True

    )

    for _, riga in anomalie.iterrows():

        logging.warning(

            f"OVERBOOKING: "

            f"{riga['Alloggio']} - "

            f"{riga['Prenotazione 1']} / "

            f"{riga['Prenotazione 2']}"

        )

# =============================================================================
# FINE CONTROLLO OVERBOOKING
# =============================================================================
# =============================================================================
# DISPONIBILITA' ALLOGGI
# =============================================================================

def verifica_disponibilita(

    df,

    alloggio,

    arrivo,

    partenza

):

    arrivo = pd.to_datetime(arrivo)

    partenza = pd.to_datetime(partenza)

    occupazione = df[

        (df["Alloggio_Assegnato"] == alloggio) &

        (df["Stato_Pratica"] == "Confermata")

    ]

    for _, prenotazione in occupazione.iterrows():

        inizio = pd.to_datetime(
            prenotazione["Arrivo"]
        )

        fine = pd.to_datetime(
            prenotazione["Partenza"]
        )

        if arrivo < fine and partenza > inizio:

            return False

    return True
# =============================================================================
# GESTIONE ALLOGGI
# =============================================================================

def inizializza_tabella_alloggi():

    conn = sqlite3.connect(DB_SQLITE)

    cur = conn.cursor()

    cur.execute("""

        CREATE TABLE IF NOT EXISTS alloggi(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            nome TEXT UNIQUE,

            tipologia TEXT,

            posti INTEGER,

            attivo INTEGER DEFAULT 1

        )

    """)

    conn.commit()

    conn.close()


def elenco_alloggi():

    conn = sqlite3.connect(DB_SQLITE)

    df = pd.read_sql_query(

        """

        SELECT *

        FROM alloggi

        WHERE attivo=1

        ORDER BY nome

        """,

        conn

    )

    conn.close()

    return df
def inserisci_alloggi_predefiniti():

    conn = sqlite3.connect(DB_SQLITE)

    cur = conn.cursor()

    alloggi = [

        ("Appartamento Girasole","Appartamento",10),

        ("Casale Lucia","Villa",6),

        ("Villa Tulipano","Villa",8),

        ("Pajara Lucy","Pajara",4),

        ("Monolocale Marina","Monolocale",3),

        ("Monolocale Margherita","Monolocale",2),

        ("Monolocale Glicine","Monolocale",3),

        ("Appartamento Lido Marini","Appartamento",4)

    ]

    for nome, tipo, posti in alloggi:

        cur.execute(

            """

            INSERT OR IGNORE INTO alloggi

            (nome,tipologia,posti)

            VALUES(?,?,?)

            """,

            (nome, tipo, posti)

        )

    conn.commit()

    conn.close()
# =============================================================================
# MENU ALLLOGGI
# =============================================================================

def pagina_alloggi():

    st.header("🏡 Gestione Alloggi")

    df = elenco_alloggi()

    tab1, tab2 = st.tabs(

        [

            "Elenco",

            "Nuovo Alloggio"

        ]

    )

    with tab1:

        st.dataframe(

            df,

            hide_index=True,

            use_container_width=True

        )

    with tab2:

        with st.form("nuovo_alloggio"):

            nome = st.text_input(

                "Nome alloggio"

            )

            tipologia = st.selectbox(

                "Tipologia",

                [

                    "Villa",

                    "Appartamento",

                    "Monolocale",

                    "Pajara",

                    "Camera"

                ]

            )
                        posti = st.number_input(

                "Posti letto",

                1,

                20,

                2

            )

            salva = st.form_submit_button(

                "💾 Salva"

            )

        if salva:

            conn = sqlite3.connect(DB_SQLITE)

            cur = conn.cursor()

            cur.execute(

                """

                INSERT INTO alloggi

                (

                    nome,

                    tipologia,

                    posti

                )

                VALUES

                (

                    ?,?,?

                )

                """,

                (

                    nome,

                    tipologia,

                    posti

                )

            )

            conn.commit()

            conn.close()

            st.success(

                "Alloggio inserito."

            )

            st.rerun()
# =============================================================================
# SELECT DINAMICA ALLOGGI
# =============================================================================

def lista_nomi_alloggi():

    df = elenco_alloggi()

    if df.empty:

        return []

    return sorted(

        df["nome"].tolist()

    )


def select_alloggio(

    label="Alloggio"

):

    alloggi = lista_nomi_alloggi()

    if len(alloggi) == 0:

        st.warning(

            "Nessun alloggio disponibile."

        )

        return None

    return st.selectbox(

        label,

        alloggi

    )
# =============================================================================
# FORM PRENOTAZIONE
# =============================================================================

def form_prenotazione():

    st.subheader(

        "Nuova Prenotazione"

    )

    with st.form(

        "prenotazione"

    ):

        cognome = st.text_input(

            "Cognome"

        )

        nome = st.text_input(

            "Nome"

        )

        alloggio = select_alloggio(

            "Alloggio"

        )

        arrivo = st.date_input(

            "Data Arrivo"

        )

        partenza = st.date_input(

            "Data Partenza"

        )
        ospiti = st.number_input(

            "Numero Ospiti",

            1,

            20,

            2

        )

        canale = st.selectbox(

            "Canale",

            CANALI

        )

        stato = st.selectbox(

            "Stato",

            STATI_PRENOTAZIONE

        )

        salva = st.form_submit_button(

            "💾 Salva Prenotazione"

        )

    if salva:

        nuova_prenotazione(

            cognome,

            nome,

            alloggio,

            arrivo,

            partenza,

            ospiti,

            canale,

            stato

        )
# =============================================================================
# TARIFFE STAGIONALI
# =============================================================================

def inizializza_tabella_tariffe():

    conn = sqlite3.connect(DB_SQLITE)

    cur = conn.cursor()

    cur.execute("""

        CREATE TABLE IF NOT EXISTS tariffe(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            alloggio TEXT,

            stagione TEXT,

            data_inizio DATE,

            data_fine DATE,

            prezzo REAL,

            soggiorno_minimo INTEGER DEFAULT 1,

            attiva INTEGER DEFAULT 1

        )

    """)

    conn.commit()

    conn.close()
def elenco_tariffe():

    conn = sqlite3.connect(DB_SQLITE)

    df = pd.read_sql_query(

        """

        SELECT *

        FROM tariffe

        WHERE attiva = 1

        ORDER BY

            data_inizio,

            alloggio

        """,

        conn

    )

    conn.close()

    return df


def pagina_tariffe():

    st.header(

        "💶 Tariffe"

    )

    df = elenco_tariffe()

    st.dataframe(

        df,

        hide_index=True,

        use_container_width=True

    )
    st.divider()

    with st.form(

        "nuova_tariffa"

    ):

        alloggio = select_alloggio(

            "Alloggio"

        )

        stagione = st.selectbox(

            "Stagione",

            [

                "Bassa",

                "Media",

                "Alta",

                "Altissima"

            ]

        )

        data_inizio = st.date_input(

            "Dal"

        )

        data_fine = st.date_input(

            "Al"

        )

        prezzo = st.number_input(

            "Prezzo €/notte",

            min_value=0.0,

            step=5.0
                    soggiorno = st.number_input(

            "Soggiorno minimo",

            min_value=1,

            max_value=30,

            value=1

        )

        salva = st.form_submit_button(

            "💾 Salva Tariffa"

        )

    if salva:

        conn = sqlite3.connect(DB_SQLITE)

        cur = conn.cursor()

        cur.execute(

            """

            INSERT INTO tariffe(

                alloggio,

                stagione,

                data_inizio,

                data_fine,

                prezzo,

                soggiorno_minimo

            )

            VALUES(?,?,?,?,?,?)

            """,

            (

                alloggio,

                stagione,

                data_inizio,
                                data_fine,

                prezzo,

                soggiorno

            )

        )

        conn.commit()

        conn.close()

        st.success(

            "Tariffa salvata."

        )

        st.rerun()

# =============================================================================
# FINE MODULO TARIFFE
# =============================================================================
# =============================================================================
# CALCOLO PREVENTIVO
# =============================================================================

def cerca_tariffa(

    alloggio,

    data_arrivo

):

    conn = sqlite3.connect(DB_SQLITE)

    query = """

        SELECT *

        FROM tariffe

        WHERE

            alloggio = ?

        AND

            attiva = 1

        AND

            date(?) BETWEEN

            date(data_inizio)

        AND

            date(data_fine)

        LIMIT 1

    """

    df = pd.read_sql_query(

        query,

        conn,

        params=(

            alloggio,

            data_arrivo

        )

    )

    conn.close()

    return df
def calcola_notti(

    arrivo,

    partenza

):

    arrivo = pd.to_datetime(arrivo)

    partenza = pd.to_datetime(partenza)

    return (

        partenza -

        arrivo

    ).days


def calcola_prezzo_base(

    alloggio,

    arrivo,

    partenza

):

    tariffa = cerca_tariffa(

        alloggio,

        arrivo

    )

    if tariffa.empty:

        return None
    prezzo_notte = float(

        tariffa.iloc[0]["prezzo"]

    )

    notti = calcola_notti(

        arrivo,

        partenza

    )

    totale = (

        prezzo_notte *

        notti

    )

    return {

        "notti": notti,

        "prezzo_notte": prezzo_notte,

        "totale": totale

    }
def widget_preventivo():

    st.subheader(

        "💶 Preventivo"

    )

    alloggio = select_alloggio()

    arrivo = st.date_input(

        "Arrivo"

    )

    partenza = st.date_input(

        "Partenza"

    )

    if st.button(

        "Calcola"

    ):

        risultato = calcola_prezzo_base(

            alloggio,

            arrivo,

            partenza

        )
        if risultato is None:

            st.error(

                "Tariffa non trovata."

            )

        else:

            st.success(

                f"""

                Notti:
                {risultato['notti']}

                Prezzo/notte:
                € {risultato['prezzo_notte']:.2f}

                Totale:
                € {risultato['totale']:.2f}

                """

            )
            # =============================================================================
# SCONTI AUTOMATICI
# =============================================================================

def calcola_sconto(

    totale,

    tipo_sconto

):

    percentuali = {

        "NESSUNO": 0,

        "WELCOME": 15,

        "SPECIAL": 20,

        "LAST_MINUTE": 10,

        "LONG_STAY": 12

    }

    perc = percentuali.get(

        tipo_sconto,

        0

    )

    valore = round(

        totale * perc / 100,

        2

    )

    return {

        "percentuale": perc,

        "importo": valore,

        "totale": totale - valore

    }
# =============================================================================
# EXTRA
# =============================================================================

EXTRA_DISPONIBILI = {

    "Pulizia Finale": 40,

    "Biancheria": 15,

    "Navetta Aeroporto": 90,

    "Navetta Stazione": 45,

    "Animale Domestico": 35,

    "Care4UHotel": 0

}


def totale_extra(

    selezionati

):

    totale = 0

    for voce in selezionati:

        totale += EXTRA_DISPONIBILI.get(

            voce,

            0

        )

    return totale
# =============================================================================
# PREVENTIVO COMPLETO
# =============================================================================

def calcola_preventivo(

    alloggio,

    arrivo,

    partenza,

    sconto,

    extra

):

    base = calcola_prezzo_base(

        alloggio,

        arrivo,

        partenza

    )

    if base is None:

        return None

    totale_base = base["totale"]

    dati_sconto = calcola_sconto(

        totale_base,

        sconto

    )
    totale_servizi = totale_extra(

        extra

    )

    totale_finale = (

        dati_sconto["totale"]

        +

        totale_servizi

    )

    return {

        **base,

        "sconto": dati_sconto,

        "extra": totale_servizi,

        "totale_finale": totale_finale

    }
# =============================================================================
# WIDGET PREVENTIVO AVANZATO
# =============================================================================

def widget_preventivo_avanzato():

    st.header(

        "📑 Preventivo"

    )

    alloggio = select_alloggio()

    arrivo = st.date_input(

        "Arrivo"

    )

    partenza = st.date_input(

        "Partenza"

    )

    sconto = st.selectbox(

        "Promozione",

        [

            "NESSUNO",

            "WELCOME",

            "SPECIAL",

            "LAST_MINUTE",

            "LONG_STAY"

        ]

    )
    extra = st.multiselect(

        "Servizi Extra",

        list(

            EXTRA_DISPONIBILI.keys()

        )

    )

    if st.button(

        "Calcola Preventivo"

    ):

        risultato = calcola_preventivo(

            alloggio,

            arrivo,

            partenza,

            sconto,

            extra

        )

        if risultato is None:

            st.error(

                "Tariffa non disponibile."

            )

            return
                    st.success(

            f"""

Notti: {risultato['notti']}

Prezzo/notte: € {risultato['prezzo_notte']:.2f}

Totale soggiorno: € {risultato['totale']:.2f}

Sconto: - € {risultato['sconto']['importo']:.2f}

Extra: € {risultato['extra']:.2f}

==========================

TOTALE: € {risultato['totale_finale']:.2f}

"""

        )
# =============================================================================
# CODICI PROMOZIONALI
# =============================================================================

def inizializza_tabella_promozioni():

    conn = sqlite3.connect(DB_SQLITE)

    cur = conn.cursor()

    cur.execute("""

        CREATE TABLE IF NOT EXISTS promozioni(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            codice TEXT UNIQUE,

            descrizione TEXT,

            sconto REAL,

            data_inizio DATE,

            data_fine DATE,

            utilizzi INTEGER DEFAULT 0,

            massimo_utilizzi INTEGER DEFAULT 999,

            attiva INTEGER DEFAULT 1

        )

    """)

    conn.commit()

    conn.close()


def cerca_promozione(codice):

    conn = sqlite3.connect(DB_SQLITE)

    df = pd.read_sql_query(

        """

        SELECT *

        FROM promozioni

        WHERE

            codice=?

        AND

            attiva=1

        LIMIT 1

        """,

        conn,

        params=(codice,)

    )

    conn.close()

    if df.empty:

        return None

    return df.iloc[0]


def applica_codice_promozionale(

    totale,

    codice

):

    promo = cerca_promozione(

        codice

    )

    if promo is None:

        return totale,0

    sconto = round(

        totale *

        promo["sconto"]/100,

        2

    )

    return (

        totale-sconto,

        sconto

    )
# =============================================================================
# GESTIONE EXTRA DINAMICI
# =============================================================================

def inizializza_tabella_extra():

    conn = sqlite3.connect(DB_SQLITE)

    cur = conn.cursor()

    cur.execute("""

        CREATE TABLE IF NOT EXISTS extra(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            descrizione TEXT,

            prezzo REAL,

            obbligatorio INTEGER DEFAULT 0,

            attivo INTEGER DEFAULT 1

        )

    """)

    conn.commit()

    conn.close()


def elenco_extra():

    conn = sqlite3.connect(DB_SQLITE)

    df = pd.read_sql_query(

        """

        SELECT *

        FROM extra

        WHERE attivo=1

        ORDER BY descrizione

        """,

        conn

    )

    conn.close()

    return df


def totale_extra_database(

    elenco

):

    df = elenco_extra()

    totale = 0

    for voce in elenco:

        riga = df[

            df["descrizione"]

            == voce

        ]

        if not riga.empty:

            totale += float(

                riga.iloc[0]["prezzo"]

            )

    return totale
# =============================================================================
# PAGINA GESTIONE EXTRA
# =============================================================================

def pagina_extra():

    st.header("🧾 Gestione Servizi Extra")

    df = elenco_extra()

    tab1, tab2 = st.tabs(

        [

            "Elenco",

            "Nuovo Extra"

        ]

    )

    with tab1:

        if df.empty:

            st.info(

                "Nessun servizio disponibile."

            )

        else:

            st.dataframe(

                df,

                hide_index=True,

                use_container_width=True

            )

    with tab2:

        with st.form(

            "nuovo_extra"

        ):

            descrizione = st.text_input(

                "Descrizione"

            )

            prezzo = st.number_input(

                "Prezzo",

                min_value=0.0,

                step=1.0,

                value=0.0

            )

            obbligatorio = st.checkbox(

                "Obbligatorio"

            )

            salva = st.form_submit_button(

                "💾 Salva"

            )

        if salva:

            conn = sqlite3.connect(DB_SQLITE)

            cur = conn.cursor()

            cur.execute(

                """

                INSERT INTO extra(

                    descrizione,

                    prezzo,

                    obbligatorio

                )

                VALUES(

                    ?,?,?

                )

                """,

                (

                    descrizione,

                    prezzo,

                    int(obbligatorio)

                )

            )

            conn.commit()

            conn.close()

            st.success(

                "Servizio inserito."

            )

            st.rerun()

# =============================================================================
# ELIMINAZIONE EXTRA
# =============================================================================

def elimina_extra(id_extra):

    conn = sqlite3.connect(DB_SQLITE)

    cur = conn.cursor()

    cur.execute(

        """

        UPDATE extra

        SET attivo=0

        WHERE id=?

        """,

        (id_extra,)

    )

    conn.commit()

    conn.close()


def pagina_elimina_extra():

    st.subheader(

        "Elimina Extra"

    )

    df = elenco_extra()

    if df.empty:

        return

    scelta = st.selectbox(

        "Servizio",

        df["descrizione"]

    )

    if st.button(

        "❌ Elimina"

    ):

        id_extra = int(

            df[

                df["descrizione"]

                == scelta

            ].iloc[0]["id"]

        )

        elimina_extra(

            id_extra

        )

        st.success(

            "Servizio eliminato."

        )

        st.rerun()

# =============================================================================
# MODIFICA EXTRA
# =============================================================================

def aggiorna_extra(

    id_extra,

    descrizione,

    prezzo,

    obbligatorio

):

    conn = sqlite3.connect(DB_SQLITE)

    cur = conn.cursor()

    cur.execute(

        """

        UPDATE extra

        SET

            descrizione=?,

            prezzo=?,

            obbligatorio=?

        WHERE id=?

        """,

        (

            descrizione,

            prezzo,

            int(obbligatorio),

            id_extra

        )

    )

    conn.commit()

    conn.close()


def pagina_modifica_extra():

    st.subheader(

        "Modifica Extra"

    )

    df = elenco_extra()

    if df.empty:

        return

    scelta = st.selectbox(

        "Servizio da modificare",

        df["descrizione"]

    )

    riga = df[

        df["descrizione"]

        == scelta

    ].iloc[0]
    with st.form("modifica_extra"):

        descrizione = st.text_input(

            "Descrizione",

            value=riga["descrizione"]

        )

        prezzo = st.number_input(

            "Prezzo",

            min_value=0.0,

            value=float(riga["prezzo"]),

            step=1.0

        )

        obbligatorio = st.checkbox(

            "Obbligatorio",

            value=bool(riga["obbligatorio"])

        )

        salva = st.form_submit_button(

            "💾 Aggiorna"

        )

    if salva:

        aggiorna_extra(

            int(riga["id"]),

            descrizione,

            prezzo,

            obbligatorio

        )

        st.success(

            "Extra aggiornato."

        )

        st.rerun()

# =============================================================================
# PROMOZIONI
# =============================================================================

def elenco_promozioni():

    conn = sqlite3.connect(DB_SQLITE)

    df = pd.read_sql_query(

        """

        SELECT *

        FROM promozioni

        WHERE attiva=1

        ORDER BY data_inizio

        """,

        conn

    )

    conn.close()

    return df


def inserisci_promozione(

    codice,

    descrizione,

    sconto,

    data_inizio,

    data_fine,

    massimo

):

    conn = sqlite3.connect(DB_SQLITE)

    cur = conn.cursor()

    cur.execute(

        """

        INSERT INTO promozioni(

            codice,

            descrizione,

            sconto,

            data_inizio,

            data_fine,

            massimo_utilizzi

        )

        VALUES(

            ?,?,?,?,?,?

        )

        """,

        (

            codice.upper(),

            descrizione,

            sconto,

            data_inizio,

            data_fine,

            massimo

        )

    )

    conn.commit()

    conn.close()


def pagina_promozioni():

    st.header(

        "🏷 Gestione Promozioni"

    )

    df = elenco_promozioni()

    tab1, tab2 = st.tabs(

        [

            "Elenco",

            "Nuova Promozione"

        ]

    )

    with tab1:

        if df.empty:

            st.info(

                "Nessuna promozione."

            )

        else:

            st.dataframe(

                df,

                hide_index=True,

                use_container_width=True

            )

    with tab2:

        with st.form(

            "nuova_promozione"

        ):

            codice = st.text_input(

                "Codice"

            )

            descrizione = st.text_input(

                "Descrizione"

            )

            sconto = st.number_input(

                "Sconto %",

                0.0,

                100.0,

                10.0

            )

            data_inizio = st.date_input(

                "Valida dal"

            )

            data_fine = st.date_input(

                "Valida fino al"

            )

            massimo = st.number_input(

                "Numero massimo utilizzi",

                1,

                9999,

                999

            )

            salva = st.form_submit_button(

                "💾 Salva Promozione"

            )

        if salva:

            inserisci_promozione(

                codice,

                descrizione,

                sconto,

                data_inizio,

                data_fine,

                massimo

            )

            st.success(

                "Promozione registrata."

            )

            st.rerun()
# =============================================================================
# MOTORE DISPONIBILITA'
# =============================================================================

def prenotazioni_confermate():

    conn = sqlite3.connect(DB_SQLITE)

    df = pd.read_sql_query(

        """

        SELECT *

        FROM ospiti

        WHERE

            Stato_Pratica='Confermata'

        """,

        conn

    )

    conn.close()

    return df


def alloggi_disponibili(

    arrivo,

    partenza

):

    alloggi = elenco_alloggi()

    prenotazioni = prenotazioni_confermate()

    disponibili = []

    arrivo = pd.to_datetime(arrivo)

    partenza = pd.to_datetime(partenza)

    for _, alloggio in alloggi.iterrows():

        occupato = False

        dati = prenotazioni[

            prenotazioni[

                "Alloggio_Assegnato"

            ] == alloggio["nome"]

        ]

        for _, p in dati.iterrows():

            inizio = pd.to_datetime(

                p["Arrivo"]

            )

            fine = pd.to_datetime(

                p["Partenza"]

            )

            if (

                arrivo < fine

                and

                partenza > inizio

            ):

                occupato = True

                break

        if not occupato:

            disponibili.append(

                {

                    "Alloggio":

                    alloggio["nome"],

                    "Tipologia":

                    alloggio["tipologia"],

                    "Posti":

                    alloggio["posti"]

                }

            )

    return pd.DataFrame(

        disponibili

    )


# =============================================================================
# RICERCA DISPONIBILITA'
# =============================================================================

def pagina_disponibilita():

    st.header(

        "📅 Disponibilità"

    )

    col1, col2 = st.columns(2)

    with col1:

        arrivo = st.date_input(

            "Arrivo"

        )

    with col2:

        partenza = st.date_input(

            "Partenza"

        )

    if st.button(

        "🔍 Cerca"

    ):

        risultato = alloggi_disponibili(

            arrivo,

            partenza

        )

        if risultato.empty:

            st.warning(

                "Nessun alloggio disponibile."

            )

        else:

            st.success(

                f"{len(risultato)} alloggi disponibili."

            )

            st.dataframe(

                risultato,

                hide_index=True,

                use_container_width=True

            )

# =============================================================================
# CALENDARIO OCCUPAZIONE
# =============================================================================

def occupazione_alloggi():

    conn = sqlite3.connect(DB_SQLITE)

    df = pd.read_sql_query(

        """

        SELECT

            Cognome,

            Nome,

            Alloggio_Assegnato,

            Arrivo,

            Partenza,

            Stato_Pratica

        FROM ospiti

        WHERE

            Stato_Pratica='Confermata'

        ORDER BY Arrivo

        """,

        conn

    )

    conn.close()

    return df
# =============================================================================
# PLANNING ALLOGGI
# =============================================================================

from calendar import monthrange


def genera_planning(

    anno,

    mese

):

    prenotazioni = occupazione_alloggi()

    alloggi = elenco_alloggi()

    giorni = monthrange(

        anno,

        mese

    )[1]

    planning = []

    for _, alloggio in alloggi.iterrows():

        riga = {

            "Alloggio":

            alloggio["nome"]

        }

        for giorno in range(

            1,

            giorni + 1

        ):

            riga[str(giorno)] = ""

        dati = prenotazioni[

            prenotazioni[

                "Alloggio_Assegnato"

            ] == alloggio["nome"]

        ]

        for _, p in dati.iterrows():

            arrivo = pd.to_datetime(

                p["Arrivo"]

            )

            partenza = pd.to_datetime(

                p["Partenza"]

            )

            if (

                arrivo.year != anno

                and

                partenza.year != anno

            ):

                continue

            for giorno in range(

                1,

                giorni + 1

            ):

                data = datetime(

                    anno,

                    mese,

                    giorno

                )

                if (

                    data >= arrivo

                    and

                    data < partenza

                ):

                    testo = "🟥"

                    if data == arrivo:

                        testo = "🟨"

                    elif data == (

                        partenza -

                        timedelta(days=1)

                    ):

                        testo = "🟦"

                    riga[str(giorno)] = testo

        planning.append(

            riga

        )

    return pd.DataFrame(

        planning

    )


# =============================================================================
# PAGINA PLANNING
# =============================================================================

def pagina_planning():

    st.header(

        "📅 Planning Occupazione"

    )

    oggi = datetime.today()

    col1, col2 = st.columns(2)

    with col1:

        anno = st.number_input(

            "Anno",

            min_value=2025,

            max_value=2050,

            value=oggi.year

        )

    with col2:

        mese = st.selectbox(

            "Mese",

            list(range(1,13)),

            index=oggi.month-1

        )

    planning = genera_planning(

        int(anno),

        int(mese)

    )

    st.dataframe(

        planning,

        hide_index=True,

        use_container_width=True,

        height=650

    )

# =============================================================================
# DETTAGLIO GIORNO
# =============================================================================

def ospiti_del_giorno(data):

    conn = sqlite3.connect(DB_SQLITE)

    df = pd.read_sql_query(

        """

        SELECT

            Cognome,

            Nome,

            Alloggio_Assegnato,

            Arrivo,

            Partenza

        FROM ospiti

        WHERE

            Stato_Pratica='Confermata'

        """,

        conn

    )

    conn.close()

    data = pd.to_datetime(data)

    elenco = []

    for _, riga in df.iterrows():

        arrivo = pd.to_datetime(

            riga["Arrivo"]

        )

        partenza = pd.to_datetime(

            riga["Partenza"]

        )

        if (

            data >= arrivo

            and

            data < partenza

        ):

            elenco.append(riga)

    return pd.DataFrame(

        elenco

    )
# =============================================================================
# DASHBOARD OPERATIVA GIORNALIERA
# =============================================================================

def dashboard_operativa():

    st.header("🏨 Dashboard Operativa")

    oggi = pd.Timestamp.today().normalize()

    df = carica_database()

    if df.empty:

        st.info("Nessuna prenotazione presente.")

        return

    df["Arrivo"] = pd.to_datetime(df["Arrivo"])

    df["Partenza"] = pd.to_datetime(df["Partenza"])

    checkin = df[

        (df["Arrivo"] == oggi) &

        (df["Stato_Pratica"] == "Confermata")

    ]

    checkout = df[

        (df["Partenza"] == oggi) &

        (df["Stato_Pratica"] == "Confermata")

    ]

    presenti = df[

        (df["Arrivo"] <= oggi) &

        (df["Partenza"] > oggi) &

        (df["Stato_Pratica"] == "Confermata")

    ]

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(

            "🟢 Check-In",

            len(checkin)

        )

    with c2:

        st.metric(

            "🔵 Check-Out",

            len(checkout)

        )

    with c3:

        st.metric(

            "🏡 Ospiti Presenti",

            len(presenti)

        )

    st.divider()

# =============================================================================
# CHECK IN
# =============================================================================

    st.subheader("🟢 Arrivi di oggi")

    if checkin.empty:

        st.success(

            "Nessun arrivo previsto."

        )

    else:

        st.dataframe(

            checkin[

                [

                    "Cognome",

                    "Nome",

                    "Alloggio_Assegnato",

                    "Cellulare",

                    "Ospiti_Totali"

                ]

            ],

            hide_index=True,

            use_container_width=True

        )

# =============================================================================
# CHECK OUT
# =============================================================================

    st.subheader("🔵 Partenze di oggi")

    if checkout.empty:

        st.success(

            "Nessuna partenza prevista."

        )

    else:

        st.dataframe(

            checkout[

                [

                    "Cognome",

                    "Nome",

                    "Alloggio_Assegnato",

                    "Cellulare"

                ]

            ],

            hide_index=True,

            use_container_width=True

        )

# =============================================================================
# OSPITI PRESENTI
# =============================================================================

    st.subheader("🏠 Attualmente presenti")

    if presenti.empty:

        st.info(

            "Nessun ospite presente."

        )

    else:

        st.dataframe(

            presenti[

                [

                    "Cognome",

                    "Nome",

                    "Alloggio_Assegnato",

                    "Arrivo",

                    "Partenza",

                    "Cellulare"

                ]

            ],

            hide_index=True,

            use_container_width=True

        )

# =============================================================================
# ALLERTE
# =============================================================================

    st.divider()

    scadenze = presenti[

        presenti["Partenza"]

        <=

        oggi +

        pd.Timedelta(days=2)

    ]

    if not scadenze.empty:

        st.warning(

            "⚠️ Nei prossimi due giorni sono previsti check-out."

        )

        st.dataframe(

            scadenze[

                [

                    "Cognome",

                    "Nome",

                    "Partenza",

                    "Alloggio_Assegnato"

                ]

            ],

            hide_index=True,

            use_container_width=True

        )
# =============================================================================
# CHECK-IN DIGITALE
# =============================================================================

def prenotazioni_in_arrivo():

    oggi = pd.Timestamp.today().normalize()

    df = carica_database()

    if df.empty:

        return df

    df["Arrivo"] = pd.to_datetime(df["Arrivo"])

    return df[

        (df["Arrivo"] >= oggi) &

        (df["Stato_Pratica"] == "Confermata")

    ].sort_values(

        "Arrivo"

    )


def registra_checkin(

    id_pratica,

    documento,

    numero_documento,

    rilasciato_da,

    data_scadenza

):

    conn = sqlite3.connect(DB_SQLITE)

    cur = conn.cursor()

    cur.execute(

        """

        UPDATE ospiti

        SET

            Check_In_Effettuato=1,

            Documenti_Ricevuti=1,

            Tipo_Documento=?,

            Numero_Documento=?,

            Documento_Rilasciato_Da=?,

            Documento_Scadenza=?

        WHERE ID=?

        """,

        (

            documento,

            numero_documento,

            rilasciato_da,

            data_scadenza,

            id_pratica

        )

    )

    conn.commit()

    conn.close()


# =============================================================================
# PAGINA CHECK-IN
# =============================================================================

def pagina_checkin():

    st.header(

        "🟢 Check-In"

    )

    df = prenotazioni_in_arrivo()

    if df.empty:

        st.success(

            "Nessun check-in."

        )

        return

    cliente = st.selectbox(

        "Prenotazione",

        df.apply(

            lambda x:

            f"{x['Cognome']} {x['Nome']} - {x['Arrivo'].date()}",

            axis=1

        )

    )

    riga = df.iloc[

        st.session_state.get(

            "checkin_index",

            0

        )

    ]

    st.write(

        f"**Alloggio:** {riga['Alloggio_Assegnato']}"

    )

    st.write(

        f"**Telefono:** {riga['Cellulare']}"

    )

    with st.form(

        "form_checkin"

    ):

        tipo = st.selectbox(

            "Documento",

            [

                "Carta Identità",

                "Passaporto",

                "Patente"

            ]

        )

        numero = st.text_input(

            "Numero"

        )

        ente = st.text_input(

            "Rilasciato da"

        )

        scadenza = st.date_input(

            "Scadenza"

        )

        conferma = st.form_submit_button(

            "✅ Conferma Check-In"

        )

    if conferma:

        registra_checkin(

            int(riga["ID"]),

            tipo,

            numero,

            ente,

            scadenza

        )

        st.success(

            "Check-in registrato."

        )

        st.balloons()

        st.rerun()
