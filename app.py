import csv
import io
import requests

# ======================================================================
# DATABASE UFFICIALE GITHUB
# ======================================================================

DATABASE_URL = (
    "https://raw.githubusercontent.com/"
    "depietromarco65/"
    "crm-casa-amici-2026/"
    "main/"
    "database_ospiti.csv"
)

COLONNE_DATABASE = [
    "numero progressivo",
    "Data del contatto",
    "Cognome",
    "Nome",
    "Nominativi Ospiti",
    "data presunta di Arrivo",
    "data presunta di Partenza",
    "Numero Ospiti",
    "adulti",
    "minori",
    "Email",
    "Portale di provenienza",
    "Note aggiuntive",
    "Cane (Razza/Taglia)",
    "Esito"
]


@st.cache_data(show_spinner=False)
def carica_database():

    righe = []

    try:

        risposta = requests.get(
            DATABASE_URL,
            timeout=20
        )

        risposta.raise_for_status()

        contenuto = io.StringIO(risposta.text)

        reader = csv.DictReader(contenuto)

        for riga in reader:

            record = {}

            for campo in COLONNE_DATABASE:
                record[campo] = (
                    riga.get(campo, "")
                    .strip()
                )

            righe.append(record)

    except Exception as errore:

        st.error(
            f"Errore lettura database GitHub:\n{errore}"
        )

    return righe


righe = carica_database()
