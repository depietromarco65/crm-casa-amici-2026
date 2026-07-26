import streamlit as st
import pandas as pd
import requests
import base64
from io import StringIO
from datetime import datetime, date

st.set_page_config(
    page_title="CRM - A Casa di Amici",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)
OWNER = "depietromarco65"
REPOSITORY = "crm-casa-amici-2026"
BRANCH = "main"

CSV_FILE = "database_ospiti.csv"

RAW_URL = (
    f"https://raw.githubusercontent.com/"
    f"{OWNER}/{REPOSITORY}/{BRANCH}/{CSV_FILE}"
)
COLONNE = [
    "N. Progressivo",
    "Data Contatto",
    "Ora Contatto",
    "Giorni Lead Time",
    "Cognome Capofamiglia",
    "Nome Capofamiglia",
    "Data Presunta Arrivo",
    "Data Presunta Partenza",
    "Alloggio Assegnato",
    "Numero Ospiti Totale",
    "Nominativo Ospiti (Dettaglio + Compleanni + Onomastici)",
    "Adulti",
    "Minori",
    "Email",
    "Portale di Provenienza",
    "Razza Taglia e Nome Cane",
    "Tariffa Totale (€)",
    "Costo Biancheria (€)",
    "Tipo Tariffa (Standard/Non Rimb.)",
    "Stato Saldo",
    "Mezzo di Trasporto e Orario Arrivo",
    "Stato Richiesta",
    "Note Aggiuntive"
]
@st.cache_data(ttl=30)

def carica_database():

    try:

        risposta = requests.get(
            RAW_URL,
            timeout=20
        )

        risposta.raise_for_status()

        df = pd.read_csv(
            StringIO(risposta.text),
            dtype=str,
            keep_default_na=False
        )

        df.columns = df.columns.str.strip()

        for colonna in COLONNE:

            if colonna not in df.columns:

                df[colonna] = ""

        df = df[COLONNE]

        return df

    except Exception as errore:

        st.error(errore)

        return pd.DataFrame(columns=COLONNE)


df = carica_database()
def euro(valore):

    try:

        return float(
            str(valore)
            .replace("€", "")
            .replace(".", "")
            .replace(",", ".")
            .strip()
        )

    except:

        return 0.0


def giorni_lead(contatto, arrivo):

    try:

        d1 = datetime.strptime(
            contatto,
            "%d/%m/%Y"
        )

        d2 = datetime.strptime(
            arrivo,
            "%d/%m/%Y"
        )

        return (d2-d1).days

    except:

        return ""
if not df.empty:

    if "Giorni Lead Time" in df.columns:

        df["Giorni Lead Time"] = df.apply(

            lambda r: giorni_lead(
                r["Data Contatto"],
                r["Data Presunta Arrivo"]
            ),

            axis=1

        )
st.title("🏡 CRM A Casa di Amici")

st.caption(
    "Gestione Ospiti • Marketing • Statistiche • Dashboard CEO"
)
if df.empty:

    st.warning("Il database è vuoto.")

    st.stop()


totale_contatti = len(df)

prenotazioni_confermate = len(
    df[
        df["Stato Richiesta"]
        .str.contains(
            "confer",
            case=False,
            na=False
        )
    ]
)

lista_attesa = len(
    df[
        df["Stato Richiesta"]
        .str.contains(
            "attesa",
            case=False,
            na=False
        )
    ]
)

non_disponibili = len(
    df[
        df["Stato Richiesta"]
        .str.contains(
            "non",
            case=False,
            na=False
        )
    ]
)

clienti_pet = len(
    df[
        df["Razza Taglia e Nome Cane"]
        .str.strip()
        != ""
    ]
)

fatturato = (
    df["Tariffa Totale (€)"]
    .apply(euro)
    .sum()
)

biancheria = (
    df["Costo Biancheria (€)"]
    .apply(euro)
    .sum()
)

lead = pd.to_numeric(
    df["Giorni Lead Time"],
    errors="coerce"
)

