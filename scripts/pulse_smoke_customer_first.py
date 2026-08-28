import sys
sys.path.insert(0, '.')
from app import create_app

app = create_app()
c = app.test_client()
html = c.get('/').get_data(as_text=True)
hidden_service = html.split('name="service" value="', 1)[1].split('"', 1)[0] if 'name="service" value="' in html else ''
checks = {
    'header-cta class': 'class="header-cta"' in html,
    'Potenzial-Check buchen (header)': 'Potenzial-Check buchen' in html,
    'hero CTA #termin': 'href="#termin"' in html,
    'footer data-track demo_started': 'data-track="demo_started" data-track-label="footer"' in html,
    'service hidden mapped (C15)': hidden_service in ('Business-Analyse', 'Potenzial-Check'),
    'demo_clicked hero': 'data-track="demo_clicked" data-track-label="hero"' in html,
    'demo_clicked invoiceflow': 'data-track="demo_clicked" data-track-label="invoiceflow"' in html,
    'roi widget': 'data-roi-rechner' in html and 'data-source="homepage"' in html,
    'analytics.js v19': 'js/analytics.js?v=19' in html,
    'id=rechner': 'id="rechner"' in html,
    'id=branchen': 'id="branchen"' in html,
    'id=termin': 'id="termin"' in html,
}
failed = False
for k, v in checks.items():
    print(('PASS' if v else 'FAIL'), k)
    if not v:
        failed = True
if failed:
    print('SOME CHECKS FAILED')
    sys.exit(1)
print('ALL SMOKE CHECKS PASS')
