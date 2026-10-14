"""Check rendered pages, local downloads, links and disclosed prototype status."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"_site"
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key in {"href","src"} and value:self.links.append(value)
pages=list(SITE.rglob("*.html"));errors=[]
if len(list(SITE.glob("*.html")))<8 or len(list((SITE/"cases").glob("*.html")))!=6:errors.append("Expected eight main pages and six case pages")
for page in pages:
    text=page.read_text(encoding="utf-8")
    parser=Links();parser.feed(text)
    for link in parser.links:
        parsed=urlparse(link)
        if parsed.scheme or not parsed.path:continue
        candidate=(SITE/parsed.path.lstrip("/") if parsed.path.startswith("/") else page.parent/unquote(parsed.path)).resolve()
        if not candidate.is_relative_to(SITE.resolve()) or not candidate.exists():errors.append(f"{page.relative_to(SITE)}: missing local target {link}")
    if "Traceback (most recent call last)" in text:errors.append("Execution traceback in "+str(page))
if "Public-source discussion prototype" not in (SITE/"index.html").read_text(encoding="utf-8"):errors.append("Prototype status missing from front page")
if errors:raise SystemExit("\n".join(errors[:30]))
print(f"Rendered site validated: {len(pages)} HTML pages; local links and downloads resolve")
