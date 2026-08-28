"""Skalantech Hub — SEO landing page content.

Jede Seite adressiert eine klar getrennte Suchintention. Die Struktur ist
identisch (H1 → Problem → Lösung → Einsatzmöglichkeiten → Vorgehen →
Technologien → Vorteile → FAQ → CTA), die Inhalte sind pro Seite substanziell
unterschiedlich. Keine erfundenen Referenzen, Kunden oder Kennzahlen.
"""

from app.branchen import LANDING_BRANCHEN

LANDING_PAGES = {
    "it-infrastruktur": {
        "nav_label": "IT-Infrastruktur",
        "breadcrumb": "IT-Infrastruktur für Unternehmen",
        "title": "IT-Infrastruktur für Unternehmen – Aufbau, Optimierung & Betrieb | Skalantech",
        "description": "Stabile IT-Infrastruktur für KMU: Server, Docker, Netzwerk, Monitoring und Backup – geplant, umgesetzt und betreut von Skalantech in Köln.",
        "cases_heading": "Wo stabile Infrastruktur den Unterschied macht.",
        "h1": "IT-Infrastruktur, auf die sich Ihr Betrieb verlassen kann.",
        "lead": "Server, Netzwerk, Monitoring, Backup – wenn die technische Basis nicht stabil ist, helfen weder neue Tools noch KI. Skalantech baut, optimiert und betreibt die Infrastruktur, die Ihr Unternehmen für automatisierte Abläufe braucht.",
        "problem_title": "Typische Ausgangslage",
        "problem": [
            "Systeme wachsen über Jahre organisch, ohne dass jemand das Gesamtbild im Blick hat.",
            "Ausfälle und langsame Anwendungen kosten Zeit – und Vertrauen im Team.",
            "Backups existieren, wurden aber nie getestet. Ein Ernstfall wäre teuer.",
            "Neue Anforderungen (Cloud, KI, Automatisierung) brauchen eine stabile Grundlage.",
        ],
        "solution_title": "Was Skalantech dafür tut",
        "solution": [
            "Strukturierte Bestandsaufnahme Ihrer Umgebung – Server, Virtualisierung, Netzwerk, Microsoft 365, Cloud.",
            "Aufbau und Modernisierung mit Docker, Linux und bewährten Open-Source-Komponenten.",
            "Monitoring, Alarmierung und dokumentierte Backup- und Wiederherstellungskonzepte.",
            "Saubere, wartbare Architektur statt Insellösungen – damit spätere Automatisierung nicht an der Basis scheitert.",
        ],
        "use_cases": [
            ("Server & Virtualisierung", "Migration, Konsolidierung und Betrieb von physischen und virtuellen Servern (VMware, Hyper-V, Linux)."),
            ("Docker & Container", "Containerisierte Dienste mit definierten, reproduzierbaren Deployments statt manueller Installationen."),
            ("Netzwerk & Sicherheit", "Segmentierung, sichere Fernzugriffe (z. B. Tailscale) und Zugriffskonzepte ohne öffentliche Ports."),
            ("Monitoring & Backup", "Frühwarnsysteme, geprüfte Wiederherstellung und dokumentierte Betriebsprozesse."),
        ],
        "process": [
            ("Aufnahme", "Systeme, Abhängigkeiten und Risiken werden erfasst und priorisiert."),
            ("Zielbild", "Architektur und Technologie werden auf Team, Budget und Betrieb ausgelegt."),
            ("Umsetzung", "In kleinen, prüfbaren Schritten – mit Tests und sauberer Übergabe."),
            ("Betrieb", "Monitoring, Wartung und Weiterentwicklung – sofern gewünscht."),
        ],
        "tech": ["Linux", "Docker", "VMware / Hyper-V", "Microsoft 365", "Azure", "Tailscale", "Caddy", "Python"],
        "benefits": [
            "Eine verlässliche Basis für Automatisierung und KI.",
            "Weniger Ausfälle, klare Verantwortlichkeiten, dokumentierter Stand.",
            "Open-Source-first: keine unnötigen Lizenz- und Vendor-Kosten.",
            "Betreuung aus einer Hand – kein Ticket-Blackbox-Gefühl.",
        ],
        "faqs": [
            ("Arbeiten Sie auch mit bestehenden, gewachsenen Umgebungen?", "Ja. Gewachsene Umgebungen werden zuerst strukturiert aufgenommen. Daraus entsteht ein realistischer Plan für Stabilisierung, Migration oder schrittweise Modernisierung."),
            ("Setzen Sie nur auf Open Source?", "Nein. Open Source wird bevorzugt geprüft, wenn es fachlich und wirtschaftlich passt. Cloud- und Microsoft-Dienste werden dort eingesetzt, wo sie den größeren Nutzen bieten."),
            ("Wie schnell ist eine Infrastruktur-Modernisierung umsetzbar?", "Das hängt von Umfang und Risikobereitschaft ab. In der Regel beginnt die Zusammenarbeit mit einer Aufnahme, danach wird der erste konkrete Schritt priorisiert."),
        ],
        "related": ["ki-integration", "n8n-automatisierung", "websites-apps"],
    },
    "ki-integration": {
        "nav_label": "KI-Integration",
        "breadcrumb": "KI-Integration für Unternehmen",
        "title": "KI-Integration für Unternehmen – KI in bestehende Systeme bringen | Skalantech",
        "description": "KI sinnvoll in bestehende Systeme integrieren: LLMs, APIs, Dokumentenanalyse und Datenanbindung – mit klarem Datenschutz und ohne Blackbox. Skalantech.",
        "cases_heading": "Wo KI-Integration konkret wird.",
        "h1": "KI in Ihre bestehenden Systeme integrieren – nicht daneben.",
        "lead": "Die meisten Unternehmen brauchen kein eigenes KI-Produkt. Sie brauchen KI, die mit vorhandenen Systemen, Daten und Prozessen zusammenarbeitet. Skalantech verbindet LLMs und Analyse-Werkzeuge über APIs sauber mit Ihrer IT.",
        "problem_title": "Warum KI-Projekte oft scheitern",
        "problem": [
            "KI-Tools werden getestet, bleiben aber Einzellösungen ohne Anbindung an echte Daten.",
            "Bestehende Systeme sprechen nicht miteinander – Daten liegen verstreut in Dateien, E-Mails und Fachanwendungen.",
            "Unklarheit über Datenschutz: Welche Daten dürfen überhaupt an externe KI-Dienste?",
            "Fehlende technische Anbindung: APIs, Webhooks und Schnittstellen sind vorhanden, aber ungenutzt.",
        ],
        "solution_title": "Was Skalantech dafür tut",
        "solution": [
            "Use-Case-Analyse: Welche Prozesse profitieren wirklich von KI – und welche nicht?",
            "Anbindung von LLMs und KI-Diensten an Ihre Systeme über APIs, Webhooks und Datenbanken.",
            "Dokumenten- und Informationsanalyse mit RAG – auf Basis Ihrer eigenen, kontrollierten Daten.",
            "Klare Datenschutz-Bewertung: Cloud-KI, lokale Modelle oder Hybrid – je nach Daten und Anforderung.",
        ],
        "use_cases": [
            ("Dokumentenanalyse", "Verträge, Rechnungen, Handbücher: relevante Informationen automatisch extrahieren und strukturieren."),
            ("Wissenssuche im Unternehmen", "Interne Dokumente über eine KI-gestützte Suche beantworten lassen – ohne dass Daten das Haus verlassen."),
            ("E-Mail- und Ticket-Klassifizierung", "Eingehende Anfragen automatisch erkennen, priorisieren und an die richtige Stelle weiterleiten."),
            ("Datenauswertung", "Zahlen aus Berichten und Tabellen zusammenfassen und Entscheidern verständlich aufbereiten."),
        ],
        "process": [
            ("Use-Case prüfen", "Gemeinsam wird ein konkretes Anwendungsszenario mit messbarem Nutzen ausgewählt."),
            ("Daten & Systeme ansehen", "Welche Datenquellen existieren, welche Qualität haben sie, wie werden sie angebunden?"),
            ("Prototyp bauen", "Eine kleine, echte Lösung – schnell, testbar, ohne Großprojekt."),
            ("Produktiv integrieren", "Robuste Anbindung, Absicherung, Dokumentation und Übergabe an Ihr Team."),
        ],
        "tech": ["Python", "OpenAI / LLM-APIs", "RAG", "APIs & Webhooks", "n8n", "Microsoft Copilot", "SQL", "Docker"],
        "benefits": [
            "KI arbeitet mit Ihren echten Daten – nicht mit allgemeinem Wissen.",
            "Kontrollierter Datenschutz statt Grauzone.",
            "Kleine, bewertbare Schritte statt Riskant-Big-Bang.",
            "Integration in den laufenden Betrieb, ohne Parallelwelten.",
        ],
        "faqs": [
            ("Dürfen unsere Unternehmensdaten an Cloud-KI gehen?", "Nur wenn das vertraglich und datenschutzrechtlich sauber ist. Für sensible Daten gibt es lokale Modelle oder hybride Ansätze – das wird vorab bewertet."),
            ("Brauchen wir dafür ein eigenes Data-Science-Team?", "Nein. Für die meisten Anwendungen reichen APIs, Workflows und eine saubere Datenanbindung. Genau dort setzt Skalantech an."),
            ("Ab wann lohnt sich ein KI-Use-Case?", "Wenn ein wiederkehrender Prozess viel manuelle Zeit kostet und klare Regeln oder Muster enthält. Die Use-Case-Analyse beantwortet das konkret."),
        ],
        "related": ["lokale-ki", "ki-agenten", "branchen-handwerk"],
    },
    "ki-automatisierung": {
        "nav_label": "KI-Automatisierung",
        "breadcrumb": "Geschäftsprozesse automatisieren",
        "title": "KI-Automatisierung für Geschäftsprozesse – weniger manuelle Arbeit | Skalantech",
        "description": "Geschäftsprozesse mit KI automatisieren: wiederkehrende Aufgaben wie Rechnungen, E-Mails, Berichte und Datenübertragung – zuverlässig und dokumentiert. Skalantech.",
        "cases_heading": "Prozesse, die sich sofort automatisieren lassen.",
        "h1": "Schluss mit manueller Arbeit. Ihre Prozesse laufen automatisiert.",
        "lead": "Rechnungen abtippen, Daten zwischen Systemen übertragen, Berichte zusammenstellen – solche Aufgaben fressen täglich Stunden. Skalantech automatisiert genau diese Abläufe: zuverlässig, nachvollziehbar und ohne dass Ihr Team die Kontrolle verliert.",
        "problem_title": "Wo manuelle Arbeit Ihr Unternehmen ausbremst",
        "problem": [
            "Mitarbeitende verbringen Zeit mit Übertragen, Abtippen und Zusammenstellen statt mit wertschöpfender Arbeit.",
            "Manuelle Prozesse sind fehleranfällig – und Fehler kosten oft mehr als die Automatisierung.",
            "Wissen über Abläufe steckt in Köpfen statt in dokumentierten, automatisierten Prozessen.",
            "Daten liegen in getrennten Systemen, die nie miteinander verbunden wurden.",
        ],
        "solution_title": "Was Skalantech dafür tut",
        "solution": [
            "Prozessanalyse: Welche Abläufe eignen sich für Automatisierung – und wo lohnt sie sich nicht?",
            "Aufbau automatisierter Workflows über n8n, APIs und Webhooks – zwischen Ihren vorhandenen Tools.",
            "KI-Unterstützung dort, wo Regeln allein nicht reichen: Dokumente, E-Mails, unstrukturierte Daten.",
            "Überwachung, Fehlerbehandlung und klare Dokumentation – damit die Automation nicht zur Blackbox wird.",
        ],
        "use_cases": [
            ("Rechnungs- und Belegverarbeitung", "Eingangsrechnungen automatisch erfassen, prüfen und im System ablegen."),
            ("Berichtserstellung", "Kennzahlen aus mehreren Quellen automatisch sammeln und als Bericht aufbereiten."),
            ("E-Mail-Workflows", "Eingehende Anfragen klassifizieren, beantworten und an die richtige Abteilung routen."),
            ("Datenabgleich & Übertragung", "Stammdaten und Dokumente zwischen CRM, ERP, Tabellen und Dateiablagen synchronisieren."),
        ],
        "process": [
            ("Prozess wählen", "Ein Ablauf mit klarem Zeitaufwand und messbarem Nutzen wird ausgewählt."),
            ("Ist-Zustand dokumentieren", "Schritte, Systeme und Ausnahmen werden sichtbar gemacht."),
            ("Workflow bauen", "Automatisierung mit n8n/APIs, inklusive Fehlerbehandlung und Protokollierung."),
            ("Übergeben", "Ihr Team versteht den Ablauf, kann ihn steuern und weiterentwickeln."),
        ],
        "tech": ["n8n", "APIs & Webhooks", "Python", "Microsoft Power Automate", "KI/LLMs", "SQL", "Docker"],
        "benefits": [
            "Weniger manuelle Arbeit – nachweisbar in Zeit gespart pro Woche.",
            "Fehlerreduktion durch konsistente, dokumentierte Abläufe.",
            "Skalierbar: einmal gebaut, läuft der Workflow ohne Zusatzkosten.",
            "Ihr Team behält die Kontrolle – keine Automatisierung gegen die Mitarbeiter.",
        ],
        "faqs": [
            ("Welche Prozesse eignen sich für Automatisierung?", "Wiederkehrende, regelbasierte Aufgaben mit klarem Anfang und Ende. Die Prozessanalyse zeigt, welche Abläufe sich wirklich lohnen."),
            ("Was ist, wenn ein automatisierter Prozess Fehler macht?", "Workflows werden mit Fehlerbehandlung, Protokollierung und Alarmierung gebaut. Bei Abweichungen wird der Mensch informiert – nichts passiert still."),
            ("Müssen wir unsere Systeme dafür umstellen?", "Nein. Die Automatisierung läuft über die vorhandenen Schnittstellen. Bestehende Systeme bleiben in Betrieb."),
        ],
        "related": ["n8n-automatisierung", "ki-agenten", "websites-apps"],
    },
    "ki-agenten": {
        "nav_label": "KI-Agenten",
        "breadcrumb": "KI-Agenten für Unternehmen",
        "title": "KI-Agenten für Unternehmen – Aufgaben autonom erledigen | Skalantech",
        "description": "KI-Agenten für Unternehmen: Agenten, die recherchieren, analysieren, dokumentieren und Workflows ausführen – mit Ihren Daten, Ihren Regeln, Ihrer Kontrolle. Skalantech.",
        "cases_heading": "Aufgaben, die ein KI-Agent übernehmen kann.",
        "h1": "KI-Agenten, die Aufgaben wirklich erledigen.",
        "lead": "Ein KI-Agent ist mehr als ein Chatbot: Er bekommt ein Ziel, nutzt Werkzeuge, greift auf Daten zu und liefert ein Ergebnis. Skalantech konzipiert und baut KI-Agenten für konkrete Unternehmensaufgaben – begrenzt, überwachbar und produktiv.",
        "problem_title": "Vom Chatbot zum produktiven Agenten",
        "problem": [
            "Generische Chatbots liefern Antworten, aber keine Ergebnisse für Ihre Prozesse.",
            "Wissen liegt in Dokumenten, aber niemand kann es systematisch nutzen.",
            "Wiederkehrende Recherche- und Dokumentationsaufgaben binden Fachkräfte.",
            "Ohne klare Grenzen und Kontrolle sind Agenten ein Risiko statt ein Gewinn.",
        ],
        "solution_title": "Was Skalantech dafür tut",
        "solution": [
            "Use-Case-Design: Welche Aufgabe soll der Agent übernehmen – mit welchem Ergebnis, welchen Grenzen?",
            "Aufbau von Agenten mit RAG auf Ihrer Wissensbasis: Dokumente, Handbücher, interne Standards.",
            "Anbindung an Werkzeuge und Systeme: Suche, APIs, Dateiablagen, Workflows.",
            "Absicherung: Rechte, Limits, Protokollierung und menschliche Freigabe an kritischen Punkten.",
        ],
        "use_cases": [
            ("Recherche-Agent", "Sammelt und strukturiert Informationen aus Quellen und liefert eine belegte Zusammenfassung."),
            ("Wissens-Assistent", "Beantwortet Fragen auf Basis Ihrer internen Dokumente – DSGVO-konform, ohne Datenabfluss."),
            ("Dokumentations-Agent", "Erstellt aus Meetings, Chats und Notizen strukturierte, ablagefähige Dokumente."),
            ("Automatisierungs-Agent", "Löst Aufgaben in Workflows aus: Daten prüfen, Status aktualisieren, nächste Schritte anstoßen."),
        ],
        "process": [
            ("Aufgabe definieren", "Ziel, Eingaben, Ausgaben und Qualitätskriterien des Agenten werden festgelegt."),
            ("Werkzeuge & Daten anbinden", "Der Agent bekommt genau die Zugriffe, die er für die Aufgabe braucht – nicht mehr."),
            ("Agent bauen & testen", "Iterativ mit echten Beispieldaten, inklusive Fehlerfällen und Ausreißern."),
            ("Bewachen & betreiben", "Protokollierung, Limits und regelmäßige Qualitätskontrolle im Betrieb."),
        ],
        "tech": ["LLMs", "RAG", "Python", "n8n", "APIs & Webhooks", "Docker", "Prompt Engineering"],
        "benefits": [
            "Ergebnisse statt Antworten: Der Agent liefert fertige Arbeit, nicht nur Text.",
            "Wissensvorsprung: Ihre internen Dokumente werden tatsächlich nutzbar.",
            "Kontrollierte Autonomie: klare Grenzen, Rechte und Freigabepunkte.",
            "Betriebsreif statt Spielerei: dokumentiert, überwachbar, wartbar.",
        ],
        "faqs": [
            ("Was ist der Unterschied zwischen Chatbot und KI-Agent?", "Ein Chatbot antwortet auf Fragen. Ein Agent bekommt ein Ziel und führt dafür mehrere Schritte aus – er nutzt Werkzeuge, greift auf Daten zu und liefert ein Arbeitsergebnis."),
            ("Können Agenten eigenständig Entscheidungen treffen?", "Nur innerhalb der Grenzen, die Sie definieren. Kritische Schritte laufen über menschliche Freigabe – der Agent schlägt vor, Sie entscheiden."),
            ("Welche Daten sehen die Agenten?", "Nur die Daten und Systeme, die explizit angebunden werden. Bei sensiblen Daten kommen lokale Modelle zum Einsatz."),
        ],
        "related": ["ki-integration", "ki-automatisierung", "branchen-handwerk"],
    },
    "n8n-automatisierung": {
        "nav_label": "n8n-Automatisierung",
        "breadcrumb": "n8n Workflow-Automatisierung",
        "title": "n8n Automatisierung für Unternehmen – Workflows selbst hosten | Skalantech",
        "description": "n8n Automatisierung: Systeme verbinden, Workflows bauen und selbst hosten – DSGVO-freundlich, ohne teure Integrationsplattform. Skalantech setzt n8n produktiv um.",
        "cases_heading": "Workflows, die n8n für Sie übernimmt.",
        "h1": "Ihre Systeme reden endlich miteinander – mit n8n.",
        "lead": "n8n verbindet Ihre Tools per Workflow: ohne teure Integrationsplattform, ohne eigene Programmierabteilung. Skalantech plant, baut und betreibt n8n-Workflows – auf Wunsch selbst gehostet, damit Ihre Daten im Haus bleiben.",
        "problem_title": "Schnittstellen-Chaos statt reibungsloser Abläufe",
        "problem": [
            "Jedes Tool hat eigene Logik – Daten müssen trotzdem zwischen allen Systemen fließen.",
            "Integrationsplattformen kosten schnell vierstellige Beträge pro Monat.",
            "Cloud-Workflow-Tools senden sensible Daten durch fremde Infrastruktur.",
            "Einmal gebaute Integrationen sind wartungsintensiv und undokumentiert.",
        ],
        "solution_title": "Was Skalantech dafür tut",
        "solution": [
            "Workflow-Design: Prozesse werden als automatisierte Abläufe zwischen Ihren Systemen modelliert.",
            "n8n-Aufbau: Instanz einrichten (Cloud oder selbst gehostet), Systeme anbinden, Workflows entwickeln.",
            "Robuste Details: Fehlerbehandlung, Retries, Logging und Monitoring statt fragiler Ketten.",
            "Dokumentation und Übergabe: Ihr Team kann Workflows selbst verstehen und anpassen.",
        ],
        "use_cases": [
            ("Daten zwischen Systemen bewegen", "CRM, ERP, Tabellen, Dateiablagen und E-Mail per Workflow synchronisieren."),
            ("Anfragen automatisch verarbeiten", "Formulare und Webhooks in strukturierte Prozesse überführen – inklusive Benachrichtigung."),
            ("KI in Workflows einbinden", "LLM-Schritte für Zusammenfassung, Klassifizierung und Textgenerierung direkt im Workflow."),
            ("Selbst gehostete n8n-Instanz", "n8n auf eigener Infrastruktur betreiben – volle Datenkontrolle, kein externer Dienst."),
        ],
        "process": [
            ("Ist-Analyse", "Welche Systeme existieren, welche Schnittstellen haben sie, wo fließen Daten manuell?"),
            ("Workflow-Konzept", "Ablauf, Ausnahmen und Fehlerfälle werden vor dem Bau festgelegt."),
            ("Umsetzung & Test", "Workflows entstehen mit echten Daten und werden gründlich getestet."),
            ("Betrieb", "Monitoring, Updates und Anpassung an veränderte Anforderungen."),
        ],
        "tech": ["n8n", "APIs & Webhooks", "Docker", "Python", "LLMs", "SQL", "Tailscale"],
        "benefits": [
            "Transparente Kosten statt monatlicher Plattformgebühren.",
            "Selbst gehostet möglich – Daten bleiben in Ihrer Infrastruktur.",
            "Schnelle Ergebnisse: erste Workflows oft innerhalb weniger Tage produktiv.",
            "Wartbar: dokumentierte Workflows, die Ihr Team selbst versteht.",
        ],
        "faqs": [
            ("Was kostet n8n gegenüber kommerziellen Plattformen?", "Die Open-Source-Version ist lizenzkostenfrei. Es fallen nur Infrastruktur- und Umsetzungskosten an – deutlich planbarer als nutzungsbasierte Plattformgebühren."),
            ("Ist selbst gehostetes n8n sicher?", "Mit sauberer Konfiguration, Zugriffskontrolle und aktuellen Versionen ja. Skalantech betreibt selbst eine produktive n8n-Instanz auf eigener Infrastruktur."),
            ("Können wir n8n ohne Programmierkenntnisse bedienen?", "Die Oberfläche ist visuell. Für robuste Workflows sind trotzdem sauberes Design und Fehlerbehandlung nötig – dafür sind wir da, bis Ihr Team sicher ist."),
        ],
        "related": ["ki-automatisierung", "lokale-ki", "branchen-handwerk"],
    },
    "lokale-ki": {
        "nav_label": "Lokale KI",
        "breadcrumb": "Lokale & selbst gehostete KI",
        "title": "Lokale KI für Unternehmen – selbst gehostet, datenschutzkonform | Skalantech",
        "description": "Lokale KI selbst gehostet: LLMs auf eigener Infrastruktur betreiben – Datenschutz, Datenkontrolle und keine Cloud-Abhängigkeit. Skalantech plant und betreibt lokale KI.",
        "cases_heading": "Einsatzfälle, für die lokale KI die richtige Wahl ist.",
        "h1": "KI, die Ihre Daten nicht verlässt.",
        "lead": "Cloud-KI ist bequem, aber nicht überall erlaubt. Für sensible Daten und strenge Anforderungen gibt es lokale KI: Sprachmodelle laufen auf Ihrer eigenen Infrastruktur. Skalantech plant, setzt um und betreibt solche Systeme.",
        "problem_title": "Wenn Cloud-KI keine Option ist",
        "problem": [
            "Sensible Daten dürfen vertraglich oder rechtlich nicht an externe Dienste gehen.",
            "Laufende Cloud-KI-Kosten skalieren mit der Nutzung – schwer planbar.",
            "Abhängigkeit von externen Anbietern, deren Verfügbarkeit und Preisgestaltung Sie nicht kontrollieren.",
            "KI soll mit internen Dokumenten arbeiten – ohne sie aus dem Haus zu geben.",
        ],
        "solution_title": "Was Skalantech dafür tut",
        "solution": [
            "Machbarkeits- und Bedarfsanalyse: Welche Aufgaben, welche Daten, welche Modellanforderungen?",
            "Infrastruktur-Aufbau für lokale Modelle: GPU- oder CPU-Betrieb, Speicher, Skalierung.",
            "Modellauswahl und Betrieb: Open-Source-LLMs einrichten, aktualisieren und betreiben (z. B. über Ollama).",
            "Anbindung an Ihre Anwendungen: API-Schnittstellen, RAG auf internen Dokumenten, Workflow-Integration.",
        ],
        "use_cases": [
            ("Interne Dokumentenanalyse", "Verträge und Handbücher lokal auswerten – ohne Datenabfluss."),
            ("Datenschutzkonforme Assistenz", "KI-Assistenten für Teams mit strengen Compliance-Anforderungen."),
            ("Offline-fähige Prozesse", "KI-Funktionen in Umgebungen ohne stabile externe Anbindung."),
            ("Kostenkontrolle", "Vorhersagbare Betriebskosten statt nutzungsabhängiger Cloud-Rechnungen."),
        ],
        "process": [
            ("Anforderung klären", "Daten, Nutzung, Qualitätsanspruch und Budget werden ehrlich bewertet."),
            ("Architektur entwerfen", "Hardware, Modelle und Anbindung werden auf den Use-Case zugeschnitten."),
            ("Aufbau & Integration", "Instanz, Modell und Schnittstellen entstehen – mit Tests gegen Ihre Daten."),
            ("Betrieb & Optimierung", "Updates, Monitoring und Modellpflege gehören zum laufenden Betrieb."),
        ],
        "tech": ["Ollama", "Open-Source-LLMs", "Docker", "Python", "RAG", "GPU/CPU", "Tailscale"],
        "benefits": [
            "Volle Datenkontrolle: Ihre Dokumente verlassen die eigene Infrastruktur nicht.",
            "Planbare Kosten: keine nutzungsabhängigen Cloud-Gebühren.",
            "Unabhängigkeit von Anbieter-Entscheidungen und API-Ausfällen.",
            "Kombinierbar: Hybrid-Modelle mit Cloud für unkritische Aufgaben, lokal für sensible.",
        ],
        "faqs": [
            ("Sind lokale Modelle genauso gut wie Cloud-KI?", "Bei vielen Aufgaben inzwischen sehr nah, bei einigen darunter. Die ehrliche Antwort hängt vom Use-Case ab – genau das wird vorab getestet."),
            ("Welche Hardware braucht lokale KI?", "Das hängt vom Modell und der Nutzung ab. Für viele Aufgaben reichen gute CPUs, für große Modelle ist eine GPU sinnvoll. Skalantech plant das realistisch."),
            ("Was passiert mit Updates der Modelle?", "Modelle und Software werden regelmäßig aktualisiert. Der Betrieb ist dokumentiert und kann von Ihrem Team übernommen werden."),
        ],
        "related": ["ki-integration", "it-infrastruktur"],
    },
}

