# ARCHITETTURA_PMS.md

# PMS - Architettura del Progetto

## Visione

Il progetto nasce come evoluzione del CRM "A Casa di Amici", ma viene progettato fin dall'inizio come un **Property Management System (PMS)** moderno, modulare e scalabile.

"A Casa di Amici" rappresenta la prima implementazione del sistema e non costituisce un vincolo architetturale.

Il PMS dovrà poter gestire un numero illimitato di strutture ricettive senza richiedere modifiche al codice sorgente.

---

# Filosofia del progetto

Il PMS dovrà essere:

- semplice da utilizzare;
- semplice da mantenere;
- modulare;
- espandibile;
- indipendente dalla tipologia di struttura;
- orientato al database;
- predisposto per integrazioni esterne.

Ogni nuova funzione dovrà rispettare questi principi.

---

# Obiettivi

Realizzare un PMS professionale che consenta la gestione completa di:

- strutture;
- unità ricettive;
- clienti;
- prenotazioni;
- disponibilità;
- planning;
- pagamenti;
- check-in;
- check-out;
- report;
- integrazioni.

---

# Principi fondamentali

## 1. Il database è il cuore del sistema

Il codice non deve contenere dati di configurazione.

Devono essere gestiti tramite database:

- strutture;
- unità ricettive;
- utenti;
- servizi;
- promozioni;
- tariffe;
- canali;
- impostazioni;
- automazioni.

---

## 2. Architettura Multi-Struttura

Il PMS dovrà poter gestire contemporaneamente:

- una sola struttura;
- dieci strutture;
- cento strutture.

L'aggiunta di una nuova struttura dovrà avvenire esclusivamente tramite l'interfaccia del programma.

Non dovrà mai richiedere modifiche al codice.

---

## 3. Unità Ricettive

Il PMS utilizza il concetto di "Unità Ricettiva" invece di "Alloggio".

Una unità può rappresentare:

- villa;
- appartamento;
- camera;
- suite;
- bungalow;
- trullo;
- pajara;
- piazzola;
- qualsiasi altra tipologia.

---

## 4. Cliente Unico

Ogni cliente deve esistere una sola volta nel database.

Lo storico comprenderà:

- prenotazioni;
- soggiorni;
- pagamenti;
- preferenze;
- recensioni;
- comunicazioni;
- documenti.

---

## 5. Prenotazioni

Ogni prenotazione collega automaticamente:

Cliente

↓

Struttura

↓

Unità Ricettiva

↓

Tariffa

↓

Pagamento

↓

Workflow

---

## 6. Disponibilità

La disponibilità viene calcolata automaticamente.

Non devono esistere dati duplicati.

Il planning rappresenta la vista grafica delle prenotazioni.

---

## 7. Tariffe

Le tariffe sono gestite esclusivamente tramite database.

Il codice non dovrà contenere prezzi.

---

## 8. Moduli indipendenti

Il PMS sarà composto da moduli indipendenti.

Esempi:

- Dashboard
- Clienti
- Prenotazioni
- Planning
- Disponibilità
- Tariffe
- Pagamenti
- Report
- Configurazione

Ogni modulo dovrà poter essere sviluppato senza modificare gli altri.

---

## 9. Integrazioni

Le integrazioni saranno gestite tramite connettori dedicati.

Esempi:

- Booking.com
- Airbnb
- Vrbo
- Expedia
- Google
- Stripe
- WhatsApp
- Email
- Alloggiati Web
- ISTAT

L'uso delle API ufficiali sarà preferito ogni volta che sarà possibile.

Il protocollo iCal dovrà essere considerato un sistema di compatibilità e non il metodo principale di sincronizzazione.

---

## 10. Automazioni

Il PMS dovrà automatizzare il maggior numero possibile di operazioni ripetitive.

Esempi:

- conferme;
- promemoria;
- richieste saldo;
- check-in;
- check-out;
- recensioni;
- fidelizzazione cliente.

---

# Struttura logica

ACCOUNT

└── STRUTTURE

  ├── UNITÀ RICETTIVE

  ├── PRENOTAZIONI

  ├── TARIFFE

  ├── DISPONIBILITÀ

  ├── PLANNING

  ├── HOUSEKEEPING

  ├── MANUTENZIONI

  └── DOCUMENTI

CLIENTI

PAGAMENTI

REPORT

CONFIGURAZIONE

INTEGRAZIONI

---

# Regole di sviluppo

Ogni nuova funzione dovrà:

- risolvere un problema reale;
- evitare duplicazioni di codice;
- essere documentata;
- essere riutilizzabile;
- essere configurabile;
- rispettare la modularità del sistema.

---

# Roadmap

Versione 1

Realizzazione del nucleo del PMS.

Versione 2

Automazioni.

Versione 3

Booking Engine.

Versione 4

Channel Manager.

Versione 5

AI Assistant.

---

# Visione finale

L'obiettivo è realizzare un PMS professionale in grado di crescere negli anni insieme all'attività ricettiva.

L'architettura dovrà permettere l'aggiunta di nuove strutture, nuovi moduli e nuove integrazioni senza modificare le fondamenta del sistema.

Il software dovrà adattarsi alle esigenze dell'utente, mantenendo nel tempo semplicità, stabilità e facilità di manutenzione.
