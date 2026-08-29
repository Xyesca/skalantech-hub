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
                    "Ein klassischer Chatbot wartet auf eine Eingabe des Benutzers und liefert daraufhin eine direkte Antwort. Seine Fähigkeiten beschränken sich meist auf die Generierung von Text oder das Abrufen von vordefinierten Informationen aus einer einfache Wissensdatenbank. Er arbeitet rein reaktiv: Eine Frage rein, eine Antwort raus. Der Chatbot kann den Kontext einer Konversation halten, aber er wird von sich aus keine Aktionen außerhalb des Chatfensters ausführen. Ein KI-Agent dagegen geht einen entscheidenden Schritt weiter: Er wird nicht für eine einmalige Frage-Antwort-Runde gebaut, sondern um ein übergeordnetes Geschäftsziel selbstständig zu erreichen. Er arbeitet proaktiv, zielorientiert und wählt selbst die nötigen Werkzeuge aus.",
                    "Ein Agent plant die dafür notwendigen Schritte eigenständig, zerlegt das Hauptziel in logische Teilergebnisse und führt Aktionen in externen Systemen aus. Während herkömmliche Automatisierungslösungen starre Wenn-Dann-Regeln benötigen und bei der kleinsten Abweichung im Datenformat abbrechen, kann ein KI-Agent dank des zugrundeliegenden Sprachmodells flexibel auf unstrukturierte Daten reagieren. Er versteht den Kontext und entscheidet situativ über den besten Weg zur Zielerreichung. Er kann Fehler selbstständig erkennen und alternative Pfade wählen, um das vorgegebene Ziel dennoch zu erreichen.",
                    "Um diesen Unterschied im Büroalltag zu verdeutlichen: Ein Chatbot kann Ihnen den Inhalt einer englischsprachigen Lieferantenrechnung übersetzen oder eine Zusammenfassung der Posten liefern, wenn Sie ihm das Dokument manuell hochladen. Ein KI-Agent hingegen übernimmt den gesamten Prozess autonom: Er überwacht fortlaufend das E-Mail-Postfach, erkennt die eingehende Rechnung, liest die Positionsdaten aus, gleicht sie mit der Bestellung in Ihrem ERP-System ab, prüft die Einhaltung der gesetzlichen Pflichtangaben nach dem Umsatzsteuergesetz und bereitet die Freigabe in der Buchhaltungssoftware vor. Der menschliche Mitarbeiter sieht am Ende nur noch das fertige Prüfergebnis und muss dieses lediglich per Klick bestätigen. Hier wird die Technologie vom netten Chat-Partner zu einem produktiven digitalen Mitarbeiter, der manuelle Arbeitsschritte vollständig überflüssig macht.",
                ],
            },
            {
                "heading": "Aus welchen Bausteinen besteht ein KI-Agent?",
                "paragraphs": [
                    "Ein produktiver KI-Agent besteht im Wesentlichen aus vier aufeinander abgestimmten Komponenten, die im Zusammenspiel seine autonome Funktionsweise sichern. Diese Bausteine müssen präzise aufeinander abgestimmt sein, um Stabilität und Sicherheit zu gewährleisten:",
                ],
                "list": [
                    "Das Sprachmodell (LLM) als Gehirn und Steuerungszentrale: Es interpretiert die Benutzerabsicht, zerlegt komplexe Zielvorgaben in logische Teilschritte (Planning) und entscheidet eigenständig, welches Werkzeug für den nächsten Schritt am besten geeignet ist. Dabei nutzt es Methoden wie Chain-of-Thought-Reasoning, um Zwischenschritte logisch zu begründen und zu bewerten.",
                    "Schnittstellen und Werkzeuge (Tools & APIs): Ein Agent benötigt Werkzeuge, um mit seiner Umwelt zu interagieren. Dazu gehören Datenbankzugriffe, Websuchmaschinen, das Ausführen von Code in geschützten Sandbox-Umgebungen sowie API-Anbindungen an CRM-, ERP- und E-Mail-Systeme. Ohne diese Werkzeuge wäre der Agent blind und handlungsunfähig, er könnte nur Texte generieren, aber keine echten Probleme lösen.",
                    "Der Speicher (Memory): Ein guter Agent benötigt ein funktionierendes Gedächtnis. Das Kurzzeitgedächtnis sichert den Zustand des aktuellen Arbeitsschritts (z. B. welche Dateien in einer Schleife bereits erfolgreich analysiert wurden). Das Langzeitgedächtnis speichert historische Informationen oder bewährte Vorgehensweisen aus früheren Aufgabenstellungen. Über eine RAG-Anbindung (Retrieval-Augmented Generation) greift der Agent in Echtzeit auf das gesamte firmeninterne Wissen zu, ohne dass das Modell aufwendig und teuer neu trainiert werden muss.",
                    "Leitplanken und Sicherheitsregeln (Guardrails): Guardrails definieren die klaren Grenzen, in denen sich der Agent bewegen darf. Sie regeln Schreib- und Leserechte, verhindern unbefugte Datenzugriffe und erzwingen menschliche Kontrollpunkte (Human-in-the-Loop) vor geschäftskritischen Aktionen – wie beispielsweise dem Ausführen von Überweisungen, dem Löschen von Kundendaten oder dem direkten Absenden von E-Mails an Endkunden.",
                ],
            },
            {
                "heading": "Typische Einsatzfälle in Unternehmen",
                "paragraphs": [
                    "In der Praxis lösen KI-Agenten konkrete Probleme von kleinen und mittelständischen Unternehmen. Skalantech hat dafür spezialisierte Lösungen entwickelt, die zeigen, wie Agenten bestehende Software nicht ersetzen, sondern intelligenter verbinden. Jede dieser Lösungen fokussiert sich auf einen klaren Business-Nutzen und entlastet Ihre Fachkräfte von wiederkehrenden Aufgaben:",
                ],
                "list": [
                    "InvoiceFlow (Rechnungsverarbeitung): Dieser Agent überwacht Rechnungseingänge, liest Positionsdaten aus, validiert die Pflichtangaben nach § 14 UStG und überträgt die geprüften Daten direkt in das Buchhaltungssystem. Die Fehlerquote bei der manuellen Dateneingabe sinkt dadurch auf nahe null, und Rechnungen werden innerhalb von Minuten statt Tagen verarbeitet.",
                    "OfferAI (Angebotserstellung): Im Vertrieb verbringen Mitarbeiter oft Stunden damit, Angebote aus unstrukturierten Kundenanfragen (z. B. PDFs, handschriftlichen Notizen oder langen E-Mails) zu erstellen. OfferAI analysiert diese Anfragen, gleicht die benötigten Teile mit der Lagerdatenbank ab, berechnet die Preise nach den hinterlegten Konditionen und generiert einen fertigen Angebotsentwurf. Die Bearbeitungszeit verkürzt sich von Stunden auf wenige Minuten.",
                    "MailAgent (E-Mail-Routing & Support): Im Kundenservice sortiert dieser Agent eingehende Nachrichten vor. Er erkennt das Anliegen (z. B. Reklamation, Adressänderung oder Preisanfrage), klassifiziert die Dringlichkeit und leitet die E-Mail an das zuständige Team weiter. Falls es sich um eine Standardanfrage handelt, bereitet er direkt eine passende Antwort vor, die der Servicemitarbeiter mit einem Klick absenden kann.",
                ],
            },
            {
                "heading": "Wo liegen die Grenzen und Risiken?",
                "paragraphs": [
                    "Trotz der enormen Leistungsfähigkeit haben KI-Agenten klare Grenzen. Sie arbeiten hervorragend in vordefinierten Mustern, bei denen die Eingaben und die erwarteten Ausgaben strukturiert sind. Sobald eine Situation jedoch hohen Ermessensspielraum, emotionale Intelligenz oder strategische Entscheidungen erfordert, stoßen sie an ihre Grenzen. Ein Agent besitzt kein echtes Verständnis, sondern verarbeitet statistische Wahrscheinlichkeiten. Er kann Lügen oder falsche Informationen generieren (Halluzinationen), wenn er nicht durch RAG und strenge Leitplanken abgesichert wird.",
                    "Ein unkontrollierter Agent, der ohne menschliche Aufsicht Angebote versendet oder Zahlungen anweist, stellt ein erhebliches geschäftliches Risiko dar. Daher gilt bei Skalantech das Prinzip: Human-in-the-Loop. Der Agent bereitet die Arbeit vor, filtert Daten und strukturiert Informationen – die finale Entscheidung und Freigabe verbleibt immer beim Menschen. So wird sichergestellt, dass die Verantwortung beim Mitarbeiter bleibt und Fehler rechtzeitig korrigiert werden.",
                    "Darüber hinaus spielen Datenschutz und Datensouveränität eine entscheidende Rolle. Wenn ein Agent vertrauliche Kundendaten verarbeitet, müssen diese streng geschützt werden. Die Übertragung an Cloud-Server außerhalb der EU kann zu rechtlichen Compliance-Konflikten führen. Die Lösung liegt hier im Hosting auf eigener, sicherer Infrastruktur oder der Nutzung lokaler Open-Source-Modelle, die vollständig im eigenen Netzwerk betrieben werden und keine sensiblen Daten nach außen geben. Dies minimiert Abhängigkeiten und schützt das geistige Eigentum Ihres Unternehmens.",
                ],
            },
        ],
        "related_service": "ki-agenten",
        "cta_text": "Einsatz von KI-Agenten prüfen",
        "next_step": {
            "kind": "prozess",
            "label": "KI-Agenten im Überblick",
            "target": "ki-agenten",
            "hint": "Prozessseite: Was Skalantech bei KI-Agenten konkret umsetzt – von RAG bis InvoiceFlow.",
        },
    },
    "n8n-selbst-hosten": {
        "title": "n8n selbst hosten: Vorteile, Risisen und was Sie beachten sollten",
        "description": "n8n selbst hosten statt Cloud: Vorteile für Datenschutz und Kosten, technische Voraussetzungen, Risiken und bewährte Betriebspraxis.",
        "h1": "n8n selbst hosten: Vorteile, Risiken und Grundlagen",
        "intro": (
            "n8n ist eine Open-Source-Workflow-Plattform, mit der sich Tools über visuell gebaute Abläufe verbinden lassen. "
            "Viele Unternehmen nutzen die Cloud-Variante – wer sensible Daten verarbeitet oder Kosten planbar halten will, "
            "hostet n8n selbst. Was das bedeutet, zeigt dieser Artikel."
        ),
        "sections": [
            {
                "heading": "Warum selbst hosten? Die zwei Haupttreiber: Datenschutz und Kostenkontrolle",
                "paragraphs": [
                    "Der wichtigste Grund für den Betrieb einer eigenen n8n-Instanz ist der Datenschutz. In vielen Branchen – wie etwa im Handwerk, bei Kanzleien oder im Kfz-Bereich – fließen personenbezogene Kundendaten, Rechnungsdaten oder interne Prozessberichte durch die Workflows. Nutzt man die Cloud-Version des Anbieters, werden diese Daten auf fremden Servern verarbeitet. Beim Self-Hosting bleibt der gesamte Datenfluss in Ihrer eigenen Hand. Die Daten verlassen Ihre Infrastruktur nicht, was die Einhaltung der DSGVO-Richtlinien erheblich vereinfacht und das Vertrauen Ihrer Kunden sichert. Sie behalten die volle Kontrolle über Logs, Zwischenspeicher und Protokolle.",
                    "Der zweite wesentliche Treiber ist die Kostenkontrolle. Das Lizenzmodell der n8n-Cloud basiert auf der Anzahl der Workflow-Ausführungen. Je mehr Prozesse Sie automatisieren und je häufiger diese laufen, desto höher steigen die monatlichen Gebühren. Ein konkretes Rechenbeispiel verdeutlicht das: Der kleinste n8n-Cloud-Tarif kostet rund 50 Euro pro Monat und erlaubt lediglich 2.500 Workflow-Ausführungen. Synchronisieren Sie jedoch ein CRM-System stündlich mit Ihrem Rechnungstool oder verarbeiten Sie tägliche Belegdaten von mehreren hundert Aufträgen, knacken Sie diese Grenze in wenigen Tagen. Ein Upgrade in höhere Tarife kostet schnell mehrere hundert Euro monatlich, was die Rentabilität der Automatisierung stark belastet.",
                    "Die quelloffene Community-Version von n8n ist dagegen lizenzkostenfrei. Sie zahlen lediglich für die zugrundeliegende Infrastruktur – zum Beispiel einen kleinen virtuellen Server (VPS) für 10 bis 20 Euro im Monat. Egal, ob Ihre Workflows zehnmal oder zehntausendmal am Tag laufen: Die Betriebskosten bleiben stabil, planbar und unabhängig vom Nutzungsvolumen. Das macht Automatisierungsprojekte auch für kleinere Betriebe von der ersten Sekunde an wirtschaftlich attraktiv und skaliert ohne finanzielle Risiken.",
                ],
            },
            {
                "heading": "Technische Voraussetzungen: Docker, PostgreSQL und Reverse-Proxy",
                "paragraphs": [
                    "Der Einstieg in das Self-Hosting von n8n ist technisch klar strukturiert. In der Praxis hat sich der Betrieb als Docker-Container etabliert. Docker kapselt die Anwendung und sorgt dafür, dass n8n unabhängig vom Betriebssystem des Servers stabil läuft und sich leicht aktualisieren lässt. Für einen stabilen Betrieb reicht meist schon ein kleiner Server mit 1 bis 2 vCPUs und 2 GB RAM aus.",
                    "Neben dem n8n-Container wird eine Datenbank benötigt. Für kleine Testumgebungen oder einfache Workflows reicht die integrierte SQLite-Datenbank aus. Sobald jedoch geschäftskritische Prozesse mit vielen gleichzeitigen Ausführungen laufen, sollte eine PostgreSQL-Datenbank als zuverlässige Basis angebunden werden. PostgreSQL verhindert Datenkorruption bei hoher Last, ermöglicht schnellere Datenbankzugriffe und erlaubt den stabilen Betrieb von n8n im Queue-Modus, bei dem mehrere Worker-Instanzen die Last gemeinsam bewältigen. Das ist wichtig, um Ausfälle bei Lastspitzen zu verhindern.",
                    "Damit die Workflows sicher von außen erreichbar sind – beispielsweise um Webhooks von CRM-Systemen zu empfangen –, wird ein Reverse-Proxy vor n8n geschaltet. Ein modernes Werkzeug dafür ist Caddy. Caddy übernimmt die Verschlüsselung (TLS/SSL) vollautomatisch und sorgt dafür, dass Daten nur über eine sichere HTTPS-Verbindung übertragen werden. Wichtig für die IT-Sicherheit: Der direkte administrative Zugriff auf die n8n-Benutzeroberfläche sollte auf das eigene Firmennetzwerk oder ein sicheres Virtual Private Network (VPN) wie Tailscale beschränkt werden, um Angriffsflächen von außen zu minimieren. Ein offenes n8n-Interface im Internet stellt ein erhebliches Sicherheitsrisiko dar.",
                ],
            },
            {
                "heading": "Typische Risiken und wie man sie vermeidet",
                "paragraphs": [
                    "Wer die Verantwortung für seine eigene n8n-Instanz übernimmt, muss auch den Betrieb absichern. Aus der Praxis wissen wir, dass drei typische Risiken den Erfolg gefährden können, wenn sie nicht von Anfang an eingeplant werden:",
                ],
                "list": [
                    "Fehlende Backups: Ein Serverausfall oder ein fehlerhaftes Update kann die mühsam gebauten Workflows zerstören. Ohne regelmäßige Backups der n8n-Datenbank und der Workflow-Konfigurationen ist die Arbeit von Wochen verloren. Wir empfehlen automatisierte, tägliche Backups an einem separaten Speicherort (z. B. ver-schlüsselt in einem externen Cloud-Storage oder auf einem Backup-Server).",
                    "Unkontrollierte Updates: n8n veröffentlicht in sehr kurzen Abständen Updates mit neuen Funktionen und Sicherheitsfixes. Einfach blind zu aktualisieren kann dazu führen, dass bestehende Konnektoren nicht mehr funktionieren oder Workflows abbrechen. Ein definierter Update-Prozess, bei dem Aktualisierungen zuerst in einer Testumgebung geprüft werden, ist Pflicht für jeden stabilen Betrieb.",
                    "Workflows ohne Fehlerbehandlung: Wenn ein verbundenes System (z. B. Ihre Buchhaltungssoftware oder ein E-Mail-Provider) kurzzeitig offline ist, bricht der n8n-Workflow ab. Ohne eine eingebaute Fehler- und Benachrichtigungslogik bemerken Sie den Ausfall oft erst Tage später, wenn wichtige Daten im Zielsystem fehlen. Jeder produktive Workflow benötigt daher eine automatische Fehlerbehandlung (Retries) und eine Alarmierung (z. B. via Mail oder Messenger), wenn ein Fehler dauerhaft auftritt.",
                ],
            },
            {
                "heading": "Lohnt sich selbst gehostetes n8n für Ihr Unternehmen?",
                "paragraphs": [
                    "Ob sich das Self-Hosting lohnt, ist keine emotionale Entscheidung, sondern eine Rechenaufgabe. Für Unternehmen, die lediglich zwei einfache Abläufe im Monat ausführen und keine sensiblen Daten verarbeiten, ist die n8n-Cloud meist der unkompliziertere Weg. Der Wartungsaufwand entfällt und man kann direkt starten, ohne sich um Infrastruktur kümmern zu müssen.",
                    "Sobald jedoch Geschäftsprozesse automatisiert werden, die täglich laufen, sensible Kundendaten enthalten oder komplexe Integrationen erfordern, ist das Self-Hosting wirtschaftlich und datenschutzrechtlich überlegen. Der einmalige Aufwand für die Einrichtung der Infrastruktur amortisiert sich schnell durch die eingesparten Lizenzkosten und die absolute Kontrolle über die eigenen Daten. Skalantech unterstützt Sie dabei: Wir bauen Ihre n8n-Infrastruktur auf, richten Backups und Monitoring ein und sorgen dafür, dass Ihre Workflows stabil, sicher und wartungsarm laufen. So nutzen Sie alle Vorteile der Open-Source-Plattform ohne das Betriebsrisiko.",
                ],
            },
        ],
        "related_service": "n8n-automatisierung",
        "related_branche": "branchen-handwerk",
        "cta_text": "n8n-Automatisierung besprechen",
        "next_step": {
            "kind": "prozess",
            "label": "n8n-Automatisierung im Überblick",
            "target": "n8n-automatisierung",
            "hint": "Prozessseite: Aufbau, Backups und Betrieb Ihrer selbst gehosteten n8n-Instanz.",
        },
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
                    "Die Nutzung von Cloud-KI (z. B. über die APIs von OpenAI, Anthropic oder Microsoft) ist der schnellste Weg, um mit Künstlicher Intelligenz im Unternehmen zu starten. Die Modelle sind sofort einsatzbereit, bieten eine extrem hohe Leistung bei komplexen Text- und Analyseaufgaben und erfordern keinerlei eigene Hardware-Investitionen. Sie bezahlen nur das, was Sie tatsächlich nutzen (Pay-per-Token). Neue Modellgenerationen stehen Ihnen sofort ohne Mehraufwand zur Verfügung.",
                    "Doch dieser Komfort hat Kehrseiten. Der erste kritische Punkt ist der Datenschutz. Sobald Sie sensible Kundendaten, Verträge oder interne Finanzberichte an eine externe Cloud-API senden, geben Sie die Kontrolle über diese Daten ab. Selbst wenn die Anbieter vertraglich zusichern, die Daten nicht für das Training ihrer Modelle zu nutzen, verbleibt ein Restrisiko bezüglich Datensicherheit, Datenübertragung und Compliance (z. B. nach DSGVO). Der zweite Punkt betrifft die Kosten. Was bei geringer Nutzung nach Cent-Beträgen aussieht, kann bei kontinuierlicher Verarbeitung großer Datenmengen (z. B. der täglichen Analyse aller eingehenden Kunden-E-Mails) schnell zu einer unvorhersehbaren monatlichen Kostenfalle werden.",
                    "Zusätzlich kommt die strategische Abhängigkeit (Vendor Lock-in) hinzu. Wenn Sie Ihre Geschäftsprozesse tief mit den proprietären APIs eines einzelnen Cloud-Anbieters verzahnen, sind Sie dessen Preispolitik, Service-Level-Agreements und Produktlaufzeiten schutzlos ausgeliefert. Ändert der Anbieter die Preisstruktur oder stellt ein bestimmtes Modell ein, müssen Sie Ihre Workflows unter Zeitdruck anpassen. Auch unvorhersehbare Netzausfälle oder Serverüberlastungen des Anbieters können Ihre automatisierten Prozesse von einer Sekunde auf die andere lahmlegen. Auch Netzwerkausfälle legen Ihre KI-Prozesse sofort lahm und beeinträchtigen Ihren operativen Betrieb.",
                ],
            },
            {
                "heading": "Lokale KI: Was selbst gehostete Modelle leisten",
                "paragraphs": [
                    "Lokale KI bedeutet, dass Open-Source-Modelle (wie Llama 3, Mistral oder Phi) auf Ihrer eigenen Server-Infrastruktur betrieben werden. Werkzeuge wie Ollama oder lokale Docker-Container machen den Betrieb heute auch für kleinere Betriebe handhabbar. Der herausragende Vorteil ist die absolute Datensouveränität. Da alle Berechnungen lokal auf Ihren eigenen Systemen stattfinden, verlässt kein einziges Bit an vertraulichen Informationen Ihr Unternehmen. Dies ist der einzige Weg, wie Kanzleien, Steuerberater, Arztpraxen oder Behörden KI rechtssicher in ihre Arbeit integrieren können.",
                    "Ein weiterer Vorteil ist die Kostenplanbarkeit. Nach den einmaligen Investitionen in die Hardware (z. B. einen Server mit einer leistungsstarken Grafikkarte mit ausreichend VRAM) fallen für die Modellnutzung keine laufenden Transaktionsgebühren an. Sie können das Modell rund um die Uhr Millionen von Anfragen verarbeiten lassen, ohne dass die Kosten steigen. Dank moderner Quantisierungsmethoden (wie GGUF) können selbst große Modelle ressourcenschonend auf Standard-Hardware betrieben werden. Die Qualität freier Open-Source-Modelle hat in den letzten Monaten zudem massiv aufgeholt. Für Standardaufgaben wie das Extrahieren von Daten aus Belegen, das Vorsortieren von E-Mails oder das Beantworten von Fragen auf Basis interner Dokumente sind lokale Open-Source-Modelle heute oft genauso präzise wie ihre Cloud-Konkurrenten.",
                    "Um lokale Modelle produktiv zu betreiben, ist jedoch die passende Hardwareauswahl entscheidend. Während kleinere Modelle mit 8 Milliarden Parametern (wie Llama-3-8B) bereits auf Consumer-Grafikkarten oder modernen Apple-Silicon-Prozessoren flüssig laufen, benötigen größere Modelle mit 70 Milliarden Parametern professionelle Hardware wie NVIDIA RTX 4090 oder A6000 Grafikkarten. Hier kommt es vor allem auf die VRAM-Größe an. Eine unzureichende Dimensionierung führt zu langen Antwortzeiten (hohe Latenz), was den Einsatz in Echtzeit-Systemen erschwert. Durch die Optimierung von Modellen und das Hinzufügen von spezialisierten Inferenz-Servern (wie vLLM) lassen sich jedoch Antwortraten erzielen, die die Leistung klassischer Cloud-Modelle bei weitem übertreffen.",
                ],
            },
            {
                "heading": "Die wichtigsten Entscheidungskriterien",
                "paragraphs": [
                    "Um die richtige Wahl für Ihr Unternehmen zu treffen, sollten Sie jeden geplanten Use-Case anhand von vier Kriterien prüfen:",
                ],
                "list": [
                    "Schutzbedarf der Daten: Verarbeiten Sie personenbezogene Daten, Geschäftsgeheimnisse oder urheberrechtlich geschützte Dokumente? Wenn ja, spricht das stark für eine lokale Lösung.",
                    "Nutzungsintensität: Handelt es sich um ein internes Tool, das gelegentlich genutzt wird, oder um einen automatisierten Hintergrundprozess, der tausende Dokumente am Tag verarbeitet? Bei hoher Intensität amortisiert sich lokale Hardware extrem schnell.",
                    "Aufgabenkomplexität: Benötigen Sie kreatives Schreiben auf Weltklasse-Niveau und die Lösung hochkomplexer logischer Probleme, oder geht es um das Extrahieren, Strukturieren und Klassifizieren von Daten? Letzteres beherrschen lokale Modelle fehlerfrei.",
                    "Betriebs-Know-how: Haben Sie die IT-Ressourcen, um einen eigenen Server zu betreiben und abzusichern, oder möchten Sie diese Verantwortung lieber an einen Partner wie Skalantech auslagern?",
                ],
            },
            {
                "heading": "Hybrid ist oft die pragmatischste Antwort",
                "paragraphs": [
                    "In der Praxis müssen Sie sich nicht zwingend für einen der beiden Wege entscheiden. Viele erfolgreiche Unternehmen setzen auf ein hybrides Modell. Sensible Kernprozesse – wie die automatische Analyse von Kundenanfragen oder das Durchsuchen der internen Wissensdatenbank – laufen sicher auf einer lokalen KI-Instanz. Unkritische Aufgaben, die eine extrem hohe kognitive Leistung erfordern (z. B. das Übersetzen von Marketingmaterialien oder das Erstellen komplexer Code-Skripte), werden an die Cloud übergeben.",
                    "Ein typisches hybrides Szenario sieht so aus: Ein lokaler Agent analysiert alle eingehenden Kunden-E-Mails und filtert sensible Adressdaten, Bankverbindungen und persönliche Details heraus. Für einfache Klassifizierungsaufgaben nutzt er das lokale Modell. Steht jedoch die Übersetzung eines komplizierten technischen Dokuments an, ruft der Agent eine Cloud-API auf – allerdings erst, nachdem er alle sensiblen Informationen lokal anonymisiert hat. Dies schützt Ihre Unternehmensdaten und nutzt gleichzeitig die volle Flexibilität globaler Cloud-Systeme dort, wo es unkritisch ist.",
                    "Ein durchdachtes IT-Konzept stellt sicher, dass die Datenströme automatisch richtig geleitet werden. Skalantech unterstützt Sie bei dieser Weichenstellung. Wir analysieren Ihre Prozesse, wählen die passenden Modelle aus und bauen eine KI-Architektur auf, die Ihren Datenschutz garantiert und gleichzeitig wirtschaftlich sinnvoll ist. Wir begleiten Sie von der ersten Hardware-Beratung bis zum laufenden Betrieb der Modelle, um eine zukunftssichere und unabhängige Lösung für Ihr Unternehmen zu etablieren.",
                ],
            },
        ],
        "related_service": "lokale-ki",
        "cta_text": "KI-Architektur für Ihr Unternehmen klären",
        "next_step": {
            "kind": "prozess",
            "label": "Lokale KI im Überblick",
            "target": "lokale-ki",
            "hint": "Prozessseite: Selbst gehostete Modelle in Ihrer Infrastruktur – ohne Datenabfluss.",
        },
    },
    "n8n-vs-power-automate": {
        "title": "n8n vs. Power Automate für Unternehmen: Der ehrliche Vergleich",
        "description": "n8n oder Power Automate? Vergleich von Kosten, Self-Hosting, KI-Integration, Datenschutz und Betrieb – und welche Plattform für welchen Use-Case passt.",
        "h1": "n8n vs. Power Automate: Welche Automatisierungsplattform passt zu Ihrem Unternehmen?",
        "intro": (
            "Beide Plattformen lösen dasselbe Grundproblem: Sie verbinden Anwendungen und automatisieren Abläufe. "
            "Die Unterschiede liegen im Detail – bei Kostenmodell, Datenkontrolle, KI-Integration und Betriebsaufwand. "
            "Dieser Artikel vergleicht ehrlich, damit die Entscheidung auf Fakten statt Bauchgefühl basiert."
        ),
        "sections": [
            {
                "heading": "Die Grundidee beider Plattformen",
                "paragraphs": [
                    "Power Automate ist Microsofts Automatisierungsplattform – eng verzahnt mit Microsoft 365, SharePoint, Teams und Dynamics. Wer bereits tief im Microsoft-Ökosystem steckt, kommt damit schnell zu Ergebnissen, weil die Konnektoren und Berechtigungen vorhanden sind. Die Stärke liegt in der Integration: Ein Team, das täglich mit Outlook, Teams und SharePoint arbeitet, bekommt die ersten Workflows ohne große Einarbeitung hin.",
                    "n8n ist eine quelloffene Workflow-Plattform, die als Cloud-Dienst oder selbst gehostet betrieben werden kann. Der visuelle Editor arbeitet mit Nodes, die per Drag-and-drop verbunden werden. Die Stärke von n8n liegt in der Flexibilität: eigene Konnektoren, Webhooks und die volle Kontrolle über den Betrieb. Für ein mittelständisches Unternehmen heißt das konkret: Die Plattform wächst mit den Prozessen, statt dass die Prozesse sich nach der Plattform richten müssen.",
                    "Die eigentliche Frage lautet nicht „welche Plattform ist besser“, sondern „welche Plattform passt zu unseren Systemen, unseren Daten und unserer Art zu arbeiten“. Beide Werkzeuge können dasselbe Ergebnis liefern: ein Angebot, das automatisch aus einer Anfrage entsteht, eine Rechnung, die ohne Handarbeit im System landet, eine Terminerinnerung, die von selbst rausgeht.",
                ],
            },
            {
                "heading": "Kosten: Das größte Missverständnis",
                "paragraphs": [
                    "Power Automate klingt oft kostenlos, weil es im Microsoft-365-Abonnement enthalten ist – tatsächlich gilt das nur für eine eingeschränkte Basisversion. Sobald Premium-Konnektoren, höhere Ausführungslimits oder Policies ins Spiel kommen, entstehen pro Benutzer oder pro Ausführung Kosten, die mit dem Umfang der Automatisierung wachsen. Gerade bei Prozessen, die täglich und in hoher Frequenz laufen, summieren sich diese Kosten schneller, als die Planung es vorsieht.",
                    "n8n ist in der quelloffenen Community-Version lizenzkostenfrei. Die Kosten bestehen aus Infrastruktur (bei Self-Hosting ein kleiner Server) und Umsetzung. Ein Beispiel aus der Praxis: Der kleinste n8n-Cloud-Tarif kostet rund 50 Euro pro Monat und erlaubt 2.500 Workflow-Ausführungen. Ein Betrieb, der ein CRM stündlich mit einem Rechnungstool synchronisiert oder täglich Belegdaten verarbeitet, erreicht diese Grenze in wenigen Tagen – und steigt dann in teurere Tarife auf. Selbst gehostet fallen dagegen nur die Serverkosten von 10 bis 20 Euro im Monat an, unabhängig davon, ob ein Workflow zehnmal oder zehntausendmal am Tag läuft.",
                    "Die Kostenfalle liegt also nicht in der Plattform selbst, sondern in der Menge der Ausführungen. Wer viele automatisierte Prozesse plant, sollte das Kostenmodell vorher durchrechnen – nicht erst, wenn die Rechnung des Anbieters höher ausfällt als erwartet.",
                ],
            },
            {
                "heading": "Datenschutz und Datenkontrolle",
                "paragraphs": [
                    "Der wichtigste Unterschied: n8n lässt sich vollständig selbst hosten. Workflow-Daten, Zwischenschritte und Protokolle bleiben dann in der eigenen Infrastruktur – für viele Unternehmen mit sensiblen Daten der entscheidende Punkt. Kundendaten, Rechnungen und interne Prozessdaten verlassen das Haus nicht. Das vereinfacht die Einhaltung der DSGVO und macht die Datenflüsse für Kunden und Prüfer nachvollziehbar.",
                    "Power Automate läuft in der Microsoft-Cloud. Für Unternehmen im Microsoft-365-Ökosystem ist das oft vertraglich sauber geregelt, aber die Daten verlassen die eigene Umgebung. Bei strengen Compliance-Anforderungen – etwa in Kanzleien, bei Steuerberatern oder im Gesundheitswesen – kann das ein Ausschlusskriterium sein, selbst wenn die Verträge sauber sind.",
                    "Wer beide Welten kombiniert, bekommt das Beste aus beiden: unkritische Abläufe in der Microsoft-Welt, sensible Prozesse auf eigener Infrastruktur. Diese Trennung ist technisch kein Problem – sie muss nur von Anfang an mitgedacht werden, statt nachträglich eingebaut zu werden.",
                ],
            },
            {
                "heading": "KI-Integration: Wo die Plattformen heute stehen",
                "paragraphs": [
                    "Beide Plattformen können KI-Schritte einbinden. Power Automate bietet mit Copilot und vorgefertigten KI-Konnektoren einen bequemen Weg für Microsoft-Nutzer – allerdings meist innerhalb des Microsoft-Universums. Wer mit Microsoft 365 arbeitet, bekommt damit schnell brauchbare Ergebnisse, bleibt aber an das Ökosystem gebunden.",
                    "n8n ist offener: LLM-Nodes erlauben die Anbindung beliebiger Modelle – OpenAI, Anthropic, aber auch selbst gehostete Modelle über Ollama. Wer lokale oder hybride KI-Lösungen plant, hat mit n8n mehr Freiheit. Das ist dort relevant, wo vertrauliche Daten nicht an externe KI-Dienste gehen sollen: Ein KI-Agent, der Angebote aus Kundenanfragen erstellt oder Rechnungen prüft, verarbeitet oft personenbezogene Daten. Läuft das Modell lokal, bleibt alles im Haus.",
                    "Für die Praxis bedeutet das: Power Automate ist der schnelle Weg für Microsoft-nahe KI-Aufgaben. n8n ist der Weg für KI, die in bestehende, heterogene Systemlandschaften integriert werden soll – und für Prozesse, bei denen Datenschutz die Modellwahl bestimmt.",
                ],
            },
            {
                "heading": "Betriebsaufwand: Wer kümmert sich um die Automatisierung?",
                "paragraphs": [
                    "Eine Automatisierung ist kein Bauprojekt, sondern ein Betriebsthema. Workflows müssen überwacht werden, Schnittstellen ändern sich, Updates können Funktionen beeinflussen. Genau hier entscheidet sich, ob eine Plattform langfristig trägt.",
                    "Power Automate entlastet den Betrieb: Microsoft kümmert sich um Verfügbarkeit und Updates. Dafür sind Sie an die Plattform gebunden – inklusive Preisänderungen und Produktentscheidungen des Anbieters. Bei n8n in der Cloud-Variante ist der Betrieb ebenfalls abgedeckt; beim Self-Hosting übernehmen Sie oder ein IT-Partner die Verantwortung für Server, Backups, Updates und Monitoring.",
                    "Wer keine IT-Abteilung hat, sollte den Betriebsaufwand nicht unterschätzen. Die gute Nachricht: Genau dafür gibt es Umsetzungspartner, die Infrastruktur und Workflows aufsetzen und den Betrieb überwachen – zum Beispiel Skalantech. Dann bleibt die Plattformwahl eine Kosten- und Datenschutzfrage, nicht eine Frage des eigenen IT-Könnens.",
                ],
            },
            {
                "heading": "Für wen lohnt sich welche Plattform?",
                "paragraphs": [
                    "Power Automate ist die pragmatische Wahl, wenn das Unternehmen vollständig auf Microsoft 365 setzt, die Teams dort arbeiten und keine Datenkontrolle außerhalb der Cloud gefordert ist. Die Einarbeitung ist flach, die Integration in Teams/SharePoint out-of-the-box. Typische Fälle: Freigabeprozesse, Dokumenten-Workflows, Benachrichtigungen innerhalb des Microsoft-Universums.",
                    "n8n lohnt sich, wenn heterogene Systeme verbunden werden müssen, Kosten skalierbar bleiben sollen, KI flexibel eingebunden wird oder Datenschutz Self-Hosting erfordert. Typische Fälle: Terminbuchung aus E-Mail-Anfragen, Rechnungsverarbeitung mit OCR, E-Mail-Routing mit KI, Synchronisation zwischen CRM, Buchhaltung und Dateiablage. Der Betrieb erfordert etwas mehr technische Verantwortung – genau dort unterstützt Skalantech.",
                    "Ein hybrider Ansatz ist üblich und legitim: Microsoft-interne Abläufe per Power Automate, unternehmenskritische und KI-lastige Workflows per n8n. Wichtig ist nur, die Grenze bewusst zu ziehen und nicht zwei Plattformen für dieselbe Aufgabe zu betreiben.",
                ],
            },
            {
                "heading": "Fünf Prüffragen für die Entscheidung",
                "paragraphs": [
                    "Statt sich von Feature-Listen beeindrucken zu lassen, hilft ein klarer Fragenkatalog:",
                ],
                "list": [
                    "In welchen Systemen leben unsere Daten? – Alles bei Microsoft: Power Automate ist der naheliegende Weg. Gemischte Landschaft: n8n verbindet flexibler.",
                    "Wie viele Ausführungen pro Monat sind realistisch? – Bei hoher Frequenz spricht das Kostenmodell klar für selbst gehostetes n8n.",
                    "Dürfen die Daten die eigene Umgebung verlassen? – Nein: Self-Hosting mit n8n ist die einzige saubere Antwort.",
                    "Soll KI in den Prozessen stecken? – Dann prüfen, welche Modelle angebunden werden können und ob lokale Modelle eine Option sein müssen.",
                    "Wer betreibt das System? – Ohne eigene IT einen Partner einplanen, sonst wird aus der Automatisierung ein Wartungsprojekt.",
                ],
            },
            {
                "heading": "Der pragmatische Einstieg",
                "paragraphs": [
                    "Die Plattformfrage lässt sich nicht im Konferenzraum entscheiden, sondern an einem konkreten Prozess. Empfehlung: einen einzelnen, klar abgegrenzten Ablauf nehmen – etwa die automatische Erfassung eingehender Rechnungen oder die Terminbuchung aus Anfragen – und diesen in beiden Systemen als Prototyp bauen lassen. Der Vergleich zeigt dann schnell, wo die Reise hingehen soll: bei Kosten, Datenschutz und Betriebsaufwand.",
                    "Skalantech begleitet diese Entscheidung mit konkreten Zahlen statt Beratungsfloskeln: Wir analysieren Ihre Prozesse, rechnen die Kostenmodelle durch und setzen die Automatisierung auf der passenden Plattform um – auf Wunsch vollständig selbst gehostet, DSGVO-konform und in bestehende Systeme integriert.",
                ],
            },
        ],
        "related_service": "n8n-automatisierung",
        "cta_text": "n8n-Automatisierung besprechen",
        "next_step": {
            "kind": "potenzial",
            "label": "Potenzial-Check starten",
            "target": "rechner",
            "hint": "In 30 Sekunden: Was Ihre manuellen Prozesse pro Jahr kosten – mit Ihren Zahlen.",
        },
        "published": "2026-08-28",
    },
    "welche-prozesse-ki-automatisierung": {
        "title": "Welche Prozesse eignen sich für KI-Automatisierung? Ein Prüfschema",
        "description": "Nicht jeder Prozess braucht KI. Mit einem klaren Prüfschema erkennen Sie, welche Abläufe sich für KI-Automatisierung lohnen – und welche besser manuell bleiben.",
        "h1": "Welche Prozesse eignen sich für KI-Automatisierung?",
        "intro": (
            "KI-Automatisierung verspricht weniger manuelle Arbeit – aber nicht jeder Prozess eignet sich dafür. "
            "Wer wahllos automatisiert, schafft Wartungsaufwand statt Wert. Dieses Prüfschema hilft, die richtigen Kandidaten zu erkennen."
        ),
        "sections": [
            {
                "heading": "Das Grundprinzip: Regelmäßigkeit plus klare Regeln",
                "paragraphs": [
                    "Der ideale Automatisierungskandidat ist ein Prozess, der regelmäßig vorkommt, klare Schritte hat und dessen Ergebnis erwartbar ist. Je häufiger ein Ablauf läuft und je klarer die Regeln sind, desto höher der Nutzen. Ein Ablauf, der einmal im Monat stattfindet und fünf Minuten dauert, bleibt besser manuell – die Einsparung rechtfertigt den Aufwand nicht.",
                    "KI kommt dort ins Spiel, wo Regeln allein nicht reichen: wenn unstrukturierte Daten (Texte, E-Mails, Dokumente) verstanden werden müssen. Reine Datenübertragung braucht keine KI – nur saubere Integration. Der Unterschied ist wichtig für die Kostenplanung: Eine klassische Integration ist günstig und vorhersagbar. Ein KI-Schritt kostet mehr, lohnt sich aber genau dort, wo ein Mensch bisher lesen, verstehen und entscheiden musste.",
                ],
            },
            {
                "heading": "Vier Fragen, die jeder Prozess beantworten muss",
                "paragraphs": [
                    "Bevor ein Prozess automatisiert wird, sollten vier Fragen beantwortet sein. Sie trennen schnell die Kandidaten von den Nicht-Kandidaten:",
                ],
                "list": [
                    "Wie oft läuft der Ablauf? – Einmal im Monat lohnt selten; täglich oder stündlich fast immer.",
                    "Wie viel Zeit kostet er manuell? – Ab etwa einer Stunde pro Woche wird Automatisierung wirtschaftlich interessant.",
                    "Sind die Regeln klar? – Ja: klassische Integration. Teilweise: KI kann die Lücke füllen. Gar nicht: erst Prozess stabilisieren.",
                    "Was passiert bei Fehlern? – Automatisierung braucht definierte Fehlerpfade, sonst entsteht stille Datenkorruption.",
                ],
            },
            {
                "heading": "Ein Rechenbeispiel aus dem Handwerk",
                "paragraphs": [
                    "Ein typischer Handwerksbetrieb zeigt, wie schnell sich die Antworten zu einer klaren Rechnung summieren. Die Zahlen stammen aus dem Skalantech-ROI-Rechner und sind konservative Defaults: 15 Angebote pro Monat à 90 Minuten ergeben 22,5 Stunden Bürozeit pro Monat. 20 Rechnungen à 30 Minuten kommen auf weitere 10 Stunden. Dazu 10 Kundenanfragen pro Woche à 15 Minuten – noch einmal 2,5 Stunden pro Woche.",
                    "Hochgerechnet auf ein Jahr sind das 520 Stunden Bürozeit: 22,5 Stunden × 12 Monate plus 10 Stunden × 12 Monate plus 2,5 Stunden × 52 Wochen. Bei einem Stundensatz von 65 Euro entspricht das einem Wert von rund 33.800 Euro pro Jahr – oder 65 vollen Arbeitstagen. Das ist kein Einzelfall, sondern die typische Ausgangslage in Betrieben ohne systematische Automatisierung. Angebote, Rechnungen und Anfragen sind genau die Prozesse, die das Prüfschema als Kandidaten identifiziert: regelmäßig, zeitintensiv, mit klaren Regeln – und mit unstrukturierten Eingaben (E-Mails, Fotos, Notizen), für die sich KI lohnt.",
                ],
            },
            {
                "heading": "Klassiker, die sich fast immer lohnen",
                "paragraphs": [
                    "In der Praxis dominieren einige wiederkehrende Muster, die unabhängig von der Branche funktionieren. Sie haben zwei Gemeinsamkeiten: Sie kosten regelmäßig Zeit, und ihre Regeln sind beschreibbar – auch wenn die Eingaben unstrukturiert sind:",
                ],
                "list": [
                    "Datenübertragung zwischen Systemen (CRM, ERP, Tabellen, Dateiablagen) – regelbasiert, hoher Zeitfresser.",
                    "Eingangsverarbeitung: Rechnungen, Belege, Bestellungen erfassen und prüfen – dank OCR/KI auch bei unstrukturierten Dokumenten.",
                    "Berichtserstellung: Kennzahlen aus mehreren Quellen sammeln und aufbereiten – ersetzt tägliche Copy-Paste-Arbeit.",
                    "E-Mail-Klassifizierung und -Routing: Anfragen erkennen, priorisieren, weiterleiten – idealer KI-Einsatz.",
                    "Dokumentation: Aus Meetings und Notizen strukturierte Unterlagen erzeugen – spart Fachkräftezeit.",
                    "Terminbuchung und -erinnerung: Anfragen per E-Mail oder Telefon in bestätigte Termine verwandeln, Erinnerungen automatisch versenden – reduziert No-Shows spürbar.",
                ],
            },
            {
                "heading": "Der Unterschied: Integration, Automatisierung, KI",
                "paragraphs": [
                    "Drei Begriffe werden im Alltag oft durcheinandergeworfen – die Unterscheidung entscheidet aber über Umfang und Kosten des Projekts. Eine Integration verbindet zwei Systeme: Das CRM schreibt eine Adresse automatisch in die Buchhaltung, wenn ein Kunde angelegt wird. Eine Automatisierung führt eine Abfolge von Schritten aus: Wenn eine Rechnung eingeht, wird sie gespeichert, geprüft und zur Freigabe weitergeleitet. KI kommt hinzu, wenn ein Schritt Verständnis erfordert: eine E-Mail lesen, eine Anfrage einsortieren, aus einem Foto ein Angebot ableiten.",
                    "Für die Praxis heißt das: Nicht jeder Prozess braucht KI, und wer KI dort einsetzt, wo eine einfache Regel reicht, zahlt unnötig. Der umgekehrte Fall ist häufiger: Prozesse scheitern an unstrukturierten Eingaben, obwohl eine saubere Integration die Hälfte des Problems gelöst hätte. Ein ehrlicher Blick auf den Ist-Zustand – welche Systeme reden schon miteinander, welche nicht – ist deshalb der erste Schritt jeder Automatisierung.",
                ],
            },
            {
                "heading": "Branchenblick: Wo der Nutzen sofort sichtbar wird",
                "paragraphs": [
                    "Das Prüfschema lässt sich auf jede Branche anwenden. Drei Beispiele zeigen, wie unterschiedlich die Kandidaten aussehen können:",
                ],
                "list": [
                    "Handwerk: Angebote aus Anfragen erstellen, Rechnungen automatisch versenden, Termine buchen. Der Einstieg ist ein einzelner Prozess – etwa die Angebotserstellung – und die Wirkung ist direkt messbar in Stunden.",
                    "Kfz-Werkstatt: Telefonische Terminanfragen in Buchungen verwandeln, Erinnerungen an HU/TÜV und Service-Termine automatisch versenden, Kunden nach dem Werkstattbesuch um Bewertung bitten. Das reduziert No-Shows und hält die Werkstatt ausgelastet.",
                    "Kanzlei und Steuerberatung: Eingangsrechnungen und Belege vorstrukturieren, Fristen aus Dokumenten extrahieren, Mandatsanfragen beantworten. Hier zählt zusätzlich der Datenschutz: lokale KI hält Mandantendaten im Haus.",
                ],
            },
            {
                "heading": "Wo Automatisierung (noch) nicht funktioniert",
                "paragraphs": [
                    "Nicht geeignet sind Prozesse mit hohem Ermessensspielraum, fehlenden Daten oder stark schwankender Qualität. Wenn das Ergebnis von Verhandlung, Gefühl oder Menschenkenntnis abhängt – etwa bei der Preisfindung in komplexen Projekten oder der Entscheidung über personelle Maßnahmen –, bleibt die Automatisierung auf Vorbereitung beschränkt. Sie kann Informationen zusammentragen, die Entscheidung trifft weiterhin der Mensch.",
                    "Auch Prozesse, die sich ständig ändern, sind schwierige Kandidaten: Jede Änderung bedeutet Wartung. Die Regel lautet: erst stabilisieren, dann automatisieren. Wer einen chaotischen Ablauf digitalisiert, automatisiert das Chaos – und bezahlt die Folgen dauerhaft im Betrieb.",
                ],
            },
            {
                "heading": "Der pragmatische Einstieg",
                "paragraphs": [
                    "Statt einer großen Automatisierungsstrategie lohnt der Start mit einem einzelnen Prozess: Zeitaufwand messen, Ablauf dokumentieren, Lösung bauen, Ergebnis kontrollieren. Sobald ein Workflow im Alltag trägt, wird das nächste Kandidatenschema durchlaufen.",
                    "Wichtig ist die Erfolgsmessung: Wie viele Stunden spart die Automatisierung wirklich? Nur messbare Ergebnisse rechtfertigen den nächsten Schritt – und machen den Unterschied zwischen Automatisierung als Projekt und Automatisierung als Prozess. Skalantech startet deshalb immer mit einer kurzen Prozessanalyse: Wir identifizieren gemeinsam die zwei oder drei Kandidaten mit dem größten Hebel, rechnen den Nutzen mit Ihren Zahlen durch und setzen den ersten Quick-Win in Tagen um – nicht in Quartalen.",
                ],
            },
        ],
        "related_service": "ki-automatisierung",
        "cta_text": "KI-Potenzial in Ihren Prozessen prüfen",
        "next_step": {
            "kind": "potenzial",
            "label": "Potenzial-Check starten",
            "target": "rechner",
            "hint": "Prüfen Sie mit Ihren Zahlen, welche Prozesse sich für die Automatisierung lohnen.",
        },
        "published": "2026-08-28",
    },
    "rag-wissensassistenten": {
        "title": "RAG und Wissensassistenten: So wird Unternehmenswissen nutzbar",
        "description": "RAG erklärt: Wie Wissensassistenten mit Retrieval-Augmented Generation Fragen auf Basis Ihrer Dokumente beantworten – inklusive Grenzen und Datenschutz.",
        "h1": "RAG und Wissensassistenten: So wird Unternehmenswissen nutzbar",
        "intro": (
            "Viele Unternehmen besitzen wertvolles Wissen in Handbüchern, Verträgen und internen Dokumenten – "
            "aber niemand kann es systematisch nutzen. Wissensassistenten auf Basis von RAG versprechen Abhilfe. "
            "Dieser Artikel erklärt, wie die Technik funktioniert, wo sie Grenzen hat und wie der Einstieg pragmatisch gelingt."
        ),
        "sections": [
            {
                "heading": "Das Grundproblem: Wissen liegt in Dokumenten, nicht in Köpfen",
                "paragraphs": [
                    "Generative KI-Modelle beantworten Fragen auf Basis ihres Trainingswissens – nicht auf Basis Ihrer Unterlagen. Wer ein internes Handbuch auswerten will, bekommt von einem allgemeinen Chatbot bestenfalls allgemeine Antworten, im schlimmsten Fall plausible Fehler. Ein Modell, das im Internet trainiert wurde, kennt weder Ihre Prozessanweisungen noch Ihre Vertragsklauseln noch Ihre Produktdaten.",
                    "Die Lösung heißt RAG: Retrieval-Augmented Generation. Das Modell wird nicht neu trainiert, sondern bekommt vor der Antwort die relevanten Passagen aus Ihren eigenen Dokumenten als Kontext – und kann so präzise, belegbare Antworten liefern. Der Unterschied zum klassischen Chatbot: Statt aus dem Gedächtnis zu antworten, schlägt der Assistent in Ihren Unterlagen nach und formuliert die Antwort auf Basis der gefundenen Stellen.",
                ],
            },
            {
                "heading": "Wie RAG funktioniert: Drei Schritte",
                "paragraphs": [
                    "RAG besteht technisch aus drei Komponenten, die zusammenarbeiten:",
                ],
                "list": [
                    "Indexierung: Dokumente werden in sinnvolle Abschnitte geteilt und in einer Vektordatenbank abgelegt – mit semantischen Embeddings, die Bedeutung statt nur Stichworte erfassen.",
                    "Abruf (Retrieval): Bei einer Frage werden die passendsten Abschnitte per Ähnlichkeitssuche gefunden – meist nur wenige aus oft tausenden Dokumenten.",
                    "Generierung: Das Sprachmodell bekommt die Frage plus die gefundenen Abschnitte und formuliert eine Antwort, die auf diesen Quellen basiert.",
                ],
            },
            {
                "heading": "Typische Einsatzfälle in Unternehmen",
                "paragraphs": [
                    "RAG lohnt sich überall dort, wo Fachwissen aus Dokumenten abgerufen werden muss. Die Muster wiederholen sich branchenübergreifend:",
                ],
                "list": [
                    "Interne Wissenssuche: Mitarbeiter fragen Richtlinien, Prozesse oder Standards ab, statt in Ordnern zu suchen.",
                    "Support und Dokumentation: Kunden- oder Serviceteams bekommen Antworten aus Handbüchern und bekannten Fehlerlösungen.",
                    "Vertrags- und Aktenprüfung: Relevante Klauseln, Fristen oder Risiken werden aus Verträgen extrahiert und zusammengefasst.",
                    "Onboarding: Neue Mitarbeiter erhalten Antworten auf Basis der internen Doku – ohne jemanden zu unterbrechen.",
                    "Kanzleien und Steuerberatung: Akten und Mandatsunterlagen zusammenfassen, Fristen und Fallstricke herausziehen – mit lokaler KI, damit Mandantendaten das Haus nicht verlassen.",
                ],
            },
            {
                "heading": "Was RAG nicht ist: Die ehrlichen Grenzen",
                "paragraphs": [
                    "RAG ist keine Fakten-Engine. Die Antwortqualität hängt direkt von der Qualität und Vollständigkeit der Dokumente ab – fehlt eine Information, kann das Modell sie nicht erfinden, aber es kann Lücken unsauber überbrücken. Deshalb gehören Quellenangaben und eine Freigabeschleife für kritische Antworten zum Design. Wer eine Antwort auf eine Vertragsfrage erhält, muss nachvollziehen können, auf welcher Klausel sie beruht.",
                    "Auch die Aufbereitung ist nicht trivial: Scans ohne Texterkennung, widersprüchliche Dokumente oder sehr lange, unstrukturierte Dateien senken die Qualität. Wer RAG einführt, sollte zuerst die Dokumentenqualität prüfen. Ein weiterer Punkt: Die Antworten sind nur so aktuell wie der Index. Ändern sich Dokumente, muss der Index neu aufgebaut oder inkrementell aktualisiert werden – sonst antwortet der Assistent mit veraltetem Wissen, was im schlimmsten Fall teurer ist als gar keine Antwort.",
                ],
            },
            {
                "heading": "Ein Beispiel aus dem Alltag: Das Service-Handbuch",
                "paragraphs": [
                    "Der typische Fall lässt sich an einem Service-Team mit einem dicken Handbuch erklären. Das Handbuch enthält Antworten auf die häufigsten Kundenfragen – aber niemand findet die passende Stelle schnell genug, und jede Antwort kostet Recherchezeit. Ein RAG-Wissensassistent macht aus diesem Handbuch ein Werkzeug: Ein Mitarbeiter fragt „Was gilt bei einem Widerruf nach 14 Tagen?“, der Assistent findet die relevanten Abschnitte, nennt die Antwort und verweist auf die Fundstelle.",
                    "Der Nutzen ist doppelt: Der Mitarbeiter bekommt eine belegbare Antwort in Sekunden statt nach Minuten der Suche, und neue Kollegen arbeiten vom ersten Tag an mit dem gesammelten Wissen des Teams – ohne dass erfahrene Kollegen jede Frage zweimal beantworten müssen. Derselbe Mechanismus funktioniert mit Richtlinien, Verträgen, Betriebsanleitungen oder Prüfprotokollen.",
                ],
            },
            {
                "heading": "Qualität messen: So erkennen Sie, ob der Assistent trägt",
                "paragraphs": [
                    "Bevor ein Wissensassistent produktiv geht, gehört ein Test mit echten Fragen dazu. Bewährt hat sich ein Fragenkatalog von 20 bis 50 typischen Fragen, deren richtige Antworten vorher festgelegt sind. Dann wird gemessen: Wie viele Antworten sind korrekt, wie viele verweisen auf die richtige Quelle, wie viele sind unbrauchbar? Eine Trefferquote von 90 Prozent und mehr bei den Kernfragen ist ein realistisches Ziel für einen gut aufbereiteten Pilot.",
                    "Wichtig ist auch der Umgang mit Unsicherheit: Ein guter Assistent sagt „dazu finde ich keine Angabe“, statt eine plausible Antwort zu erfinden. Diese Fähigkeit zur ehrlichen Auskunft lässt sich im Test direkt prüfen, indem man gezielt Fragen stellt, die im Dokumentenbestand nicht beantwortet werden. Erst wenn Qualität, Quellenbezug und Ehrlichkeit stimmen, lohnt der Ausbau auf weitere Wissensbereiche.",
                ],
            },
            {
                "heading": "Datenschutz: Lokal oder in der Cloud?",
                "paragraphs": [
                    "Der entscheidende Vorteil von RAG: Die Dokumente müssen das Unternehmen nicht verlassen. Bei einem selbst gehosteten Setup mit lokalen Modellen bleiben Index, Abruf und Generierung vollständig in der eigenen Infrastruktur. Für Kanzleien, Steuerberater, Arztpraxen oder Betriebe mit sensiblen Kundendaten ist das oft die einzige zulässige Variante – denn Mandats-, Patienten- oder Kundendaten dürfen nicht an beliebige Cloud-Dienste fließen.",
                    "Für unkritische Inhalte kann auch eine Cloud-Variante mit vertraglicher Absicherung sinnvoll sein. Die Faustregel: Je sensibler die Dokumente, desto eher gehört das System nach innen. Moderne lokale Modelle (etwa über Ollama betrieben) liefern für Zusammenfassungen, Klassifikationen und Fragen mit Quellenbezug heute eine Qualität, die für die meisten internen Anwendungen ausreicht – ohne dass Daten das Haus verlassen.",
                ],
            },
            {
                "heading": "Der pragmatische Einstieg",
                "paragraphs": [
                    "RAG beginnt nicht mit der Technik, sondern mit einer konkreten Frage: Welches Dokumenten-Set beantwortet welche wiederkehrenden Fragen? Ein Pilot mit einer klar abgegrenzten Doku (z. B. ein Handbuch oder eine Richtlinien-Sammlung) zeigt schnell, ob Qualität und Nutzen stimmen. Ein Pilot sollte nicht größer sein als nötig – zehn bis fünfzig saubere Dokumente reichen, um den Nutzen zu bewerten.",
                    "Wichtig ist die Erfolgsmessung: Beantwortet der Assistent typische Fragen korrekt? Werden Quellen angegeben? Erspart er messbar Zeit? Erst wenn ein Pilot trägt, lohnt der Ausbau auf weitere Wissensbereiche. Skalantech setzt Wissensassistenten auf bestehender Infrastruktur um – selbst gehostet, mit klaren Quellenangaben und einem Freigabeprozess für kritische Antworten. So bleibt das Wissen im Haus und der Assistent wird zum Werkzeug, dem Mitarbeiter vertrauen.",
                ],
            },
        ],
        "related_service": "ki-agenten",
        "cta_text": "Wissensassistenten mit Ihren Daten prüfen",
        "next_step": {
            "kind": "prozess",
            "label": "KI-Agenten im Überblick",
            "target": "ki-agenten",
            "hint": "Prozessseite: Wissensassistenten und RAG im Unternehmenseinsatz.",
        },
        "published": "2026-08-28",
    },
    "kosten-roi-ki-automatisierung": {
        "title": "Kosten und ROI von KI-Automatisierung: Was sich wirklich lohnt",
        "description": "KI-Automatisierung rechnet sich nicht immer. Mit einer ehrlichen Kosten-Nutzen-Rechnung erkennen Sie, welche Prozesse sich automatisieren lassen – und welche nicht.",
        "h1": "Kosten und ROI von KI-Automatisierung: Was sich wirklich lohnt",
        "intro": (
            "Automatisierung kostet zuerst Zeit und Geld – Umsetzung, Betrieb, Wartung. "
            "Wann rechnet sich das? Dieser Artikel liefert einen ehrlichen Rechenweg, "
            "damit die Entscheidung auf Zahlen statt auf Hype basiert."
        ),
        "sections": [
            {
                "heading": "Die vier Kostenarten, die fast immer unterschätzt werden",
                "paragraphs": [
                    "Eine Automatisierung besteht aus mehr als dem Bau des Workflows. Vollständig gerechnet gehören dazu:",
                ],
                "list": [
                    "Prozessanalyse: Den Ablauf verstehen, dokumentieren, Engpässe und Ausnahmen identifizieren – oft 20–30 Prozent des Gesamtaufwands.",
                    "Umsetzung: Workflow bauen, Schnittstellen anbinden, Testen mit echten Daten.",
                    "Betrieb: Monitoring, Fehlerbehebung, Updates und Anpassungen an veränderte Systeme – die Dauerlast.",
                    "Lizenz- und Infrastrukturkosten: Plattformgebühren, Server, ggf. KI-API-Kosten pro Aufruf.",
                ],
            },
            {
                "heading": "Die Nutzenrechnung: Zeitersparnis und mehr",
                "paragraphs": [
                    "Der Kernnutzen ist fast immer Zeit. Wer die manuelle Arbeit in Stunden pro Woche kennt, kann rechnen: Stunden pro Woche mal Wochen pro Jahr mal Stundensatz ergibt den jährlichen Wert der Automatisierung.",
                    "Daneben zählen: vermiedene Fehlerkosten (Übertragungsfehler, vergessene Schritte), schnellere Durchlaufzeiten (Kundenzufriedenheit) und Skaleneffekte (mehr Volumen ohne mehr Personal).",
                ],
            },
            {
                "heading": "Ein konkretes Beispiel: Der typische Handwerksbetrieb",
                "paragraphs": [
                    "Die Rechnung lässt sich an einem typischen Handwerksbetrieb durchspielen. Die Zahlen stammen aus dem Skalantech-ROI-Rechner und sind bewusst konservative Defaults – keine Werbeversprechen, sondern eine nachvollziehbare Ausgangslage.",
                    "Der Betrieb erstellt 15 Angebote pro Monat à 90 Minuten: das sind 22,5 Stunden Bürozeit. Dazu kommen 20 Rechnungen à 30 Minuten (10 Stunden) und 10 Kundenanfragen pro Woche à 15 Minuten (2,5 Stunden pro Woche). Hochgerechnet auf ein Jahr: 22,5 Stunden × 12 Monate, plus 10 Stunden × 12 Monate, plus 2,5 Stunden × 52 Wochen – zusammen 520 Stunden pro Jahr.",
                    "Bei einem Verrechnungssatz von 65 Euro pro Stunde sind das 33.800 Euro pro Jahr – oder 65 volle Arbeitstage, die der Inhaber oder die Mitarbeiter im Büro statt auf der Baustelle verbringen. Das ist kein Einzelfall, sondern die typische Ausgangslage in Betrieben, in denen Angebote, Rechnungen und Termine manuell verwaltet werden.",
                ],
            },
            {
                "heading": "Die Faustregel: Wann lohnt es sich?",
                "paragraphs": [
                    "Als Richtwert gilt: Ein Prozess, der mindestens eine Stunde pro Woche manuell kostet, regelmäßig läuft und stabile Regeln hat, ist ein ernsthafter Kandidat. Darunter übersteigt der Wartungsaufwand oft den Nutzen.",
                    "Die drei Prüffragen vor jedem Projekt: Wie oft läuft der Prozess? Wie viel Zeit kostet er konkret? Bleiben die Regeln in den nächsten zwei Jahren stabil? Drei Ja-Antworten rechtfertigen die Rechnung. In dem Beispiel oben ist die Antwort auf alle drei Fragen klar: Angebote und Rechnungen laufen wöchentlich, kosten Stunden und ändern ihre Struktur kaum.",
                    "Zur Einordnung der Kosten: Eine Automatisierung von Angebots- und Rechnungsprozessen ist ein überschaubares Projekt – kein mehrjähriges IT-Vorhaben. Wer den Nutzen von 33.800 Euro pro Jahr den einmaligen Umsetzungskosten gegenüberstellt, sieht meist eine Amortisation innerhalb weniger Monate. Selbst im konservativen Fall – etwa ein kleinerer Betrieb mit der Hälfte der Volumina – bleiben mehrere tausend Euro Jahreswert, die gegen die Kosten stehen.",
                ],
            },
            {
                "heading": "Die klassischen ROI-Fallen",
                "paragraphs": [
                    "Die häufigsten Fehler bei Automatisierungsprojekten:",
                ],
                "list": [
                    "Instabile Prozesse automatisieren: Wer einen chaotischen Ablauf digitalisiert, automatisiert das Chaos – Wartung frisst den Nutzen.",
                    "Wartung unterschätzen: Jede Systemänderung (neues CRM-Release, andere Schnittstelle) kostet Anpassungszeit. Ohne Budget dafür stirbt die Automatisierung langsam.",
                    "Schöne statt kritische Prozesse wählen: Ein „Nice-to-have“-Workflow, der selten läuft, liefert keine Rechtfertigung für die Infrastruktur.",
                    "Nur die Baukosten rechnen: Betrieb und Wartung über drei Jahre gehören in jede ROI-Betrachtung.",
                ],
            },
            {
                "heading": "Der pragmatische Rechenweg in fünf Schritten",
                "paragraphs": [
                    "Eine belastbare Entscheidung braucht keine perfekte Excel-Tabelle, aber fünf Zahlen:",
                ],
                "list": [
                    "Stunden pro Woche, die der Prozess heute manuell kostet.",
                    "Stundensatz des betroffenen Teams (intern oder extern).",
                    "Einmalige Kosten: Analyse plus Umsetzung.",
                    "Jährliche Betriebskosten: Wartung, Lizenzen, Infrastruktur.",
                    "Zusätzlicher Nutzen: Fehlerreduktion, Durchlaufzeit, Skalierung – bewusst konservativ schätzen.",
                ],
            },
            {
                "heading": "Lizenzmodelle im Blick: Cloud-Abo oder Self-Hosting",
                "paragraphs": [
                    "Ein oft übersehener Kostenpunkt ist das Plattformmodell. Cloud-Dienste rechnen häufig pro Ausführung ab: Wer viele Workflows laufen lässt, zahlt mit der Menge mit. Bei n8n etwa kostet der kleinste Cloud-Tarif rund 50 Euro im Monat und erlaubt 2.500 Ausführungen – ein Betrieb, der ein CRM stündlich synchronisiert oder täglich Belegdaten verarbeitet, erreicht diese Grenze in wenigen Tagen und rutscht in teurere Tarife.",
                    "Selbst gehostet (etwa n8n auf einem kleinen Server) fallen dagegen nur feste Infrastrukturkosten von 10 bis 20 Euro im Monat an – unabhängig von der Anzahl der Ausführungen. Für Betriebe mit vielen, häufig laufenden Workflows ist das über die Jahre deutlich günstiger und planbarer. Der Preis dafür ist Betriebsverantwortung: Updates, Backups und Monitoring müssen organisiert sein. Genau dafür gibt es Umsetzungspartner, die Infrastruktur und Workflows aufsetzen und betreiben – dann bleibt die Entscheidung eine reine Kostenfrage.",
                ],
            },
            {
                "heading": "E-Rechnung: Ein externer Treiber, der die Rechnung beschleunigt",
                "paragraphs": [
                    "Seit dem 1. Januar 2025 müssen alle Unternehmen in Deutschland elektronische Rechnungen von anderen Unternehmen empfangen können. Die Versandpflicht kommt gestaffelt: Ab 2027 für Betriebe mit mehr als 800.000 Euro Vorjahresumsatz, ab 2028 für alle B2B-Rechnungen. Die Formate sind XRechnung (für die öffentliche Hand) und ZUGFeRD ab Version 2.0 (PDF mit eingebetteten XML-Daten).",
                    "Für Betriebe, die Rechnungen heute noch manuell in Word oder als PDF-Anhang erstellen, ist das kein reines Verwaltungsthema mehr, sondern eine gesetzliche Anforderung mit Termin. Eine Rechnungsautomatisierung, die Belege erfasst, prüft und im richtigen Format erzeugt, erfüllt diese Pflicht nebenbei – und rechnet sich zusätzlich über die eingesparte Zeit. Der Dringlichkeitsfaktor macht aus einer Rechenaufgabe eine klare Priorität.",
                ],
            },
            {
                "heading": "Automatisieren, outsourcen oder lassen?",
                "paragraphs": [
                    "Nicht jede Automatisierung ist die richtige Antwort. Manchmal ist ein externer Dienstleister für einen Spezialprozess günstiger als ein eigener Workflow; manchmal ist der manuelle Prozess – gut dokumentiert – die wirtschaftlichste Option.",
                    "Die Entscheidung gehört auf Papier: Kosten, Nutzen und Risiko der drei Optionen gegenüberstellen. Genau diese Rechnung macht den Unterschied zwischen Automatisierung als Projekt und Automatisierung als wertschöpfender Prozess. Wichtig ist der ehrliche Umgang mit Zahlen: Eine ROI-Schätzung auf Basis konservativer Annahmen ist belastbar; eine auf Basis von Wunschdenken führt zu Enttäuschung. Skalantech beziffert den Nutzen vor dem Start gemeinsam mit Ihren echten Zahlen – anpassbar, ohne Garantie, aber nachvollziehbar.",
                ],
            },
        ],
        "related_service": "ki-automatisierung",
        "cta_text": "KI-Potenzial in Ihren Prozessen prüfen",
        "next_step": {
            "kind": "potenzial",
            "label": "Potenzial-Check starten",
            "target": "rechner",
            "hint": "Rechnen Sie den ROI mit Ihren eigenen Zahlen durch – ohne Anmeldung.",
        },
        "published": "2026-08-28",
    },
}

