# PC Builder

**Studente:** Stefano Marri Malacrida, matricola 7136241<br>
**Tipo di progetto (Project Type):** Full-Stack Web Application e-commerce<br>
**Framework utilizzato (Framework):** Django

## Descrizione del progetto

Questo progetto è un'applicazione web e-commerce dedicata alla vendita di componenti hardware per computer, con una funzionalità aggiuntiva che guida passo dopo passo l'utente nella costruzione di un PC con componenti compatibili tra loro. Gli utenti possono navigare nel catalogo, utilizzare l'assemblatore guidato, gestire il carrello, applicare codici sconto, lasciare recensioni sui prodotti acquistati e completare e tracciare i propri ordini. È inoltre presente una dashboard gestionale dedicata allo Store Manager per la gestione di prodotti, categorie, ordini, recensioni e codici sconto.

> **NOTA:** L'assemblatore guidato simula la compabilità rilevando delle parole nel nome dei prodotti. Ovviamente non è realistico e non si troverebbe mai in un reale sito di vendita di componenti, ma è implementato a scopo puramente dimostrativo.

## Funzionalità principali per ruolo

### Utente Visitatore (non autenticato)

- Esplorazione del catalogo prodotti con ricerca per nome, filtri per categoria e prezzo, e ordinamento secondo più criteri.
- Visualizzazione dei dettagli dei prodotti e delle recensioni lasciate dagli altri utenti.
- Utilizzo del PC Builder (configuratore guidato) per creare un PC con componenti compatibili tra loro.
- Gestione del carrello salvato nella sessione; una volta effettuato il login, il carrello verrà salvato nel database e sarà accessibile anche da altri dispositivi con lo stesso account.
- Registrazione di un nuovo account e login.

### Utente Cliente (autenticato)

- Tutte le funzionalità del visitatore non autenticato.
- Inserimento di recensioni e valutazioni (stelle) sui prodotti acquistati.
- Modifica del proprio profilo utente (nome, cognome, email, indirizzo, città, CAP e telefono).
- Checkout del carrello con inserimento dei dati di spedizione.
- Applicazione di codici sconto per un importo fisso o in percentuale (es. `SCONTO10`, `PROMO20`). Un utente può utilizzare uno stesso codice sconto una sola volta.
- Storico degli ordini effettuati, di cui si può accedere ai dettagli in una pagina dedicata.

### Store Manager (ruolo manager)

- Accesso alla dashboard di amministrazione del negozio (`/dashboard/`).
- Gestione del catalogo prodotti: creazione, modifica ed eliminazione di prodotti e categorie.
- Gestione dei codici sconto, in percentuale o ad importo fisso: creazione, modifica ed eliminazione dei coupon utilizzabili dagli utenti.
- Gestione degli ordini: visualizzazione di tutti gli ordini effettuati dai clienti, aggiornamento dello stato di spedizione o cancellazione dell'ordine.
- Moderazione delle recensioni: possibilità di eliminare recensioni inappropriate.

### Amministratore (superuser)

- Accesso completo al pannello di amministrazione nativo di Django (`/admin/`).
- Gestione completa di utenti, gruppi, permessi e di tutti i dati del database.

## Installazione ed esecuzione locale

1. **Clonare il repository:**

   ```bash
   git clone https://github.com/Stefano299/Backend.git
   cd Backend
   ```

2. **Creare e attivare l'ambiente virtuale:**
   - Su Linux/macOS:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - Su Windows:
     ```cmd
     python -m venv .venv
     .venv\Scripts\activate
     ```

3. **Installare le dipendenze:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurare il database:**
   Nel repository è già incluso il database pre-popolato `db.sqlite3`. Non è necessario eseguire le migrazioni o creare un superuser da zero, a meno che non si voglia ricominciare da un database vuoto.
   Se si vuole ricreare il database da zero:

   ```bash
   # Rimuovere il file db.sqlite3 esistente, poi:
   python manage.py migrate
   python populate_db.py  # Per ripopolare i dati demo
   ```

5. **Avviare il server di sviluppo:**
   ```bash
   python manage.py runserver
   ```
   L'applicazione sarà accessibile all'indirizzo: `http://127.0.0.1:8000/`.

## Database SQLite e dati demo

Il database SQLite incluso nel repository si chiama **`db.sqlite3`**. Esso può essere ripopolato con i dati demo in qualsiasi momento tramite lo script `populate_db.py`.

