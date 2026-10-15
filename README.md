# ATLAS AI AUTOPILOT – B2 Starter v0.2

KI-Serviceagentur-Prototyp für die Entwicklung von B2B-Serviceangeboten, Lead-Verwaltung, individuellen Kontaktentwürfen, Auftragslieferungen, Aufgabenfreigaben und manueller Finanzübersicht.

## Was enthalten ist
- Service-Agent: entwickelt ein abgegrenztes Angebot mit Testpreisen und Lieferumfang.
- Lead-CRM: erfasst passende Unternehmen und verwaltet den Kontaktstatus.
- Sales-Agent: erstellt individuelle Kontaktentwürfe zur manuellen Prüfung.
- Delivery-Agent: erstellt Lieferentwürfe aus Kundenbriefings.
- Aufgaben-/Freigabeübersicht und manuelle Finanzübersicht.
- SQLite-Speicherung; Docker-Startvorlage.

## Wichtig: Was nicht automatisch passiert
Dieses Projekt ist kein autonomes Unternehmen und garantiert keine Kunden oder Einnahmen. Es versendet keine E-Mails, veröffentlicht keine Inhalte, schaltet keine Anzeigen, nimmt keine Zahlungen an und greift nicht auf Bankkonten zu. Das ist bewusst so: Kontaktaufnahmen, Kundenlieferungen, Ausgaben und rechtlich relevante Aktionen müssen geprüft und freigegeben werden.

## Lokal starten
1. Python 3.11+ installieren.
2. Im Projektordner Terminal öffnen.
3. `pip install -r requirements.txt`
4. Optional `OPENAI_API_KEY` als Umgebungsvariable setzen.
5. `streamlit run app.py`
6. Browser-Adresse öffnen, die Streamlit ausgibt (normalerweise `http://localhost:8501`).

## Docker
1. Docker installieren.
2. `.env.example` nach `.env` kopieren und den KI-API-Schlüssel dort lokal eintragen.
3. `docker compose up --build -d` ausführen.
4. Dashboard unter `http://localhost:8501` öffnen.

Nicht ungeschützt direkt ins öffentliche Internet stellen. Für Onlinebetrieb HTTPS, Zugangsschutz, sichere Secret-Verwaltung, Backups, Updates und eine Firewall einrichten. API-Schlüssel nicht in GitHub oder öffentliche Dateien hochladen.

## Nächste Schritte vor echtem Geschäftsbetrieb
- Ein enges Angebot und eine Zielgruppe wählen.
- Beispielarbeiten erstellen und die Nachfrage mit wenigen Gesprächen testen.
- Gewerbe-, Steuer-, Datenschutz-, Impressums- und Vertragsfragen passend zum konkreten Angebot klären.
- Für Kontaktaufnahmen geltende Regeln für E-Mail-Werbung und Datenschutz prüfen. Keine unaufgeforderten Massenmails.
- Angebot, Lieferumfang, Änderungsrunden, Fristen und Preise schriftlich festhalten.
- Zahlungsanbieter separat einrichten, wenn Kunden bereit sind zu kaufen. Keine Bank-Logins, PINs oder TANs in dieses Projekt eingeben.

## API-Kosten
Die KI-API wird in der Regel separat nach Anbieter und Nutzung abgerechnet. Setze beim API-Anbieter ein kleines Nutzungslimit bzw. Budgetlimit, teste mit wenigen Anfragen und kontrolliere den Verbrauch. Hosting und Domain sind ebenfalls separate Kosten.


## Onlinebetrieb auf Render (geschützte Starter-Version)
- Dieses Projekt enthält `render.yaml` für einen Docker-Webdienst mit dauerhaftem Datenträger. Der Blueprint nutzt den kostenpflichtigen Starter-Plan; prüfe vor dem Erstellen den aktuellen Preis bei Render.
- Vor dem Start müssen in Render als geheime Umgebungsvariablen `OPENAI_API_KEY` und ein starkes `ATLAS_DASHBOARD_PASSWORD` gesetzt werden. Lade niemals `.env`, API-Schlüssel oder Passwörter in GitHub hoch.
- Das Passwort-Gate ist ein einfacher Schutz für einen privaten Prototyp, kein Ersatz für eine professionelle Benutzerverwaltung oder Sicherheitsprüfung. Teile die URL nicht öffentlich.
- Für API-Kosten beim Anbieter ein niedriges Budget-/Nutzungslimit setzen.