# ── Websites & Business Apps (eigene Angebotsseite, dedicated Template) ──
# Struktur & Wireframe: LUMINA (Kanban t_f59f5d89, 02_WIREFRAME.md). Copy = DRAFTS
# aus dem LUMINA-Prototyp (03_COPY-SLOTS-VELA §4); VELA-Endfassung (t_d9baa082)
# ersetzt die Texte als Follow-up (Muster: ROI-Rechner-VELA-Delta).
WEBSITES_APPS_COPY = {
    "nav_label": "Websites & Apps",
    "breadcrumb": "Websites & Business Apps",
    "title": "Websites & Business Apps für KMU – digitaler Vertrieb & Prozess-Tools | Skalantech",
    "description": "Corporate Websites, die Anfragen bringen, und Business-Apps, die Prozesse automatisieren: gebaut, integriert und betreut von Skalantech in Köln.",
    "h1": "Websites, die verkaufen. Apps, die Prozesse beschleunigen.",
    "lead": "Skalantech baut keine Visitenkarten, sondern digitale Werkzeuge: High-Performance-Websites, die Anfragen bringen, und interne Business-Apps, die wiederkehrende Arbeit übernehmen – tief integriert in Ihre Prozesse.",
    "hero_trust": "Server-gerendert · DSGVO-konform · Kein Vendor-Lock-in",
    "cta_primary": "Kostenlose Business-Analyse",
    "cta_secondary": "Projekt besprechen",
    "cta_mid": "Jetzt Business-Analyse buchen",
    "problem_title": "Eine Website, die nichts bringt, kostet Geld.",
    "problem": [
        "Ihre Website zählt Besucher, aber keine Anfragen.",
        "Jede Änderung kostet Wochen und eine Agentur-Rechnung.",
        "Prozesse laufen in Excel, E-Mails und Kopfarbeit – Daten doppelt, Fehler inklusive.",
        "Tools werden gekauft, aber nie angebunden – sie bleiben Insellösungen.",
    ],
    "offer_title": "Zwei Produktlinien. Ein Ziel: Ihr Betrieb arbeitet digital.",
    "offer_intro": "Beides entsteht aus Ihrem Geschäftsprozess – nicht aus einer Design-Vorlage.",
    "offer": [
        {
            "label": "01 · Corporate Websites",
            "title": "High-Performance Corporate Websites",
            "text": "Websites, die nicht nur gut aussehen, sondern Anfragen produzieren: conversion-optimiert, server-gerendert für SEO und schnell geladen – auf Technik, die Sie nicht an ein Baukastensystem fesselt.",
            "features": [
                "Conversion-Pfad statt Visitenkarte: klare Struktur, CTA, Terminbuchung",
                "SEO & Ladezeit: server-gerendert, gute Core Web Vitals, strukturierte Daten",
                "Formulare direkt angebunden: Website → n8n → CRM, statt E-Mail-Anhang",
                "Echte Fotos und Fakten statt generischer Stock-Ästhetik",
            ],
        },
        {
            "label": "02 · Business Apps & Portale",
            "title": "Interne Business Apps & Portale",
            "text": "Werkzeuge für Ihr Team und Ihre Kunden, die wiederkehrende Arbeit übernehmen: von der Angebots-Erstellung bis zum Kundenportal – gebaut auf Ihre Prozesse, nicht in eine Cloud, die Sie nicht kontrollieren.",
            "features": [
                "ROI-Rechner & Lead-Funnel: Besucher beziffern den Nutzen selbst und buchen Termine",
                "Buchungssysteme & Kunden-Onboarding: Termine, Formulare, Verträge in einem Fluss",
                "Interne Portale: Angebote, Rechnungen, Status – ohne E-Mail-Pingpong",
                "Anbindung an n8n, CRM und Bestandssysteme – kein Vendor-Lock-in",
            ],
            "link_text": "Live-Beispiel: ROI-Rechner",
            "link_url": "/branchen/handwerk#roi-rechner",
        },
    ],
    "abgrenzung_title": "Keine WordPress-Agentur. Kein Baukasten. Kein Lock-in.",
    "abgrenzung": [
        "Wir starten beim Geschäftsprozess, nicht beim Design.",
        "Website und App sind tief in Ihre IT integriert: n8n, CRM, Automatisierung.",
        "Open-Source-first, dokumentiert, übergabebereit.",
        "Code, Daten und Domains gehören Ihnen – jederzeit.",
    ],
    "process_title": "So läuft die Zusammenarbeit.",
    "process": [
        ("Business Audit", "Wir starten beim Geschäftsprozess: Wo entstehen Anfragen, wo verlieren Sie Zeit? Das ist der Anfang – nicht das Design."),
        ("Architektur & UX", "Datenbasierte Wireframes, conversion-fokussiert und auf Ihre Zielgruppe ausgerichtet – bevor eine Zeile Code entsteht."),
        ("Build & Integration", "State-of-the-art Tech-Stack, direkte Anbindung an Ihre IT-Infrastruktur, Tests inklusive."),
        ("Launch & Operation", "Hosting, Security-Hardening, Analytics und laufende Optimierung – damit die Seite nicht veraltet."),
    ],
    "cases_heading": "Gebaut. Nicht versprochen.",
    "use_cases": [
        ("Lead-Funnel mit Terminbuchung (Handwerk / Immobilien)", "Eine Website, die qualifizierte Anfragen generiert, mit integrierter Terminbuchung, die automatisch im Kalender landet – inklusive Erinnerungen."),
        ("Mandanten-Portal & ROI-Rechner (Kanzleien / B2B)", "Hochsichere Portale für Mandanten und interaktive ROI-Rechner, die den Nutzen Ihrer Leistung sofort beziffern – DSGVO-konform, lokal betreibbar."),
    ],
    "pricing_title": "Klare Preise. Zwei Stufen. Kein Kleingedrucktes.",
    "pricing": [
        {
            "name": "Build",
            "price": "ab 4.900 €",
            "unit": "einmalig",
            "text": "Corporate Website oder MVP einer Business-App – inklusive Audit, Architektur, Umsetzung und Launch.",
            "features": [
                "Business-Audit & Conversion-Struktur",
                "Design & Umsetzung (Website oder App-MVP)",
                "SEO-Grundlage: server-gerendert, strukturierte Daten",
                "Launch, Security-Hardening, Übergabe",
            ],
            "cta": "Projekt skizzieren",
        },
        {
            "name": "Operate & Grow",
            "price": "ab 490 €",
            "unit": "/ Monat",
            "text": "Ihre Systeme bleiben sicher, aktuell und werden kontinuierlich besser – wir betreuen, messen und optimieren.",
            "features": [
                "Sicheres Hosting & Maintenance",
                "Monitoring, Backups, Updates",
                "Analytics & Conversion-Reporting",
                "Kontinuierliche Optimierung (CRO)",
            ],
            "cta": "Betrieb besprechen",
            "badge": "Für laufenden Betrieb",
            "highlight": True,
        },
    ],
    "pricing_note": "Die Preise sind Einstiegswerte aus typischen Projekten – Ihr individuelles Angebot entsteht nach dem kostenlosen Business-Audit.",
    "tech": ["Next.js", "Python", "n8n", "Docker", "PostgreSQL", "Tailscale", "Caddy"],
    "faqs": [
        ("Müssen wir auf WordPress setzen?", "Nein. Wir setzen auf moderne, server-gerenderte Technik (z. B. Next.js), die schneller lädt und mehr Kontrolle lässt. Wenn WordPress bei Ihnen im Betrieb verankert ist, migrieren wir Schritt für Schritt – ohne Neubau um jeden Preis."),
        ("Was kostet eine Website bei Skalantech?", "Corporate Websites starten bei 4.900 € einmalig. Der genaue Preis entsteht im Business-Audit aus Umfang, Integrationen und Tempo – Sie bekommen ein Festangebot, bevor etwas gebaut wird."),
        ("Wie lange dauert ein Projekt?", "Eine Corporate Website ist typischerweise in 3–6 Wochen live, eine Business-App in 6–12 Wochen – abhängig von Integrationen und Freigaben."),
        ("Können Sie meine bestehende Website übernehmen?", "Ja. Im Audit prüfen wir, ob Übernahme, Umbau oder Neubau wirtschaftlicher ist – und empfehlen ehrlich, was weniger kostet."),
        ("Was passiert nach dem Launch?", "Mit dem Operate-&-Grow-Retainer ab 490 €/Monat bleiben Hosting, Sicherheit, Analytics und Optimierung in einer Hand. Ohne Retainer übergeben wir dokumentiert – Sie sind Eigentümer von Code, Daten und Domains."),
        ("Arbeitet ihr mit unserem CRM zusammen?", "Ja. Formulare, Buchungen und Funnels binden wir per n8n an gängige CRMs und Systeme an. Welche Schnittstellen bei Ihnen nötig sind, prüfen wir im Audit."),
    ],
    "trust": [
        ("Security-First", "TLS, DSGVO-konforme Verarbeitung, gehärtete Server – Sicherheit ist Teil des Builds, kein Extra."),
        ("Keine externen Tracker", "First-Party-Analytics statt Tracking-Krake – die Daten bleiben bei Ihnen."),
        ("Eigentum bleibt bei Ihnen", "Code, Daten und Domains gehören Ihnen. Kein Vendor-Lock-in."),
        ("Ein Ansprechpartner", "Xavier baut und betreut die Systeme selbst – persönlich erreichbar, keine Blackbox."),
    ],
    "cta_final_title": "Kostenlose Business-Analyse?",
    "cta_final_text": "30 Minuten, unverbindlich. Wir schauen uns Ihren Prozess an und sagen ehrlich, ob und wie eine Website oder Business-App Sie voranbringt.",
    "cta_final": "Kostenlose Business-Analyse",
    "tracking": {"hero": "hero_cta_click", "faq": "faq_open", "check": "check_cta_click"},
}

