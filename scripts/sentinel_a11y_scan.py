"""SENTINEL Accessibility-Scan: semantische Checks auf gerendertem HTML."""
import os, re, sys
from html.parser import HTMLParser

os.environ["SECRET_KEY"] = "test-secret"
os.environ["ADMIN_PASSWORD"] = "test-admin-password"
os.environ["SESSION_COOKIE_SECURE"] = "false"
os.environ["DATABASE_URL"] = "sqlite:////tmp/sentinel_smoke.db"
os.environ["RATELIMIT_STORAGE_URI"] = "memory://"
sys.path.insert(0, "/root/skalantech-hub")
from app import create_app

app = create_app("production")
app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
client = app.test_client()

class A11yParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.issues = []
        self.images = 0
        self.imgs_no_alt = []
        self.labels = []
        self.inputs = []
        self.h_counts = {f"h{i}": 0 for i in range(1, 7)}
        self.buttons = []
        self.links = 0
        self.current_label_for = None

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "img":
            self.images += 1
            if "alt" not in d:
                self.imgs_no_alt.append((tag, d.get("src", "?")))
        if tag == "label":
            self.labels.append(d.get("for"))
        if tag in ("input", "select", "textarea"):
            self.inputs.append((tag, d.get("id"), d.get("type"), d.get("aria-label"), d.get("name")))
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.h_counts[tag] += 1
        if tag == "button":
            self.buttons.append((d.get("aria-label"), d.get("type"), d.get("aria-expanded")))
        if tag == "a":
            self.links += 1

pages = ["/", "/impressum", "/datenschutz", "/agb", "/koeln", "/demos", "/automationen", "/websites-apps", "/it-infrastruktur"]

for path in pages:
    html = client.get(path).get_data(as_text=True)
    p = A11yParser()
    p.feed(html)
    print(f"=== {path} ===")
    print(f"  h1={p.h_counts['h1']} h2={p.h_counts['h2']} h3={p.h_counts['h3']} | img={p.images} no-alt={len(p.imgs_no_alt)} | links={p.links}")
    if p.h_counts["h1"] != 1:
        print(f"  ISSUE: {p.h_counts['h1']} h1-Elemente (erwartet 1)")
    if p.imgs_no_alt:
        print(f"  ISSUE: Bilder ohne alt: {p.imgs_no_alt}")
    # label-for deckt inputs ab
    ids_needing_label = [i[1] for i in p.inputs if i[1] and i[3] is None and i[2] not in ("hidden", "checkbox")]
    missing = [i for i in ids_needing_label if i not in p.labels and i not in (x for x in ids_needing_label)]
    missing_ids = [i for i in ids_needing_label if i not in p.labels]
    if missing_ids:
        print(f"  ISSUE: Inputs ohne label-for und ohne aria-label: {missing_ids}")
    # Buttons ohne aria-label, die nur Icons enthalten könnten (menu-toggle hat aria-label)
    for b in p.buttons:
        if not b[0] and b[1] != "submit" and b[1] != "button":
            pass
    # HTML lang
    if 'lang="de"' not in html:
        print("  ISSUE: html lang=de fehlt")
    # skip-link
    if path == "/" and "skip-link" not in html:
        print("  ISSUE: skip-link fehlt")

print("\n=== DETAILS/SUMMARY (FAQ) ===")
faq_html = client.get("/").get_data(as_text=True)
print("details-Tags:", faq_html.count("<details"), "| summary:", faq_html.count("<summary"))

print("\n=== FOCUS-MANAGE / ARIA-LIVE ===")
for needle in ["aria-live=\"polite\"", "aria-expanded", "role=\"status\""]:
    print(f"{needle}: {'OK' if needle in faq_html else 'MISS'}")
