 # Udsalgstracker

 Dette projekt er en Chrome extension med en Python-baseret backend til at tracke udsalg og sende notifikationer.

 ## Projektstruktur

 - `extension/`: Chrome extension-kode
	 - `manifest.json`
	 - `background/`
	 - `content/`
	 - `popup/`
	 - `assets/`
 - `backend/`: Python backend
	 - `database/`
	 - `main.py/`
	 - `notifier/`
	 - `scraper/`
 - `requirements.txt`: Python-pakker
 - `.env`: hemmelige værdier (API-nøgler, mailoplysninger)
 - `.env.example`: eksempel på miljøvariabler
 - `.gitignore`: filer og mapper der ikke skal i versionsstyring

 ## Fase 1: Fundament

 Denne fase indeholder:
 - Projektstruktur på plads
 - Basale krav til Python-pakker
 - Git-ignorering af hemmelige filer
 - `.env.example` som reference

 ## Næste skridt

 Når fundamentet er klar, kan du begynde at implementere:
 1. Chrome extension manifest og UI
 2. Python backend scraper og notifikationslogik
 3. Kommunikation mellem extension og backend