# ── P1 ROI-Rechner (/rechner + Homepage-Sektion) — VELA-Endfassung ─────
# Copy 1:1 aus VELA (Kanban t_8a6f04a7, roi_rechner_copy.py). Endfassung,
# keine Drafts. FAQPage-Schema wird 1:1 aus ROI_RECHNER_FAQS gerendert
# (Template rechner.html), damit kein Text-Drift entsteht.
ROI_RECHNER_COPY = {
    # ── 1. Standalone-Seite /rechner ────────────────────────────────────────
    "roi_meta_title": "ROI-Rechner: Was kostet manuelle Arbeit? | Skalantech",
    "roi_meta_description": "Manuelle Prozesse kosten Zeit und Geld. Rechnen Sie in 30 Sekunden aus, was ein wiederkehrender Ablauf Ihr Unternehmen pro Jahr kostet.",
    "roi_h1": "Was kostet Sie manuelle Arbeit?",
    "roi_subline": "Sechs Angaben, eine Zahl: Wählen Sie einen wiederkehrenden Ablauf, schätzen Sie Aufwand und Fehlerquote — und sehen Sie sofort, was er pro Jahr kostet und wie viel Automatisierung davon wegnimmt.",
    "roi_trust_line": "Ihre Angaben bleiben auf Ihrem Gerät. Der Rechner speichert nichts und sendet nichts an einen Server.",

    # ── 2. Homepage-Sektion (Block nach Pain, vor Services) ─────────────────
    "roi_section_label": "Rechner",
    "roi_h2": "Was kostet Sie manuelle Arbeit?",
    "roi_section_subline": "Ein wiederkehrender Prozess kostet mehr, als es sich anfühlt. Rechnen Sie selbst — in 30 Sekunden, ohne Anmeldung.",
    "roi_see_more": "Zum vollständigen ROI-Rechner →",

    # ── 3. Widget-Inputs ─────────────────────────────────────────────────────
    "roi_step1_legend": "Welcher Prozess kostet Zeit?",
    "roi_process_label": "Prozess",
    "roi_process_placeholder": "Prozess auswählen …",
    "roi_process_angebote": "Angebote erstellen",
    "roi_process_rechnungen": "Rechnungen & Belege",
    "roi_process_termine": "Terminvergabe & -erinnerung",
    "roi_process_daten": "Daten übertragen / erfassen",
    "roi_process_berichte": "Berichte & Recherche",
    "roi_process_kommunikation": "E-Mails & Nachverfolgung",
    "roi_process_sonstiges": "Anderer Prozess",

    "roi_step2_legend": "Wie viel Aufwand ist das?",
    "roi_minutes_label": "Zeit pro Durchlauf",
    "roi_minutes_unit": "Minuten",
    "roi_frequency_label": "Wie oft pro Woche",
    "roi_frequency_unit": "× pro Woche",
    "roi_error_label": "Fehlerquote / Nacharbeit",
    "roi_error_hint": "Der Anteil, der wegen Fehlern oder Korrekturen ein zweites Mal anfällt.",

    "roi_step3_legend": "Was kostet eine Stunde?",
    "roi_rate_label": "Stundensatz (Vollkosten)",
    "roi_rate_hint": "Lohn plus Arbeitgeberanteile und Nebenkosten — der reale Preis einer Arbeitsstunde.",
    "roi_rate_unit": "€/h",

    "roi_step4_legend": "Wie viel davon lässt sich automatisieren?",
    "roi_auto_label": "Automatisierungsgrad",
    "roi_auto_note": "Das ist Ihre Annahme — kein Versprechen. Im Erstgespräch prüfen wir, welcher Wert für Ihren Prozess realistisch ist.",

    # ── 4. Ergebnis-Panel ────────────────────────────────────────────────────
    "roi_result_kicker": "Ihre Schätzung",
    "roi_result_cost": "≈ 28.400 €",  # dynamisch gerendert (Beispielwert)
    "roi_result_cost_unit": "pro Jahr",
    "roi_result_auto_label": "davon automatisierbar",
    "roi_result_detail": "19.900 € · 610 h pro Jahr",  # dynamisch gerendert (Beispielwert)
    "roi_result_cta": "Kostenloses Erstgespräch",
    "roi_result_note": "Schätzung auf Basis Ihrer Angaben. Der echte Wert hängt von Prozess, Daten und Team ab. Im kostenlosen Erstgespräch analysieren wir ihn.",

    # ── 5. /rechner — „So funktioniert's" ────────────────────────────────────
    "roi_how_title": "So kommen Sie zur Zahl",
    "roi_how_step1_title": "Prozess wählen",
    "roi_how_step1_text": "Wählen Sie den wiederkehrenden Ablauf, der Ihrem Team am meisten Zeit kostet.",
    "roi_how_step2_title": "Aufwand schätzen",
    "roi_how_step2_text": "Schätzen Sie Dauer, Häufigkeit und Fehlerquote — grobe Werte genügen für die Größenordnung.",
    "roi_how_step3_title": "Einsparpotenzial sehen",
    "roi_how_step3_text": "Sie sehen sofort die Jahreskosten und was Automatisierung davon wegnimmt.",

    # ── FAQ (6 Fragen aus 05 §5, Antworten Endfassung) ───────────────────────
    "roi_faq_q1": "Wie genau ist diese Berechnung?",
    "roi_faq_a1": "Die Rechnung basiert auf Ihren Angaben und konservativen Annahmen (47 Wochen pro Jahr, Vollkosten-Stundensatz). Sie ersetzt keine Prozessanalyse — sie zeigt die Größenordnung. Den genauen Wert ermitteln wir im Erstgespräch.",
    "roi_faq_q2": "Was passiert mit meinen Eingaben?",
    "roi_faq_a2": "Nichts. Die Berechnung läuft komplett in Ihrem Browser. Ihre Angaben werden nicht gespeichert und nicht an einen Server übertragen.",
    "roi_faq_q3": "Was ist der „Stundensatz (Vollkosten)“?",
    "roi_faq_a3": "Der Stundensatz (Vollkosten) ist Lohn plus Arbeitgeberanteile plus Nebenkosten — also das, was eine Arbeitsstunde Ihr Unternehmen wirklich kostet, nicht das Bruttogehalt.",
    "roi_faq_q4": "Warum 47 Arbeitswochen?",
    "roi_faq_a4": "Der Rechner rechnet mit 47 Arbeitswochen pro Jahr. Damit sind Urlaub, Feiertage und durchschnittliche Krankheitstage bereits berücksichtigt.",
    "roi_faq_q5": "Wie viel lässt sich wirklich automatisieren?",
    "roi_faq_a5": "Das hängt vom Prozess, den Daten und den Schnittstellen ab. Der Schieberegler ist Ihre Annahme, kein Versprechen. Im Erstgespräch bewerten wir, welcher Automatisierungsgrad für Ihren konkreten Ablauf realistisch ist.",
    "roi_faq_q6": "Was kostet die Analyse?",
    "roi_faq_a6": "Das Erstgespräch ist kostenlos und unverbindlich. Sie bekommen eine ehrliche Einschätzung — auch wenn die Antwort lautet, dass sich Automatisierung für Sie nicht lohnt. Kosten entstehen erst, wenn Sie ein Projekt beauftragen.",

    # ── Abschluss-CTA ────────────────────────────────────────────────────────
    "roi_cta_title": "Klingt nach einem lohnenden Projekt?",
    "roi_cta_text": "30 Minuten, unverbindlich: Wir analysieren Ihren Prozess und sagen Ihnen ehrlich, ob sich Automatisierung lohnt — und wo nicht.",
}

