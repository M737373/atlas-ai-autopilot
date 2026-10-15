import os, sqlite3, json
from datetime import datetime
import streamlit as st

APP_TITLE = "ATLAS AI AUTOPILOT"
DB_PATH = os.getenv("ATLAS_DB_PATH", "atlas.db")

st.set_page_config(page_title=APP_TITLE, page_icon="🤖", layout="wide")

# Simple dashboard gate for the hosted starter. Set ATLAS_DASHBOARD_PASSWORD
# as a secret environment variable in the hosting provider before deployment.
_dashboard_password = os.getenv("ATLAS_DASHBOARD_PASSWORD", "")
if not _dashboard_password:
    st.error("Dashboard noch gesperrt: Der Betreiber muss ATLAS_DASHBOARD_PASSWORD als geheime Umgebungsvariable setzen.")
    st.stop()
if not st.session_state.get("atlas_authenticated", False):
    st.title("🔐 ATLAS AI AUTOPILOT")
    st.write("Bitte gib dein Dashboard-Passwort ein.")
    entered_password = st.text_input("Dashboard-Passwort", type="password")
    if st.button("Anmelden", type="primary"):
        if entered_password and entered_password == _dashboard_password:
            st.session_state["atlas_authenticated"] = True
            st.rerun()
        else:
            st.error("Passwort stimmt nicht.")
    st.stop()

st.title("🤖 ATLAS AI AUTOPILOT")
st.caption("KI-Serviceagentur: Angebote, Kunden-Leads, Auftragsentwürfe und Marketing. Externe Aktionen bleiben unter deiner Kontrolle.")


def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT, agent TEXT, title TEXT, status TEXT, details TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, kind TEXT, amount REAL, note TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS ideas (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT, name TEXT, audience TEXT, problem TEXT, status TEXT, notes TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT, company TEXT, contact TEXT, email TEXT, niche TEXT, need TEXT, status TEXT, notes TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT, client_name TEXT, service TEXT, brief TEXT, status TEXT, deliverable TEXT)")
    conn.commit()
    return conn

conn = db()

def add_task(agent, title, details, status="Entwurf"):
    conn.execute("INSERT INTO tasks (created_at, agent, title, status, details) VALUES (?, ?, ?, ?, ?)",
                 (datetime.now().isoformat(timespec="seconds"), agent, title, status, details))
    conn.commit()

def ai_available():
    return bool(os.getenv("OPENAI_API_KEY"))

def ask_ai(system_prompt, user_prompt):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return "Kein OPENAI_API_KEY gefunden. Trage deinen Schlüssel lokal in die Umgebungsvariable ein und starte die App neu."
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.7,
        )
        return resp.choices[0].message.content or "Keine Antwort erhalten."
    except Exception as e:
        return f"KI-Aufruf fehlgeschlagen: {e}"

# Sidebar
st.sidebar.header("Einrichtung")
st.sidebar.write("KI-API: " + ("✅ Schlüssel erkannt" if ai_available() else "⚪ Noch nicht eingerichtet"))
st.sidebar.info("Dieses Starterprojekt veröffentlicht nichts automatisch, schaltet keine Anzeigen und führt keine Zahlungen aus. Erst testen und Freigaben einrichten.")
st.sidebar.caption("Niemals Bank-Login, PIN oder TAN hier eintragen.")

# Metrics
rows = conn.execute("SELECT kind, COALESCE(SUM(amount),0) FROM transactions GROUP BY kind").fetchall()
amounts = {k: float(v) for k, v in rows}
income = amounts.get("Einnahme", 0.0)
expenses = amounts.get("Ausgabe", 0.0)
task_count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
ideas_count = conn.execute("SELECT COUNT(*) FROM ideas").fetchone()[0]
c1,c2,c3,c4 = st.columns(4)
c1.metric("Erfasste Einnahmen", f"€ {income:,.2f}")
c2.metric("Erfasste Ausgaben", f"€ {expenses:,.2f}")
c3.metric("Saldo (erfasst)", f"€ {income-expenses:,.2f}")
c4.metric("Aufgaben / Ideen", f"{task_count} / {ideas_count}")

