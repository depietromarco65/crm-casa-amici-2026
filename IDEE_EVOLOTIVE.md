# IDEE_EVOLUTIVE.md

# CRM / PMS - Registro delle Evoluzioni

Questo documento raccoglie tutte le idee, le migliorie e le funzionalità future del progetto.

## Principi del progetto

Ogni nuova funzionalità dovrà rispettare i seguenti criteri:

- risolvere un'esigenza reale;
- non complicare inutilmente il software;
- essere modulare;
- essere compatibile con l'architettura del PMS;
- essere configurabile tramite database e non tramite codice.

---

# Evoluzioni previste

## 001 - Gestione Multi-Struttura

### Obiettivo

Consentire la gestione di un numero illimitato di strutture ricettive all'interno dello stesso PMS.

### Stato

✔ Prevista

### Priorità

Alta

### Note

Ogni struttura potrà avere:

- dati fiscali
- CIN/CIR
- logo
- fotografie
- utenti dedicati
- impostazioni proprie
- unità ricettive

---

## 002 - Gestione Unità Ricettive

### Obiettivo

Sostituire il concetto di "alloggio" con "Unità Ricettiva".

Una unità potrà essere:

- villa
- appartamento
- camera
- suite
- bungalow
- trullo
- pajara
- piazzola
- ecc.

---

## 003 - Dashboard Direzionale

Da sviluppare.

Funzioni previste:

- Occupazione
- ADR
- RevPAR
- Incassi
- Check-in
- Check-out
- Saldi
- Statistiche

---

## 004 - AI Assistant

Da sviluppare.

L'assistente AI dovrà:

- aiutare la reception
- suggerire prezzi
- individuare anomalie
- generare report
- rispondere ai clienti

---

## 005 - Booking Engine Proprietario

Obiettivo:

Consentire la prenotazione diretta dal sito.

Funzioni:

- disponibilità
- preventivo
- pagamento
- conferma automatica

---

## 006 - Channel Manager

Obiettivo

Il PMS dovrà poter dialogare con:

- Booking.com
- Airbnb
- Vrbo
- Expedia
- Google

Preferibilmente tramite API ufficiali.

iCal dovrà essere utilizzato esclusivamente come sistema di emergenza o fallback.

---

## 007 - Housekeeping

Da sviluppare.

Gestione:

- pulizie
- cambio biancheria
- manutenzioni
- controlli qualità

---

## 008 - Workflow Automatici

Automazioni previste:

- preventivi
- conferme
- saldo
- check-in
- check-out
- richiesta recensione
- fidelizzazione cliente

---

# Idee da valutare

In questa sezione verranno annotate tutte le idee future senza implementarle immediatamente.

Ogni idea dovrà contenere:

## Titolo

### Problema

...

### Soluzione proposta

...

### Benefici

...

### Complessità

Bassa / Media / Alta

### Priorità

Bassa / Media / Alta

### Stato

- Da valutare
- Approvata
- In sviluppo
- Completata
- Scartata

---

# Decisioni progettuali

Questa sezione conterrà le decisioni importanti prese durante lo sviluppo.

## Decisione 001

Il PMS sarà progettato come software multi-struttura.

Motivazione:

consentire la crescita futura senza modificare l'architettura.

---

## Decisione 002

Il database sarà l'unica fonte dei dati.

Il codice non dovrà contenere:

- tariffe
- servizi
- strutture
- promozioni
- configurazioni

Tutti questi elementi saranno gestiti tramite il database.

---

## Decisione 003

Il PMS sarà sviluppato in modo modulare.

Ogni nuovo modulo dovrà poter essere aggiunto senza modificare quelli esistenti.