# FAQPage-Schema 1:1 — identisch zu den Slots im Dict (kein Drift möglich).
ROI_RECHNER_FAQS = [
    (ROI_RECHNER_COPY["roi_faq_q1"], ROI_RECHNER_COPY["roi_faq_a1"]),
    (ROI_RECHNER_COPY["roi_faq_q2"], ROI_RECHNER_COPY["roi_faq_a2"]),
    (ROI_RECHNER_COPY["roi_faq_q3"], ROI_RECHNER_COPY["roi_faq_a3"]),
    (ROI_RECHNER_COPY["roi_faq_q4"], ROI_RECHNER_COPY["roi_faq_a4"]),
    (ROI_RECHNER_COPY["roi_faq_q5"], ROI_RECHNER_COPY["roi_faq_a5"]),
    (ROI_RECHNER_COPY["roi_faq_q6"], ROI_RECHNER_COPY["roi_faq_a6"]),
]

# ── Branchen-Landingpages (Stage 5 der Pipeline) ───────────────────────
# Copy 1:1 aus VELA (Kanban t_7ccdf6ff). Schlüssel "branchen-{slug}" →
# Routen /branchen/{slug} (explizit, kein Catch-All). In LANDING_ORDER
# bewusst NICHT aufgenommen — die Branch-Slugs haben ein eigenes URL-Schema
# und werden in public.py separat in die Sitemap aufgenommen.
LANDING_PAGES.update(LANDING_BRANCHEN)

# Websites-&-Apps-Angebotsseite (dedicated Template websites_apps.html) —
# in LANDING_PAGES, damit _render_landing + _landing_map + Sitemap sie finden.
LANDING_PAGES["websites-apps"] = WEBSITES_APPS_COPY

# Reihenfolge für Navigation, Sitemap und interne Verlinkung
LANDING_ORDER = [
    "websites-apps",
    "it-infrastruktur",
    "ki-integration",
    "ki-automatisierung",
    "ki-agenten",
    "n8n-automatisierung",
    "lokale-ki",
]