page = st.sidebar.radio("Bereich", ["Übersicht", "Service-Angebot erstellen", "Kunden-Leads", "Auftragslieferung erstellen", "Marketing erstellen", "Geschäftsidee prüfen", "Produkt erstellen", "Aufgaben & Freigaben", "Finanzen", "Setup-Anleitung"])

if page == "Übersicht":
    st.subheader("Startplan")
    st.markdown("""
    **B2-Modus: KI-Dienstleistungen verkaufen, mit maximal sinnvoller Automatisierung.**

    1. Eine klare Zielgruppe und ein eng umrissenes Service-Angebot auswählen.
    2. Beispielarbeiten und ein transparentes Angebot erstellen.
    3. Interessenten im Lead-CRM erfassen und passende, individuelle Kontaktentwürfe erstellen.
    4. Kundenbriefings in konkrete Lieferaufgaben umwandeln.
    5. Qualität prüfen, Ergebnisse freigeben und erst danach an Kunden senden.
    """)
    st.warning("Umsatz ist nicht garantiert. Starte mit einem kleinen Test und gib kein Werbebudget frei, bevor Nachfrage nachgewiesen ist.")
    recent = conn.execute("SELECT created_at, agent, title, status FROM tasks ORDER BY id DESC LIMIT 8").fetchall()
    st.subheader("Letzte Aufgaben")
    if recent:
        st.dataframe([{"Zeit": r[0], "Agent": r[1], "Aufgabe": r[2], "Status": r[3]} for r in recent], use_container_width=True, hide_index=True)
    else:
        st.write("Noch keine Aufgaben. Nutze links die Bereiche, um erste Entwürfe zu erstellen.")

elif page == "Service-Angebot erstellen":
    st.subheader("🧩 Service-Agent: ein verkaufbares KI-Angebot entwickeln")
    niche = st.text_input("Zielgruppe / Branche", placeholder="z. B. lokale Handwerksbetriebe")
    service = st.selectbox("Leistung", ["Social-Media-Content-Paket", "Blog- und Website-Texte", "Produktbeschreibungen für Onlineshops", "Kunden-FAQ und Wissensdatenbank", "Lead-Recherche und CRM-Aufbereitung", "E-Mail-Newsletter", "Individuelles KI-Content-Paket"])
    experience = st.selectbox("Dein Erfahrungsstand", ["Anfänger, noch keine Referenzen", "Grundkenntnisse", "Erfahrene Umsetzung"])
    weekly_hours = st.selectbox("Zeit, die du selbst investieren kannst", ["1–3 Stunden", "3–5 Stunden", "5–10 Stunden", "10+ Stunden"])
    if st.button("Angebot und Preise entwickeln", type="primary"):
        if not niche.strip():
            st.error("Bitte eine Zielgruppe angeben.")
        else:
            prompt = f"Entwickle ein realistisches, kleines B2B-Serviceangebot für den deutschen Markt. Zielgruppe: {niche}. Leistung: {service}. Erfahrungsstand: {experience}. Verfügbare Zeit: {weekly_hours}. Liefere: (1) konkretes Kundenproblem, (2) klar abgegrenzte Leistung, (3) drei Pakete mit vorsichtigen Testpreisen in Euro und exakten Lieferumfängen, (4) was ausdrücklich nicht enthalten ist, (5) Ablauf und benötigte Kundenzulieferungen, (6) Qualitätscheckliste, (7) 3 risikoarme Nachfrage-Tests. Kennzeichne Preise als Hypothesen, keine Umsatzversprechen, keine erfundenen Marktstatistiken. Keine Rechts- oder Steuerbehauptungen."
            result = ask_ai("Du bist ein pragmatischer B2B-Angebotsberater. Keine Umsatzgarantien, keine unbelegten Behauptungen. Achte auf realistische Lieferumfänge und klare Grenzen.", prompt)
            add_task("Service-Agent", f"Serviceangebot: {service} für {niche}", result, "Prüfung erforderlich")
            st.markdown(result)
            st.download_button("Angebot als TXT herunterladen", result, file_name="atlas_serviceangebot.txt", mime="text/plain")

