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

# =====================================================================
# BLOCCO 3 - KPI, LEAD TIME E STATISTICHE
# =====================================================================

def calcola_lead_time(data_contatto, data_arrivo):

    try:

        d1 = datetime.strptime(
            data_contatto.strip(),
            "%d/%m/%Y"
        )

        d2 = datetime.strptime(
            data_arrivo.strip(),
            "%d/%m/%Y"
        )

        return (d2 - d1).days

    except:

        return None


totale_lead_time = 0
conteggio_lead = 0

confermate = 0
lista_attesa = 0
non_disponibili = 0
in_sospeso = 0

pet_friendly = 0

for riga in righe:

    lead = calcola_lead_time(
        riga.get("Data del contatto", ""),
        riga.get("data presunta di Arrivo", "")
    )

    if lead is None:
        riga["Lead Time"] = "N.D."
    else:
        riga["Lead Time"] = lead
        totale_lead_time += lead
        conteggio_lead += 1

    esito = riga.get(
        "Esito",
        ""
    ).lower()

    if "confermata" in esito:
        confermate += 1

    elif "lista" in esito:
        lista_attesa += 1

    elif "non" in esito:
        non_disponibili += 1

    else:
        in_sospeso += 1

    cane = riga.get(
        "Cane (Razza/Taglia)",
        ""
    ).lower()

    if (
        cane
        and cane != "no"
        and cane != "-"
        and cane != "nessuno"
    ):
        pet_friendly += 1


lead_medio = 0

if conteggio_lead > 0:
    lead_medio = round(
        totale_lead_time / conteggio_lead,
        1
    )


# =====================================================================
# BLOCCO 4 - CREAZIONE TABS
# =====================================================================

tab_dashboard, tab_archivio, tab_marketing, tab_nuovo = st.tabs(
    [
        "📊 Dashboard CEO",
        "📋 Archivio",
        "🎯 Marketing",
        "➕ Nuovo Contatto"
    ]
)

# =====================================================================
# BLOCCO 5 - DASHBOARD CEO
# =====================================================================

with tab_dashboard:

    st.header("Dashboard Direzionale")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Totale Contatti",
        len(righe)
    )

    c2.metric(
        "Prenotazioni Confermate",
        confermate
    )

    c3.metric(
        "Clienti Pet Friendly",
        pet_friendly
    )

    c4.metric(
        "Lead Time Medio",
        f"{lead_medio} giorni"
    )

    st.divider()

    a, b, c, d = st.columns(4)

    a.metric(
        "In sospeso",
        in_sospeso
    )

    b.metric(
        "Lista attesa",
        lista_attesa
    )

    c.metric(
        "Non disponibili",
        non_disponibili
    )

    d.metric(
        "Database",
        f"{len(righe)} record"
    )

# =====================================================================
# BLOCCO 6 - FILTRI ARCHIVIO
# =====================================================================

with tab_archivio:

    st.header("Archivio Ospiti")

    c1, c2, c3 = st.columns(3)

    cognome = c1.text_input(
        "Cognome"
    ).strip().lower()

    alloggio = c2.text_input(
        "Alloggio"
    ).strip().lower()

    solo_animali = c3.checkbox(
        "Solo clienti Pet Friendly"
    )

    risultati = []

    for r in righe:

        ok = True

        if cognome:

            if cognome not in r.get(
                "Cognome",
                ""
            ).lower():

                ok = False

        if alloggio:

            if alloggio not in r.get(
                "Note aggiuntive",
                ""
            ).lower():

                ok = False

        cane = r.get(
            "Cane (Razza/Taglia)",
            ""
        ).lower()

        animale = (
            cane
            and cane != "no"
            and cane != "-"
            and cane != "nessuno"
        )

        if solo_animali and not animale:

            ok = False

        if ok:

            risultati.append(r)

# =====================================================================
# BLOCCO 7 - TABELLA ARCHIVIO
# =====================================================================

    if risultati:

        st.dataframe(
            risultati,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "Nessun record trovato."
        )

# =====================================================================
# BLOCCO 8 - MARKETING
# =====================================================================

with tab_marketing:

    st.header("Marketing CRM")

    cognomi = sorted(
        list(
            {
                r["Cognome"]
                for r in righe
                if r.get("Cognome")
            }
        )
    )

    if cognomi:

        scelto = st.selectbox(
            "Cliente",
            cognomi
        )

        cliente = next(
            r
            for r in righe
            if r["Cognome"] == scelto
        )

        nome = cliente.get(
            "Nome",
            ""
        )

        cane = cliente.get(
            "Cane (Razza/Taglia)",
            ""
        )

        note = cliente.get(
            "Note aggiuntive",
            ""
        ).lower()

        oggetto = "Un saluto da Torre Pali"

        if "burraco" in note:

            testo = f"""Gentile {nome},

ci farebbe molto piacere riavervi nostri ospiti.

Le prenotazioni dirette sono già aperte.

https://acasadiamici.info
"""

        elif cane:

            testo = f"""Gentile {nome},

anche {cane} sarà il benvenuto.

https://acasadiamici.info
"""

        else:

            testo = f"""Gentile {nome},

stiamo aprendo le prenotazioni della nuova stagione.

https://acasadiamici.info
"""

        st.text_input(
            "Oggetto",
            oggetto
        )

        st.text_area(
            "Email",
            testo,
            height=300
        )

# =====================================================================
# BLOCCO 9 - NUOVO CONTATTO
# =====================================================================

with tab_nuovo:

    st.header("Nuovo Contatto")

    with st.form("nuovo"):

        c1, c2 = st.columns(2)

        with c1:

            data_contatto = st.text_input(
                "Data",
                datetime.now().strftime("%d/%m/%Y")
            )

            cognome = st.text_input("Cognome")

            nome = st.text_input("Nome")

            nominativi = st.text_area(
                "Nominativi"
            )

            arrivo = st.text_input(
                "Arrivo"
            )

            partenza = st.text_input(
                "Partenza"
            )

        with c2:

            ospiti = st.number_input(
                "Ospiti",
                1,
                20,
                2
            )

            adulti = st.number_input(
                "Adulti",
                1,
                20,
                2
            )

            minori = st.number_input(
                "Minori",
                0,
                20,
                0
            )

            email = st.text_input(
                "Email"
            )

            portale = st.selectbox(
                "Portale",
                [
                    "Sito",
                    "Booking",
                    "Airbnb",
                    "VRBO",
                    "Lovely",
                    "UltMin"
                ]
            )

            cane = st.text_input(
                "Animale",
                "No"
            )

            esito = st.selectbox(
                "Esito",
                [
                    "🔄 In sospeso",
                    "✅ Confermata",
                    "📋 Lista attesa",
                    "❌ Non disponibile"
                ]
            )

            note = st.text_area(
                "Note"
            )

        salva = st.form_submit_button(
            "Salva"
        )

# =====================================================================
# BLOCCO 10 - SALVATAGGIO
# =====================================================================

        if salva:

            nuovo_id = len(righe) + 1

            nuova_riga = [
                nuovo_id,
                data_contatto,
                cognome,
                nome,
                nominativi,
                arrivo,
                partenza,
                ospiti,
                adulti,
                minori,
                email,
                portale,
                note,
                cane,
                esito
            ]

            st.info(
                "Il salvataggio sul repository GitHub verrà implementato tramite GitHub API nel blocco successivo."
            )