Il database è già pre-popolato con:

- Categorie di componenti PC (Processori, Schede Madri, RAM, GPU, Alimentatori, Case, Dissipatori, Storage).
- Numerosi prodotti con prezzi, immagini (memorizzate in `media/`), descrizioni, sconti, recensioni e livelli di stock differenti.
- Alcuni codici sconto pronti all'uso: `SCONTO10` per uno sconto in percentuale del 10%, `PROMO20` di 20€ (sconto fisso) e `WELCOME5` di 5€ (sconto fisso).
- Recensioni lasciate dagli utenti su vari prodotti.
- Ordini effettuati dai clienti, di cui si può accedere ai dettagli in una pagina dedicata.
- Gli account utente elencati di seguito.

## Account Demo per i test

Di seguito sono riportate le credenziali degli utenti creati appositamente per testare l'applicazione:

- **Amministratore (Superuser):**
  - **Username:** `admin`
  - **Password:** `admin12345`
  - **Ruolo:** Amministratore di sistema (accesso al pannello di amministrazione di Django `/admin/`)

- **Store Manager:**
  - **Username:** `manager`
  - **Password:** `manager12345`
  - **Ruolo:** Gestore del negozio (accesso alla dashboard `/dashboard/`)

- **Clienti (Standard Users):**
  - **Username:** `bob` | **Password:** `bob12345`
  - **Username:** `bobby` | **Password:** `bobby12345`
  - **Username:** `taylor` | **Password:** `taylor12345`
  - **Username:** `john` | **Password:** `john12345`
  - **Username:** `alice` | **Password:** `alice12345`
  - **Username:** `charlie` | **Password:** `charlie12345`
  - **Ruolo:** Clienti del negozio

## Link per il deployment online

L'applicazione è pubblicata online al seguente indirizzo:
**https://backend-naap.onrender.com/**

## Scenario di test consigliato (Browser)

Per verificare le funzionalità principali del progetto si suggeriscono i seguenti test:

1. **Test Cliente (Catalogo):**
   - Aprire il sito e navigare nel catalogo prodotti.
   - Cercare e selezionare un prodotto di proprio interesse.
   - Aggiungere il prodotto al carrello direttamente dalla pagina dei dettagli.
   - Andare al carrello, inserire il codice sconto `SCONTO10` nell'apposito campo e cliccare su "Applica Sconto" per verificare il ricalcolo del prezzo totale (con detrazione del 10%).
   - Cliccare su "Procedi al Checkout" ed effettuare il login con le credenziali di un cliente (ad esempio `bob` / `bob12345`).
   - Inserire i dati di spedizione nella pagina di checkout e confermare l'ordine.
   - Andare nella pagina "I Miei Ordini" (dal menu utente) per visualizzare l'ordine appena creato e lo stato "Ordine ricevuto".
   - Lasciare una recensione (voto in stelle e commento) sul prodotto acquistato.

2. **Test Cliente (Assemblatore):**
   - Cliccare su "Assemblatore" nella barra di navigazione e completare tutti gli step selezionando un componente per ciascuna categoria.
   - Al termine, nella schermata di riepilogo finale della configurazione, cliccare su "Aggiungi tutto al carrello".
   - Procedere al pagamento come nel punto precedente.

> **NOTA:** Il carrello è memorizzato nel database per gli utenti autenticati, mentre per gli utenti non autenticati è memorizzato nella sessione. Dopo che un utente non autenticato effettua il login, il carrello viene salvato nel database.

> **NOTA:** Un utente può usare uno stesso codice sconto una sola volta..

3. **Test Permessi:**
   - Con l'utente `bob` ancora connesso, provare ad accedere all'indirizzo della dashboard del manager (`http://127.0.0.1:8000/dashboard/`). L'applicazione impedirà l'accesso mostrando una pagina di errore per permessi insufficienti.

4. **Test Store Manager:**
   - Effettuare il logout e successivamente il login con l'utente `manager` / `manager12345`.
   - Andare alla dashboard gestionale tramite l'apposito link nel menu o inserendo l'URL `/dashboard/`.
   - Nella sezione "Ordini", individuare l'ordine effettuato da `bob` nei punti precedenti, cliccare su "Modifica" e cambiare lo stato di spedizione.
   - Effettuare il logout, accedere nuovamente come `bob` ed andare sulla pagina "I Miei Ordini" per verificare che lo stato dell'ordine sia effettivamente aggiornato.