elif page == "Kunden-Leads":
    st.subheader("📇 Lead-CRM")
    st.caption("Leads werden manuell erfasst. Nutze nur rechtmäßig erhobene Kontaktdaten und beachte Datenschutz- und Werberegeln. Es werden keine Nachrichten automatisch versendet.")
    with st.form("lead_form"):
        company = st.text_input("Unternehmen / Kontaktname")
        contact = st.text_input("Ansprechpartner (optional)")
        email = st.text_input("E-Mail (optional)")
        niche = st.text_input("Branche")
        need = st.text_area("Vermuteter Bedarf / öffentlich bekannte Anknüpfung")
        status = st.selectbox("Status", ["Neu", "Zu prüfen", "Kontaktentwurf erstellt", "Kontaktiert", "Antwort erhalten", "Kunde", "Kein Interesse"])
        notes = st.text_area("Notizen")
        if st.form_submit_button("Lead speichern"):
            if not company.strip():
                st.error("Unternehmen oder Kontaktname ist erforderlich.")
            else:
                conn.execute("INSERT INTO leads (created_at,company,contact,email,niche,need,status,notes) VALUES (?,?,?,?,?,?,?,?)", (datetime.now().isoformat(timespec="seconds"), company, contact, email, niche, need, status, notes))
                conn.commit()
                st.success("Lead gespeichert.")
                st.rerun()
    leads = conn.execute("SELECT id,company,contact,email,niche,need,status,notes FROM leads ORDER BY id DESC").fetchall()
    if leads:
        st.dataframe([{"ID":r[0],"Unternehmen":r[1],"Kontakt":r[2],"E-Mail":r[3],"Branche":r[4],"Bedarf":r[5],"Status":r[6],"Notizen":r[7]} for r in leads], use_container_width=True, hide_index=True)
        lead_ids = [r[0] for r in leads]
        selected_id = st.selectbox("Lead für individuellen Kontaktentwurf auswählen", lead_ids, format_func=lambda x: next(f"#{r[0]} · {r[1]} · {r[6]}" for r in leads if r[0] == x))
        chosen = next(r for r in leads if r[0] == selected_id)
        offer = st.text_input("Dein Angebot für diesen Lead", placeholder="z. B. 8 Social-Media-Beiträge pro Monat", key="lead_offer")
        if st.button("Kontaktentwurf erstellen"):
            prompt = f"Erstelle einen kurzen, individuellen und ehrlichen B2B-Kontaktentwurf auf Deutsch. Unternehmen: {chosen[1]}. Kontakt: {chosen[2]}. Branche: {chosen[4]}. Öffentlich begründeter Anknüpfungspunkt / vermuteter Bedarf: {chosen[5]}. Angebot: {offer}. Keine falschen Behauptungen, keine fingierte Vertrautheit, kein Druck, keine erfundenen Referenzen. Keine automatische Versendung. Formuliere eine Betreffzeile und Nachricht sowie einen Hinweis, welche Fakten vor dem Versand geprüft werden müssen."
            result = ask_ai("Du verfasst respektvolle, individuelle Geschäftskommunikation. Vermeide Massen-Spam, Täuschung und unbelegte Aussagen.", prompt)
            add_task("Sales-Agent", f"Kontaktentwurf für {chosen[1]}", result, "Prüfung erforderlich")
            st.markdown(result)
            st.download_button("Kontaktentwurf herunterladen", result, file_name="kontaktentwurf.txt", mime="text/plain")
    else:
        st.info("Noch keine Leads erfasst. Starte mit wenigen, passenden Unternehmen und überprüfe die rechtliche Zulässigkeit einer Kontaktaufnahme.")