ARTICLE_ORDER = [
    "was-ist-ein-ki-agent",
    "n8n-selbst-hosten",
    "lokale-ki-vs-cloud-ki",
    "n8n-vs-power-automate",
    "welche-prozesse-ki-automatisierung",
    "rag-wissensassistenten",
    "kosten-roi-ki-automatisierung",
]

# Publikationsdatum (Fallback; Artikel können eigenes "published" tragen)
ARTICLE_PUBLISHED = "2026-08-16"

# ── 5 Content-Säulen für /wissen (Issue #16) ────────────────────────────
# Anzeige-Reihenfolge = Reihenfolge in PILLARS. Technik steht bewusst an
# letzter Stelle: Der Einstieg läuft über Nutzen (Praxis, Branche, Datenschutz,
# Kosten), Technik ist für alle, die tiefer einsteigen wollen.
# Jeder Artikel trägt ein eigenes "next_step" (Demo / Prozess- / Branchenseite
# / Potenzial-Check); Säulen-Karten ("cards") ergänzen dort, wo keine Artikel
# liegen (Branchen) oder ein direkter Tool-Einstieg sinnvoll ist.
PILLARS = [
    {
        "id": "praxis-prozesse",
        "num": "01",
        "title": "Praxis & Prozesse",
        "tagline": "Welche Abläufe sich lohnen – und wie der Einstieg gelingt.",
        "articles": ["welche-prozesse-ki-automatisierung", "rag-wissensassistenten"],
        "cards": [
            {
                "kind": "prozess",
                "title": "Automationen im Überblick",
                "text": "Wiederkehrende Muster, die sich fast immer lohnen – mit Beispielen aus Handwerk, Kfz, Kanzlei und Immobilien.",
                "label": "Prozessseite ansehen",
                "target": "automationen",
            },
        ],
    },
    {
        "id": "branchen",
        "num": "02",
        "title": "Branchen",
        "tagline": "Was Automatisierung für Ihre Branche konkret bedeutet – mit Branchendaten und passenden Prozessen.",
        "articles": [],
        "branches": ["handwerk", "kfz", "kanzleien", "immobilien"],
    },
    {
        "id": "datenschutz-kontrolle",
        "num": "03",
        "title": "Datenschutz & Kontrolle",
        "tagline": "Wo Ihre Daten bleiben und wie Sie die Kontrolle über Systeme, Kosten und Abhängigkeiten behalten.",
        "articles": ["lokale-ki-vs-cloud-ki", "n8n-selbst-hosten"],
        "cards": [],
    },
    {
        "id": "kosten-entscheidung",
        "num": "04",
        "title": "Kosten & Entscheidung",
        "tagline": "Ehrliche Zahlen statt Hype – damit die Entscheidung auf Fakten basiert.",
        "articles": ["kosten-roi-ki-automatisierung", "n8n-vs-power-automate"],
        "cards": [
            {
                "kind": "potenzial",
                "title": "Potenzial-Check",
                "text": "Rechnen Sie in 30 Sekunden aus, was ein wiederkehrender Prozess Ihr Unternehmen pro Jahr kostet.",
                "label": "Potenzial-Check starten",
                "target": "rechner",
            },
        ],
    },
    {
        "id": "technik-erklaert",
        "num": "05",
        "title": "Technik erklärt",
        "tagline": "Wie die Technik funktioniert – für alle, die tiefer einsteigen wollen.",
        "articles": ["was-ist-ein-ki-agent"],
        "cards": [],
    },
]
