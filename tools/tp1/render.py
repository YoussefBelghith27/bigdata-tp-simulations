"""Rendu des écrans HTML en PNG 1242x1060 (Playwright + Chrome), avec la boîte de la cible."""
import base64, pathlib
from playwright.sync_api import sync_playwright

W, H = 1242, 1060
F = pathlib.Path("/home/claude/tp1/fonts")

def _b64(p):
    return base64.b64encode((F / p).read_bytes()).decode()

FONTS = f"""
@font-face{{font-family:UI;font-weight:400;src:url(data:font/woff2;base64,{_b64('noto-sans-latin-400-normal.woff2')})}}
@font-face{{font-family:UI;font-weight:600;src:url(data:font/woff2;base64,{_b64('noto-sans-latin-600-normal.woff2')})}}
@font-face{{font-family:UI;font-weight:700;src:url(data:font/woff2;base64,{_b64('noto-sans-latin-700-normal.woff2')})}}
@font-face{{font-family:MONO;src:url(data:font/ttf;base64,{_b64('CascadiaMono.ttf')})}}
"""

class Renderer:
    def __enter__(self):
        self.p = sync_playwright().start()
        self.b = self.p.chromium.launch(executable_path="/usr/bin/google-chrome")
        self.pg = self.b.new_page(viewport={"width": W, "height": H})
        return self

    def __exit__(self, *a):
        self.b.close(); self.p.stop()

    def render(self, body, css="", out=None):
        html = f"<!doctype html><html><head><meta charset=utf-8><style>{FONTS}{css}</style></head><body>{body}</body></html>"
        self.pg.set_content(html)
        self.pg.evaluate("document.fonts.ready")
        self.pg.wait_for_timeout(60)
        box = self.pg.evaluate("""() => { const e = document.querySelector('[data-t]'); if (!e) return null;
            const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)]; }""")
        png = self.pg.screenshot(clip={"x": 0, "y": 0, "width": W, "height": H})
        if out:
            pathlib.Path(out).write_bytes(png)
        return png, box

    def measure(self, css, text):
        self.pg.set_content(f"<style>{FONTS}{css}</style><span id=a>{text}</span>")
        self.pg.evaluate("document.fonts.ready"); self.pg.wait_for_timeout(60)
        return self.pg.evaluate("document.getElementById('a').getBoundingClientRect().width")