elif page == "Auftragslieferung erstellen":
    st.subheader("📦 Delivery-Agent: Kundenbriefing in einen Lieferentwurf umwandeln")
    client_name = st.text_input("Kunde / Projektname")
    deliver_service = st.selectbox("Lieferart", ["Social-Media-Plan mit Beiträgen", "Blogartikel", "Website-Texte", "Produktbeschreibungen", "FAQ / Wissensdatenbank", "Newsletter", "Anderes"])
    brief = st.text_area("Kundenbriefing", placeholder="Ziel, Zielgruppe, Tonalität, Umfang, Fakten, verbotene Aussagen, Format ...", height=180)
    if st.button("Lieferentwurf erstellen", type="primary"):
        if not client_name.strip() or not brief.strip():
            st.error("Bitte Projektname und Briefing ausfüllen.")
        else:
            prompt = f"Erstelle einen professionellen ERSTENTWURF für eine bezahlte B2B-Leistung. Kunde/Projekt: {client_name}. Lieferart: {deliver_service}. Kundenbriefing: {brief}. Halte dich eng an das Briefing. Erfinde keine Fakten, Quellen, Referenzen, Ergebnisse oder Kundenaussagen. Markiere fehlende Angaben als [KUNDE MUSS BESTÄTIGEN]. Am Ende: Qualitätscheckliste, offene Rückfragen und Fakten, die vor Auslieferung geprüft werden müssen. Schreibe in sauberem Deutsch."
            result = ask_ai("Du bist ein sorgfältiger Produktionsassistent einer kleinen KI-Serviceagentur. Ausgabe ist ein Entwurf, der vor Lieferung von einem Menschen geprüft werden muss.", prompt)
            conn.execute("INSERT INTO clients (created_at,client_name,service,brief,status,deliverable) VALUES (?,?,?,?,?,?)", (datetime.now().isoformat(timespec="seconds"), client_name, deliver_service, brief, "Prüfung erforderlich", result))
            conn.commit()
            add_task("Delivery-Agent", f"Lieferentwurf: {client_name} / {deliver_service}", result, "Prüfung erforderlich")
            st.markdown(result)
            st.download_button("Lieferentwurf herunterladen", result, file_name="kundenlieferung_entwurf.txt", mime="text/plain")
    projects = conn.execute("SELECT id,created_at,client_name,service,status FROM clients ORDER BY id DESC LIMIT 20").fetchall()
    if projects:
        st.subheader("Gespeicherte Projekte")
        st.dataframe([{"ID":r[0],"Datum":r[1],"Kunde":r[2],"Leistung":r[3],"Status":r[4]} for r in projects], use_container_width=True, hide_index=True)

elif page == "Geschäftsidee prüfen":
    st.subheader("🔎 Research-Agent: Geschäftsidee strukturieren")
    name = st.text_input("Idee / Produkt", placeholder="z. B. Haushaltsbudget-Vorlagen")
    audience = st.text_input("Zielgruppe", placeholder="z. B. Berufseinsteiger in Deutschland")
    problem = st.text_area("Welches Problem löst das Produkt?", placeholder="Beschreibe das konkrete Problem.")
    if st.button("Idee analysieren", type="primary"):
        if not name.strip() or not audience.strip() or not problem.strip():
            st.error("Bitte alle drei Felder ausfüllen.")
        else:
            prompt = f"Bewerte diese digitale Produktidee kritisch für den deutschen Markt. Trenne Fakten, Annahmen und offene Fragen. Erstelle: Zielkunden, Problemstärke, mögliche Konkurrenz-Suchbegriffe, Differenzierung, 3 günstige Nachfrage-Tests, Risiken und Go/No-Go-Kriterien. Erfinde keine Rechercheergebnisse und kennzeichne fehlende Live-Recherche ausdrücklich.\nIdee: {name}\nZielgruppe: {audience}\nProblem: {problem}"
            result = ask_ai("Du bist ein vorsichtiger Marktanalyse-Assistent. Keine Umsatzversprechen. Keine erfundenen Daten.", prompt)
            conn.execute("INSERT INTO ideas (created_at,name,audience,problem,status,notes) VALUES (?,?,?,?,?,?)", (datetime.now().isoformat(timespec="seconds"), name, audience, problem, "Zu prüfen", result))
            conn.commit()
            add_task("Research-Agent", f"Idee prüfen: {name}", result)
            st.markdown(result)
            st.success("Analyse gespeichert.")
    ideas = conn.execute("SELECT created_at,name,audience,status FROM ideas ORDER BY id DESC LIMIT 10").fetchall()
    if ideas:
        st.subheader("Gespeicherte Ideen")
        st.dataframe([{"Zeit":x[0],"Idee":x[1],"Zielgruppe":x[2],"Status":x[3]} for x in ideas], use_container_width=True, hide_index=True)

