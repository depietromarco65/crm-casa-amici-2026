import streamlit as st
import pandas as pd
import requests
import csv
import base64
import io
from datetime import datetime

# ==========================================================
# CONFIGURAZIONE APPLICAZIONE
# ==========================================================

st.set_page_config(
    page_title="CRM - A Casa di Amici",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# CONFIGURAZIONE GITHUB
# ==========================================================

REPO = "depietromarco65/crm-casa-amici-2026"
BRANCH = "main"
DATABASE = "database_ospiti.csv"

RAW_URL = (
    f"https://raw.githubusercontent.com/"
    f"{REPO}/{BRANCH}/{DATABASE}"
)

API_URL = (
    f"https://api.github.com/repos/"
    f"{REPO}/contents/{DATABASE}"
)

# ==========================================================
# STILE GRAFICO
# ==========================================================

st.markdown("""
<style>

.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
}

div[data-testid="stMetric"]{
    border:1px solid #d9d9d9;
    border-radius:12px;
    padding:15px;
    background:white;
}

.card{
    border:1px solid #E6E6E6;
    border-radius:12px;
    padding:15px;
    margin-bottom:12px;
    background:#ffffff;
}

.badge{
    border-radius:20px;
    padding:4px 12px;
    font-size:12px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)
# ==========================================================
# CARICAMENTO DATABASE
# ==========================================================

@st.cache_data(ttl=30)
def carica_database():

    try:

        df = pd.read_csv(
            RAW_URL,
            dtype=str,
            keep_default_na=False
        )

        df.fillna("nd", inplace=True)

        return df

    except Exception as errore:

        st.error(f"Errore caricamento database: {errore}")

        return pd.DataFrame()


# ==========================================================
# CORREZIONE EMAIL
# ==========================================================

def correggi_email(email):

    if not email:
        return "nd"

    email = email.strip().lower()

    sostituzioni = {

        "@gmal.com":"@gmail.com",
        "@gmaill.com":"@gmail.com",
        "@gmail.con":"@gmail.com",
        "@hotmal.com":"@hotmail.com",
        "@hotmial.com":"@hotmail.com",
        "@liberoit":"@libero.it",
        "@icloud.con":"@icloud.com"

    }

    for errata, corretta in sostituzioni.items():

        if email.endswith(errata):

            email = email.replace(errata, corretta)

    return email


# ==========================================================
# SALVATAGGIO SU GITHUB
# ==========================================================

def salva_database(df):

    if "GITHUB_TOKEN" not in st.secrets:

        st.error("Token GitHub mancante")

        return False

    token = st.secrets["GITHUB_TOKEN"]

    headers = {

        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"

    }

    risposta = requests.get(API_URL, headers=headers)

    if risposta.status_code != 200:

        st.error("Impossibile leggere il file GitHub")

        return False

    sha = risposta.json()["sha"]

    csv_buffer = io.StringIO()

    df.to_csv(
        csv_buffer,
        index=False
    )

    contenuto = base64.b64encode(
        csv_buffer.getvalue().encode("utf-8")
    ).decode()

    payload = {

        "message":"Aggiornamento CRM",

        "content":contenuto,

        "sha":sha

    }

    commit = requests.put(

        API_URL,

        headers=headers,

        json=payload

    )

    return commit.status_code in [200,201]
    # ==========================================================
# CARICAMENTO DATABASE
# ==========================================================

df = carica_database()

if df.empty:
    st.stop()
df = carica_database()

if df.empty:
    st.stop()

# ==========================================================
# CREAZIONE AUTOMATICA CAMPI CRM
# ==========================================================

campi_crm = [
    "Telefono",
    "WhatsApp",
    "Compleanno",
    "Cliente VIP",
    "Blacklist",
    "Lead Caldo",
    "Green Incentive",
    "Preferenze",
    "Note CRM"
]

nuove_colonne = False

for campo in campi_crm:
    if campo not in df.columns:
        df[campo] = "nd"
        nuove_colonne = True

if nuove_colonne:
    salva_database(df)
    st.success("Database aggiornato con i nuovi campi CRM.")
# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.image(
    "https://img.icons8.com/fluency/96/home.png",
    width=70
)

st.sidebar.title("🏡 CRM")

pagina = st.sidebar.radio(

    "Menu",

    [

        "Dashboard",
        "Nuovo Contatto",
        "Ricerca",
        "Prenotazioni",
        "Statistiche",
        "Impostazioni"

    ]

)

st.sidebar.markdown("---")

st.sidebar.write(f"Record database: **{len(df)}**")

# ==========================================================
# DASHBOARD
# ==========================================================

if pagina == "Dashboard":

    st.title("🏡 CRM - A Casa di Amici")

    st.caption("Gestione Contatti e Prenotazioni")

    col1,col2,col3,col4 = st.columns(4)

    with col1:

        st.metric(

            "👥 Contatti",

            len(df)

        )

    confermate = df[
        df["Stato Richiesta"]
        .str.contains(
            "confer",
            case=False,
            na=False
        )
    ]

    with col2:

        st.metric(

            "✅ Confermate",

            len(confermate)

        )

    attesa = df[
        df["Stato Richiesta"]
        .str.contains(
            "attesa",
            case=False,
            na=False
        )
    ]

    with col3:

        st.metric(

            "🟡 Attesa",

            len(attesa)

        )

    try:

        totale = (

            pd.to_numeric(

                df["Tariffa Totale (€)"]
                .astype(str)
                .str.replace(",", "."),

                errors="coerce"

            )

            .fillna(0)

            .sum()

        )

    except:

        totale = 0

    with col4:

        st.metric(

            "💶 Totale",

            f"€ {totale:,.2f}"

        )
        # ==========================================================
# RICERCA RAPIDA
# ==========================================================

st.markdown("---")

st.subheader("🔍 Ricerca Cliente")

ricerca = st.text_input(

    "",

    placeholder="Cognome, Nome, Email, ID..."

)

if ricerca:

    filtro = (

        df["Cognome Capofamiglia"].str.contains(
            ricerca,
            case=False,
            na=False
        )

        |

        df["Nome Capofamiglia"].str.contains(
            ricerca,
            case=False,
            na=False
        )

        |

        df["Email"].str.contains(
            ricerca,
            case=False,
            na=False
        )

        |

        df["N. Progressivo"].astype(str).str.contains(
            ricerca,
            na=False
        )

    )

    risultati = df[filtro]

else:

    risultati = df.copy()

st.write(f"**Risultati:** {len(risultati)}")

st.markdown("---")

# ==========================================================
# TABELLA CRM
# ==========================================================

visualizza = risultati[[

    "N. Progressivo",

    "Cognome Capofamiglia",

    "Nome Capofamiglia",

    "Data Presunta Arrivo",

    "Data Presunta Partenza",

    "Alloggio Assegnato",

    "Email",

    "Stato Richiesta",

    "Tariffa Totale (€)"

]]

st.dataframe(

    visualizza,

    use_container_width=True,

    hide_index=True

)
# ==========================================================
# SCHEDA CLIENTE
# ==========================================================

st.markdown("---")

if len(risultati) > 0:

    id_cliente = st.selectbox(

        "Seleziona Cliente",

        risultati["N. Progressivo"].astype(str)

    )

    indice = df[
        df["N. Progressivo"].astype(str) == id_cliente
    ].index[0]

    record = df.loc[indice]

    st.subheader("📋 Scheda Cliente")

    col1, col2 = st.columns(2)

    with col1:

        cognome = st.text_input(
            "Cognome",
            record["Cognome Capofamiglia"]
        )

        nome = st.text_input(
            "Nome",
            record["Nome Capofamiglia"]
        )

        email = st.text_input(
            "Email",
            record["Email"]
        )

        arrivo = st.text_input(
            "Data Arrivo",
            record["Data Presunta Arrivo"]
        )

        partenza = st.text_input(
            "Data Partenza",
            record["Data Presunta Partenza"]
        )

    with col2:

        alloggio = st.text_input(
            "Alloggio",
            record["Alloggio Assegnato"]
        )

        stato = st.text_input(
            "Stato Richiesta",
            record["Stato Richiesta"]
        )

        tariffa = st.text_input(
            "Tariffa Totale (€)",
            record["Tariffa Totale (€)"]
        )

        note = st.text_area(
            "Note",
            record["Note Aggiuntive"],
            height=180
        )
        # ==========================================================
# SALVATAGGIO MODIFICHE
# ==========================================================

    st.markdown("---")

    if st.button(
        "💾 Salva Modifiche",
        use_container_width=True
    ):

        df.at[indice, "Cognome Capofamiglia"] = cognome.strip()

        df.at[indice, "Nome Capofamiglia"] = nome.strip()

        df.at[indice, "Email"] = correggi_email(email)

        df.at[indice, "Data Presunta Arrivo"] = arrivo

        df.at[indice, "Data Presunta Partenza"] = partenza

        df.at[indice, "Alloggio Assegnato"] = alloggio

        df.at[indice, "Stato Richiesta"] = stato

        df.at[indice, "Tariffa Totale (€)"] = tariffa

        df.at[indice, "Note Aggiuntive"] = note

        ok = salva_database(df)

        if ok:

            st.success("✅ Modifiche salvate correttamente.")

            st.cache_data.clear()

            st.rerun()

        else:

            st.error("❌ Errore durante il salvataggio su GitHub.")
