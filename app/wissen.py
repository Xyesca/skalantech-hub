"""Skalantech Hub — Wissensartikel (SEO-fähige Blogstruktur).

Qualität vor Quantität: wenige, substanzielle Artikel statt generierter
SEO-Masse. Alle Inhalte sind technisch sachlich gehalten und enthalten keine
erfundenen Studien, Kunden oder Kennzahlen.
"""

ARTICLES = {
    "was-ist-ein-ki-agent": {
        "title": "Was ist ein KI-Agent? Definition, Beispiele und Abgrenzung",
        "description": "KI-Agenten für Unternehmen erklärt: Was ein Agent ist, wie er sich von Chatbots unterscheidet, welche Aufgaben er übernimmt und wo die Grenzen liegen.",
        "h1": "Was ist ein KI-Agent?",
        "intro": (
            "KI-Agenten sind aktuell eines der meistgenutzten Schlagworte in der Unternehmens-IT. "
            "Häufig bleibt aber unklar, was ein Agent tatsächlich kann – und was nicht. Dieser Artikel "
            "grenzt den Begriff sauber ab und zeigt, wo Agenten in Unternehmen echten Nutzen stiften."
        ),
        "sections": [
            {
                "heading": "Definition: Was unterscheidet einen KI-Agenten von einem Chatbot?",
                "paragraphs": [
                    "Ein Chatbot beantwortet Fragen. Er bekommt eine Eingabe und liefert eine Antwort – meist als Text, ohne weitere Werkzeuge. Ein KI-Agent geht darüber hinaus: Er bekommt ein Ziel, plant mehrere Schritte und nutzt dafür Werkzeuge. Er kann Dokumente durchsuchen, Daten aus einer API abrufen, Inhalte strukturieren und am Ende ein Arbeitsergebnis liefern.",
                    "Konkret: Ein Chatbot erklärt Ihnen den Inhalt einer Rechnung, wenn Sie sie hochladen. Ein Agent erkennt eingehende Rechnungen, liest sie, prüft Pflichtfelder, legt sie im System ab und informiert die Buchhaltung – als durchgängiger automatisierter Ablauf.",
                ],
            },
            {
                "heading": "Aus welchen Bausteinen besteht ein KI-Agent?",
                "paragraphs": [
                    "Ein KI-Agent kombiniert im Kern vier Komponenten: ein Sprachmodell (LLM) für Verständnis und Entscheidungen, Zugriff auf Werkzeuge (APIs, Suche, Dateien), einen Kontext aus Daten – häufig per RAG aus eigenen Dokumenten – sowie klare Regeln und Grenzen, die festlegen, was der Agent darf und was nicht.",
                    "Diese Bausteine machen Agenten für Unternehmen interessant: Das LLM übernimmt die Verarbeitung, während die Anbindung an die eigenen Systeme dafür sorgt, dass Ergebnisse in bestehende Prozesse passen.",
                ],
            },
            {
                "heading": "Typische Einsatzfälle in Unternehmen",
                "paragraphs": [
                    "Praxisnah sind Agenten vor allem dort, wo Wissen verarbeitet und Arbeit vorbereitet wird:",
                ],
                "list": [
                    "Recherche-Agenten sammeln Informationen aus Quellen und liefern belegte Zusammenfassungen.",
                    "Wissens-Assistenten beantworten Fragen auf Basis interner Dokumente – ohne dass Daten das Unternehmen verlassen.",
                    "Dokumentations-Agenten erstellen aus Meetings, Chats und Notizen strukturierte, ablagefähige Unterlagen.",
                    "Automatisierungs-Agenten stoßen in Workflows Aktionen an: Daten prüfen, Status aktualisieren, nächste Schritte auslösen.",
                ],
            },
            {
                "heading": "Wo liegen die Grenzen?",
                "paragraphs": [
                    "Agenten sind keine Ersatzmitarbeiter. Sie arbeiten zuverlässig bei klar definierten Aufgaben mit erwartbaren Ergebnissen. Wo Entscheidungen mit Risiko verbunden sind, gehört eine menschliche Freigabe in den Prozess. Ohne klare Regeln, Rechtebegrenzung und Protokollierung wird ein Agent schnell zum Risiko – das ist eine Frage des Designs, nicht der Technologie.",
                    "Wer Agenten einführen will, sollte mit einem einzelnen, klar abgegrenzten Use-Case starten, den Agent schrittweise testen und die Qualität der Ergebnisse regelmäßig kontrollieren.",
                ],
            },
        ],
        "related_service": "ki-agenten",
        "cta_text": "Einsatz von KI-Agenten prüfen",
    },
    "n8n-selbst-hosten": {
        "title": "n8n selbst hosten: Vorteile, Risiken und was Sie beachten sollten",
        "description": "n8n selbst hosten statt Cloud: Vorteile für Datenschutz und Kosten, technische Voraussetzungen, Risiken und bewährte Betriebspraxis.",
        "h1": "n8n selbst hosten: Vorteile, Risiken und Grundlagen",
        "intro": (
            "n8n ist eine Open-Source-Workflow-Plattform, mit der sich Tools über visuell gebaute Abläufe verbinden lassen. "
            "Viele Unternehmen nutzen die Cloud-Variante – wer sensible Daten verarbeitet oder Kosten planbar halten will, "
            "hostet n8n selbst. Was das bedeutet, zeigt dieser Artikel."
        ),
        "sections": [
            {
                "heading": "Warum selbst hosten?",
                "paragraphs": [
                    "Der wichtigste Grund ist Datenkontrolle: Bei einer selbst gehosteten Instanz verlassen Workflow-Daten Ihre Infrastruktur nicht. Das ist relevant, sobald personenbezogene oder vertrauliche Unternehmensdaten durch Workflows fließen.",
                    "Der zweite Grund ist Kostenplanbarkeit. Die Open-Source-Version von n8n ist lizenzkostenfrei. Es fallen nur Infrastruktur- und Betriebskosten an – statt nutzungsbasierter Plattformgebühren, die mit dem Datenvolumen skalieren.",
                ],
            },
            {
                "heading": "Technische Voraussetzungen",
                "paragraphs": [
                    "n8n ist eine Node.js-Anwendung mit Datenbank (standardmäßig SQLite, für größere Installationen PostgreSQL). Der Betrieb läuft sauber als Docker-Container auf einem kleinen Server oder VPS. Für den Zugriff von außen sollte ein Reverse-Proxy mit TLS (etwa Caddy) und ein Zugriffskonzept ohne unnötig offene Ports eingerichtet werden.",
                    "Bei der Planung sind Backups der n8n-Datenbank und der Workflow-Definitionen Pflicht – ein verlorener Workflow ist sonst nicht wiederherstellbar. Ebenso wichtig ist ein Update-Prozess, denn n8n erscheint in kurzen Zyklen.",
                ],
            },
            {
                "heading": "Typische Risiken und wie man sie vermeidet",
                "paragraphs": [
                    "Die häufigsten Fehler bei selbst gehostetem n8n sind: fehlende Backups, offene Instanzen ohne Zugriffsschutz, unkontrollierte Update-Fahrpläne und Workflows ohne Fehlerbehandlung. Ein Workflow ohne Retry- und Fehlerlogik bricht still – und niemand merkt es, bis Daten fehlen.",
                    "Bewährte Praxis: Monitoring und Alarmierung für fehlgeschlagene Ausführungen, dokumentierte Workflows, ein definierter Update-Rhythmus und Tests nach Änderungen an verbundenen Systemen.",
                ],
            },
            {
                "heading": "Lohnt sich selbst gehostetes n8n für Ihr Unternehmen?",
                "paragraphs": [
                    "Wenn Workflows überwiegend unkritische Daten verarbeiten und ein kleines Team die Plattform betreuen kann, ist die Cloud-Variante oft pragmatischer. Sobald sensible Daten, Compliance-Anforderungen oder hohe Workflow-Volumina ins Spiel kommen, zahlt sich die eigene Instanz aus.",
                    "Ein hybrider Ansatz ist ebenfalls möglich: selbst gehostete Instanz für kritische Prozesse, Cloud für unkritische Ad-hoc-Automatisierung. Die Entscheidung sollte auf Basis der konkreten Prozesse getroffen werden – nicht nach Bauchgefühl.",
                ],
            },
        ],
        "related_service": "n8n-automatisierung",
        "cta_text": "n8n-Automatisierung besprechen",
    },
    "lokale-ki-vs-cloud-ki": {
        "title": "Lokale KI vs. Cloud-KI: Was Unternehmen wissen müssen",
        "description": "Lokale KI oder Cloud-KI? Vergleich von Datenschutz, Kosten, Qualität und Betrieb – und wann sich welches Modell für Unternehmen lohnt.",
        "h1": "Lokale KI vs. Cloud-KI: Der ehrliche Vergleich",
        "intro": (
            "Vor jeder KI-Einführung steht eine Grundsatzfrage: Sollen Modelle in der Cloud laufen oder auf eigener Infrastruktur? "
            "Die Antwort hängt von Daten, Anforderungen und Budget ab – und ist seltener eindeutig, als Marketing suggeriert."
        ),
        "sections": [
            {
                "heading": "Cloud-KI: Vorteile und Grenzen",
                "paragraphs": [
                    "Cloud-KI (etwa über API-Zugänge großer Anbieter) bietet sofortige Verfügbarkeit, hohe Modellqualität und keine eigene Hardware. Für unkritische Aufgaben ist das oft die schnellste und beste Lösung.",
                    "Die Grenzen liegen bei Daten und Kosten: Vertrauliche Daten dürfen nicht immer an externe Dienste. Und die Kosten skalieren mit der Nutzung – bei intensiver Verarbeitung werden sie schwer planbar.",
                ],
            },
            {
                "heading": "Lokale KI: Was selbst gehostete Modelle leisten",
                "paragraphs": [
                    "Lokale KI bedeutet: Open-Source-Modelle laufen auf eigener Hardware, meist über Werkzeuge wie Ollama oder direkt in Docker. Daten verlassen das Unternehmen nicht, Kosten sind vorhersagbar, und die Abhängigkeit von einzelnen Anbietern entfällt.",
                    "Der Preis dafür: eigene Hardware oder ein leistungsfähiger Server, laufender Betriebsaufwand und teils geringere Modellqualität als die besten Cloud-Modelle. Moderne Open-Source-Modelle sind jedoch bei vielen Alltagsaufgaben inzwischen vergleichbar stark.",
                ],
            },
            {
                "heading": "Die wichtigsten Entscheidungskriterien",
                "paragraphs": [
                    "Vier Fragen entscheiden in der Praxis:",
                ],
                "list": [
                    "Welche Daten werden verarbeitet – und dürfen sie das Unternehmen verlassen?",
                    "Wie stark ist die Nutzung – ein paar Anfragen am Tag oder kontinuierliche Verarbeitung?",
                    "Welche Qualität ist nötig – reicht ein gutes Open-Source-Modell oder braucht es Spitzenleistung?",
                    "Wer betreibt die Infrastruktur – gibt es im Team Kapazität für Betrieb und Updates?",
                ],
            },
            {
                "heading": "Hybrid ist oft die pragmatischste Antwort",
                "paragraphs": [
                    "Viele Unternehmen kommen mit einem hybriden Modell am besten: lokale KI für sensible Daten und kritische Prozesse, Cloud-KI für unkritische Aufgaben mit hohem Qualitätsanspruch. So bleibt die Datenkontrolle dort, wo sie nötig ist, und die Flexibilität der Cloud dort, wo sie nutzt.",
                    "Wichtig ist, die Entscheidung pro Use-Case zu treffen und die Kosten beider Wege realistisch zu vergleichen – inklusive Betriebsaufwand der eigenen Infrastruktur.",
                ],
            },
        ],
        "related_service": "lokale-ki",
        "cta_text": "KI-Architektur für Ihr Unternehmen klären",
    },
}

ARTICLE_ORDER = [
    "was-ist-ein-ki-agent",
    "n8n-selbst-hosten",
    "lokale-ki-vs-cloud-ki",
]

# Publikationsdatum (Tag des Deployments der Wissensstruktur)
ARTICLE_PUBLISHED = "2026-08-16"