elif page == "Produkt erstellen":
    st.subheader("🛠️ Produkt-Agent: digitalen Produktentwurf erstellen")
    product = st.text_input("Produktidee", placeholder="z. B. Wochenplaner als PDF")
    audience = st.text_input("Für wen?", key="prod_audience")
    format_ = st.selectbox("Format", ["PDF-Leitfaden", "Arbeitsbuch", "Checkliste", "Vorlagenpaket", "Mini-Kurs-Gliederung", "E-Mail-Kurs"])
    detail = st.text_area("Besondere Anforderungen", placeholder="Ton, Umfang, Inhalte, Grenzen ...")
    if st.button("Produktentwurf erstellen", type="primary"):
        if not product.strip() or not audience.strip():
            st.error("Bitte Produktidee und Zielgruppe ausfüllen.")
        else:
            result = ask_ai("Du bist Produktentwickler für kleine digitale Produkte. Liefere einen originellen, klar strukturierten Entwurf. Erfinde keine fachlichen Fakten. Markiere Stellen, die geprüft werden müssen.", f"Erstelle einen brauchbaren ersten Entwurf für ein digitales Produkt. Produkt: {product}. Zielgruppe: {audience}. Format: {format_}. Anforderungen: {detail}. Enthalten sein sollen Titel, Nutzenversprechen ohne übertriebene Behauptungen, Inhaltsstruktur, Beispielinhalt, Qualitätscheckliste und nächste Validierungsschritte.")
            add_task("Produkt-Agent", f"Produktentwurf: {product}", result)
            st.markdown(result)
            st.download_button("Entwurf als TXT herunterladen", result, file_name="produktentwurf.txt", mime="text/plain")

elif page == "Marketing erstellen":
    st.subheader("📣 Marketing-Agent: Inhalte vorbereiten")
    product = st.text_input("Produkt / Angebot", placeholder="Was wird angeboten?")
    audience = st.text_input("Zielgruppe", key="marketing_audience")
    channel = st.selectbox("Kanal", ["Landingpage", "Instagram", "TikTok-Skript", "Pinterest", "E-Mail", "Blogartikel"])
    tone = st.selectbox("Stil", ["Sachlich und vertrauenswürdig", "Freundlich", "Direkt und verkaufsorientiert", "Fachlich"])
    if st.button("Marketingentwurf erstellen", type="primary"):
        if not product.strip() or not audience.strip():
            st.error("Bitte Angebot und Zielgruppe eintragen.")
        else:
            result = ask_ai("Du bist ein ethischer Marketing-Assistent. Keine falschen Versprechen, erfundenen Testimonials, künstliche Verknappung oder unbelegten Erfolgsbehauptungen. Werbung klar und ehrlich formulieren.", f"Erstelle einen Marketingentwurf. Angebot: {product}. Zielgruppe: {audience}. Kanal: {channel}. Stil: {tone}. Gib eine klare Überschrift, Nutzenargumente, Handlungsaufforderung und einen kurzen Fakten-/Rechtscheck. Nicht veröffentlichen, nur Entwurf.")
            add_task("Marketing-Agent", f"Marketing: {product} / {channel}", result)
            st.markdown(result)
            st.download_button("Marketingtext herunterladen", result, file_name="marketingentwurf.txt", mime="text/plain")