lead_medio = round(
    lead.mean(),
    1
)
st.divider()

st.subheader("📊 Dashboard CEO")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Contatti",
    totale_contatti
)

c2.metric(
    "Confermate",
    prenotazioni_confermate
)

c3.metric(
    "Lista Attesa",
    lista_attesa
)

c4.metric(
    "Clienti Pet",
    clienti_pet
)

c5, c6, c7 = st.columns(3)

c5.metric(
    "Lead Time Medio",
    f"{lead_medio} giorni"
)

c6.metric(
    "Fatturato",
    f"€ {fatturato:,.2f}"
)

c7.metric(
    "Biancheria",
    f"€ {biancheria:,.2f}"
)
st.divider()

pagina = st.sidebar.radio(

    "MENU",

    [

        "Dashboard",

        "Archivio",

        "Nuovo Contatto",

        "Marketing",

        "Statistiche"

    ]

)
if pagina == "Dashboard":

    st.subheader("Ultimi contatti")

    st.dataframe(

        df.sort_values(

            by="N. Progressivo",

            ascending=False

        ),

        use_container_width=True,

        hide_index=True

    )
if pagina == "Archivio":

    st.subheader("📋 Archivio Clienti")

    filtro_cognome = st.text_input(
        "Cerca Cognome"
    ).strip().lower()

    filtro_nome = st.text_input(
        "Cerca Nome"
    ).strip().lower()

    filtro_portale = st.selectbox(
        "Portale",
        ["Tutti"] + sorted(
            df["Portale di Provenienza"]
            .fillna("")
            .unique()
            .tolist()
        )
    )

    archivio = df.copy()
    if filtro_cognome:

        archivio = archivio[
            archivio["Cognome Capofamiglia"]
            .str.lower()
            .str.contains(
                filtro_cognome,
                na=False
            )
        ]

    if filtro_nome:

        archivio = archivio[
            archivio["Nome Capofamiglia"]
            .str.lower()
            .str.contains(
                filtro_nome,
                na=False
            )
        ]

    if filtro_portale != "Tutti":

        archivio = archivio[
            archivio["Portale di Provenienza"]
            == filtro_portale
        ]
    st.dataframe(

        archivio,

        use_container_width=True,

        hide_index=True

    )
    st.divider()

    elenco = (
        archivio["Cognome Capofamiglia"]
        + " "
        + archivio["Nome Capofamiglia"]
    ).tolist()

    if elenco:

        cliente = st.selectbox(

            "Scheda Cliente",

            elenco

        )

        indice = elenco.index(cliente)

        record = archivio.iloc[indice]

        c1, c2 = st.columns(2)

        with c1:

            st.write("### Dati")

            st.write(
                "**Cognome:**",
                record["Cognome Capofamiglia"]
            )

            st.write(
                "**Nome:**",
                record["Nome Capofamiglia"]
            )

            st.write(
                "**Email:**",
                record["Email"]
            )

            st.write(
                "**Telefono/Trasporto:**",
                record["Mezzo di Trasporto e Orario Arrivo"]
            )

            st.write(
                "**Portale:**",
                record["Portale di Provenienza"]
            )

        with c2:

            st.write("### Prenotazione")

            st.write(
                "**Arrivo:**",
                record["Data Presunta Arrivo"]
            )

            st.write(
                "**Partenza:**",
                record["Data Presunta Partenza"]
            )

            st.write(
                "**Alloggio:**",
                record["Alloggio Assegnato"]
            )

            st.write(
                "**Tariffa:**",
                record["Tariffa Totale (€)"]
            )

            st.write(
                "**Saldo:**",
                record["Stato Saldo"]
            )

            st.write(
                "**Stato:**",
                record["Stato Richiesta"]
            )

        st.divider()

        st.write("### Note")

        st.text_area(

            "",

            record["Note Aggiuntive"],

            height=150,

            disabled=True

        )
    csv = archivio.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(

        "⬇️ Esporta Archivio",

        csv,

        "archivio_clienti.csv",

        "text/csv"

    )