elif page == "Aufgaben & Freigaben":
    st.subheader("📋 Aufgaben und Freigaben")
    st.caption("In dieser Version werden Ergebnisse als Entwürfe gespeichert. Veröffentlichungen, Ausgaben und Kundenkommunikation sind nicht automatisiert.")
    tasks = conn.execute("SELECT id,created_at,agent,title,status,details FROM tasks ORDER BY id DESC").fetchall()
    if not tasks:
        st.write("Noch keine Aufgaben.")
    else:
        for t in tasks:
            with st.expander(f"#{t[0]} · {t[3]} · {t[4]}"):
                st.caption(f"{t[1]} | {t[2]}")
                st.text(t[5] or "")
                new_status = st.selectbox("Status", ["Entwurf", "Prüfung erforderlich", "Freigegeben", "Abgelehnt", "Erledigt"], index=["Entwurf", "Prüfung erforderlich", "Freigegeben", "Abgelehnt", "Erledigt"].index(t[4]) if t[4] in ["Entwurf", "Prüfung erforderlich", "Freigegeben", "Abgelehnt", "Erledigt"] else 0, key=f"status_{t[0]}")
                if st.button("Status speichern", key=f"save_{t[0]}"):
                    conn.execute("UPDATE tasks SET status=? WHERE id=?", (new_status, t[0]))
                    conn.commit()
                    st.rerun()

elif page == "Finanzen":
    st.subheader("💶 Einnahmen und Ausgaben erfassen")
    with st.form("finance_form"):
        kind = st.selectbox("Typ", ["Einnahme", "Ausgabe"])
        amount = st.number_input("Betrag in Euro", min_value=0.0, step=1.0, format="%.2f")
        note = st.text_input("Notiz", placeholder="z. B. Produktverkauf oder Hosting")
        submitted = st.form_submit_button("Buchung speichern")
        if submitted:
            conn.execute("INSERT INTO transactions (date,kind,amount,note) VALUES (?,?,?,?)", (datetime.now().date().isoformat(), kind, amount, note))
            conn.commit()
            st.success("Buchung gespeichert.")
    tx = conn.execute("SELECT date,kind,amount,note FROM transactions ORDER BY id DESC LIMIT 100").fetchall()
    if tx:
        st.dataframe([{"Datum":r[0],"Typ":r[1],"Betrag (€)":r[2],"Notiz":r[3]} for r in tx], use_container_width=True, hide_index=True)
    st.caption("Manuelle Übersicht, keine Buchhaltungs- oder Steuerberatung und keine automatische Bankanbindung.")

elif page == "Setup-Anleitung":
    st.subheader("⚙️ Einrichtung")
    st.markdown("""
    **B2-Modus: KI-Dienstleistungen**

    Nutze zuerst „Service-Angebot erstellen“, erfasse passende Kontakte unter „Kunden-Leads“ und erstelle aus echten Kundenbriefings unter „Auftragslieferung erstellen“ einen überprüfbaren Entwurf. Kontaktentwürfe und Lieferungen werden nicht automatisch versendet.

    **Lokal starten**

    1. Python 3.11 oder neuer installieren.
    2. Im Projektordner ein Terminal öffnen.
    3. Abhängigkeiten installieren: `pip install -r requirements.txt`
    4. Optional einen OpenAI-API-Schlüssel als Umgebungsvariable `OPENAI_API_KEY` hinterlegen.
    5. Starten: `streamlit run app.py`

    **Für den dauerhaften Onlinebetrieb** brauchst du einen Hosting-Anbieter. Lege API-Schlüssel dort als geheime Umgebungsvariablen ab, nicht im Quellcode und nicht in öffentlichen Repositories.

    **Zahlungen:** Diese Version nimmt keine Zahlungen entgegen. Für einen echten Shop musst du einen Zahlungsanbieter, Produktbedingungen, Impressum/Datenschutz, Widerrufs- und Steuerfragen passend zum Angebot einrichten. Bank-Login, PIN und TAN werden nicht benötigt.
    """)
    st.code("pip install -r requirements.txt\nstreamlit run app.py", language="bash")
    st.markdown("**Beispiel für Umgebungsvariablen** (nicht in eine öffentliche Datei schreiben):")
    st.code("OPENAI_API_KEY=dein_api_schluessel\nOPENAI_MODEL=gpt-4.1-mini", language="bash")

st.divider()
st.caption("ATLAS B2 Starter v0.2 · KI-Serviceagentur-Prototyp. Keine automatischen Nachrichten, Anzeigen, Bankzugriffe oder Zahlungsausführungen.")
