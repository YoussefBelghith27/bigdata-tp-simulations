"""Composants HTML des écrans reconstitués (Windows 11, navigateur, installateurs MSI, cmd, mongosh)."""
import html, re

E = html.escape
CW = 8.203125          # largeur d'un caractère Cascadia Mono 14px
COLS = 148
LH = 18
CON_TOP = 84
MAXL = (1060 - CON_TOP - 8) // LH

CSS = """
*{box-sizing:border-box}
body{margin:0;width:1242px;height:1060px;overflow:hidden;font-family:UI;font-size:13px;color:#1b1b1b;position:relative}
/* ---------- console ---------- */
.ct{position:absolute;inset:0 0 auto 0;height:84px;background:#202020}
.ct .tab{position:absolute;left:8px;top:50px;height:34px;width:300px;background:#0c0c0c;border-radius:8px 8px 0 0;color:#fff;
  display:flex;align-items:center;gap:10px;padding:0 12px;font-size:12.5px}
.ct .tab i{font-style:normal;font:11px MONO;background:#2b2b2b;border:1px solid #555;border-radius:3px;padding:0 3px;color:#ddd}
.ct .tab b{margin-left:auto;font-weight:400;color:#aaa}
.ct .plus{position:absolute;left:318px;top:56px;color:#ccc;font-size:18px}
.ct .wc{position:absolute;right:0;top:0;display:flex;color:#ddd;font-size:14px}.ct .wc span{width:46px;height:32px;display:grid;place-items:center}
.cb{position:absolute;left:0;right:0;top:84px;bottom:0;background:#0c0c0c}
.cl{position:absolute;left:8px;right:8px;bottom:3px;font:14px/18px MONO;color:#cccccc;white-space:pre}
.cur{display:inline-block;width:8px;height:15px;background:#cccccc;vertical-align:-2px}
.g{color:#16c60c}.y{color:#f9f1a5}.c{color:#61d6d6}.m{color:#b4009e}.k{color:#767676}.rd{color:#e74856}.w{color:#f2f2f2}.bl{color:#3b78ff}
/* ---------- bureau ---------- */
.desk{position:absolute;inset:0;background:
  radial-gradient(ellipse 60% 55% at 62% 58%, #7fb6ee 0%, rgba(127,182,238,0) 70%),
  radial-gradient(ellipse 50% 60% at 30% 70%, #3c7fd6 0%, rgba(60,127,214,0) 70%),
  linear-gradient(160deg,#cfe3f7 0%,#8fbbe9 40%,#2f6fc4 100%)}
.task{position:absolute;left:0;right:0;bottom:0;height:48px;background:rgba(238,242,247,.94);border-top:1px solid #d6dbe2;
  display:flex;justify-content:center;align-items:center;gap:6px}
.task .ic{width:40px;height:40px;border-radius:5px;display:grid;place-items:center}
.task .ic.on{background:rgba(255,255,255,.75);box-shadow:inset 0 0 0 1px #e1e5ea}
.task .clock{position:absolute;right:14px;top:6px;text-align:right;font-size:12px;line-height:17px}
.win{position:absolute;background:#fff;border:1px solid #9aa5b1;border-radius:8px;box-shadow:0 10px 40px rgba(0,0,0,.35);overflow:hidden}
.tb{height:32px;display:flex;align-items:center;padding-left:12px;gap:8px;font-size:12px;background:#f3f3f3}
.tb .wc{margin-left:auto;display:flex}.tb .wc span{width:46px;height:32px;display:grid;place-items:center;font-size:13px;color:#333}
.btn{display:inline-flex;align-items:center;justify-content:center;min-width:88px;height:28px;padding:0 12px;border:1px solid #c9c9c9;
  border-bottom-color:#a9a9a9;border-radius:4px;background:#fdfdfd;font-size:13px;color:#1b1b1b}
.btn.pri{background:#005fb8;color:#fff;border-color:#004e98}
.btn.dis{color:#a0a0a0;background:#f5f5f5;border-color:#e0e0e0}
.dim{position:absolute;inset:0;background:rgba(0,0,0,.45)}
/* ---------- MSI classique ---------- */
.msi{position:absolute;width:496px;height:390px;background:#f0f0f0;border:1px solid #7a7a7a;box-shadow:0 8px 30px rgba(0,0,0,.4);zoom:1.5;font-size:11px}
.msi .t{height:30px;background:#fff;display:flex;align-items:center;padding-left:8px;gap:6px;font-size:11.5px;border-bottom:1px solid #ddd}
.msi .t .x{margin-left:auto;width:44px;text-align:center;font-size:13px}
.msi .bn{height:58px;background:#fff;border-bottom:1px solid #a0a0a0;padding:9px 16px;position:relative}
.msi .bn h3{margin:0 0 4px;font-size:12px}.msi .bn p{margin:0 0 0 12px;font-size:11px}
.msi .bn .logo{position:absolute;right:12px;top:8px;width:40px;height:40px}
.msi .bot{position:absolute;left:0;right:0;bottom:0;height:48px;border-top:1px solid #a0a0a0;display:flex;gap:6px;justify-content:flex-end;align-items:center;padding-right:10px}
.msi .b{min-width:75px;height:23px;border:1px solid #adadad;background:#e1e1e1;display:inline-flex;align-items:center;justify-content:center;font-size:11px;padding:0 8px}
.msi .b.def{border:1px solid #0078d7;box-shadow:inset 0 0 0 1px #0078d7}
.msi .b.dis{color:#a0a0a0;background:#ececec;border-color:#cfcfcf}
.msi .side{position:absolute;left:0;top:30px;width:164px;bottom:48px;background:linear-gradient(180deg,#00684a 0%,#13aa52 60%,#b8e6c9 100%)}
.msi .side svg{position:absolute;left:52px;top:70px}
.msi .wel{position:absolute;left:180px;top:48px;right:18px}
.msi .wel h2{font-size:15px;margin:0 0 16px;font-weight:700}
.msi .body{padding:14px 22px}
.chk{display:inline-block;width:13px;height:13px;border:1px solid #333;background:#fff;vertical-align:-2px;margin-right:6px;position:relative}
.chk.on::after{content:"";position:absolute;left:3px;top:0;width:4px;height:8px;border:solid #222;border-width:0 2px 2px 0;transform:rotate(45deg)}
.rad{display:inline-block;width:13px;height:13px;border:1px solid #333;border-radius:50%;background:#fff;vertical-align:-2px;margin-right:6px;position:relative}
.rad.on::after{content:"";position:absolute;left:3px;top:3px;width:5px;height:5px;border-radius:50%;background:#222}
.fld{display:inline-block;background:#fff;border:1px solid #7a7a7a;height:20px;line-height:18px;padding:0 4px;font-size:11px;vertical-align:middle}
.fld.dis{background:#f0f0f0;border-color:#c0c0c0;color:#888}
/* ---------- navigateur ---------- */
.br .tabs{height:38px;background:#e9edf2;display:flex;align-items:flex-end;padding-left:8px;gap:2px}
.br .tabs .tab{height:32px;width:280px;white-space:nowrap;overflow:hidden;background:#fff;border-radius:8px 8px 0 0;display:flex;align-items:center;gap:8px;padding:0 10px;font-size:12px}
.br .tabs .tab.off{background:transparent;color:#555}
.br .tabs .wc{margin-left:auto;display:flex;align-self:flex-start}.br .tabs .wc span{width:46px;height:32px;display:grid;place-items:center}
.br .nav{height:42px;display:flex;align-items:center;gap:12px;padding:0 10px;border-bottom:1px solid #e3e3e3;font-size:16px;color:#444}
.br .url{flex:1;height:30px;border-radius:15px;background:#f1f3f4;display:flex;align-items:center;padding:0 14px;font-size:13.5px;color:#202124;gap:8px}
.br .url.focus{background:#fff;box-shadow:inset 0 0 0 2px #0b57d0}
.br .pg{position:absolute;left:0;right:0;top:80px;bottom:0;overflow:hidden}
/* ---------- page de téléchargement ---------- */
.mhead{height:54px;background:#001e2b;color:#fff;display:flex;align-items:center;gap:28px;padding:0 28px;font-size:13px}
.mhead .brand{font-weight:600;font-size:16px;color:#fff}
.mhero{background:#001e2b;color:#fff;padding:26px 28px 30px;display:flex;gap:30px}
.mhero h1{font-size:28px;margin:0 0 10px;font-weight:700}.mhero p{margin:0;color:#c1ccd6;font-size:13.5px;line-height:1.5;max-width:470px}
.card{background:#fff;color:#1c2d38;border-radius:10px;padding:18px 20px;width:410px;flex:none;box-shadow:0 4px 18px rgba(0,0,0,.3)}
.card label{display:block;font-size:12px;font-weight:600;margin:10px 0 4px;color:#3d4f58}
.sel{height:36px;border:1px solid #889397;border-radius:6px;display:flex;align-items:center;padding:0 12px;font-size:13.5px;position:relative;background:#fff}
.sel::after{content:"";position:absolute;right:14px;top:13px;width:7px;height:7px;border:solid #3d4f58;border-width:0 2px 2px 0;transform:rotate(45deg)}
.sel .badge{margin-left:8px;background:#e3fcf7;color:#00684a;border:1px solid #c0fae6;border-radius:10px;font-size:11px;padding:0 7px}
.dl{margin-top:16px;display:flex;gap:10px}
.dlb{height:38px;padding:0 20px;border-radius:6px;background:#00ed64;color:#001e2b;font-weight:700;display:inline-flex;align-items:center;font-size:14px;border:1px solid #00a35c}
.dll{height:38px;padding:0 16px;border-radius:6px;border:1px solid #889397;display:inline-flex;align-items:center;font-size:13px}
.menu{position:absolute;background:#fff;border:1px solid #c1c7c6;border-radius:6px;box-shadow:0 6px 18px rgba(0,0,0,.2);padding:4px 0;font-size:13.5px;color:#1c2d38;z-index:3}
.menu div{padding:7px 14px}.menu .hv{background:#e3fcf7}
.mbody{padding:24px 28px;color:#3d4f58;font-size:13px;line-height:1.6}
.flyout{position:absolute;right:60px;top:84px;width:360px;background:#fff;border-radius:8px;box-shadow:0 8px 28px rgba(0,0,0,.28);border:1px solid #ddd;padding:12px 14px;font-size:12.5px;z-index:4}
/* ---------- explorateur ---------- */
.ex .cmd{height:44px;display:flex;align-items:center;gap:16px;padding:0 14px;font-size:12.5px;border-bottom:1px solid #e5e5e5;color:#333}
.ex .ab{height:40px;display:flex;align-items:center;gap:10px;padding:0 12px;border-bottom:1px solid #e5e5e5}
.ex .path{flex:1;height:30px;border:1px solid #d8d8d8;border-radius:4px;display:flex;align-items:center;padding:0 10px;font-size:13px;gap:6px;background:#fff}
.ex .path.sel{border-color:#0067c0;box-shadow:inset 0 0 0 1px #0067c0}
.ex .path .hl{background:#cce4f7}
.ex .srch{width:200px;height:30px;border:1px solid #d8d8d8;border-radius:4px;padding:0 10px;display:flex;align-items:center;color:#777;font-size:12.5px}
.ex .nav{position:absolute;left:0;top:116px;bottom:22px;width:190px;border-right:1px solid #eee;padding:8px 0;font-size:12.5px}
.ex .nav div{padding:5px 18px;display:flex;gap:8px;align-items:center}.ex .nav .on{background:#e8eef5}
.ex .list{position:absolute;left:191px;right:0;top:116px;bottom:22px;font-size:12.5px}
.ex .hdr,.ex .row{display:grid;grid-template-columns:1fr 150px 160px 90px;padding:0 14px;height:28px;align-items:center}
.ex .hdr{color:#555;border-bottom:1px solid #eee}
.ex .row.on{background:#cce8ff}
.ex .row span:last-child{text-align:right}
.ex .st{position:absolute;left:0;right:0;bottom:0;height:22px;font-size:11.5px;padding:3px 14px;color:#444}
/* ---------- boîtes Windows classiques ---------- */
.dlg{position:absolute;background:#f0f0f0;border:1px solid #888;box-shadow:0 10px 36px rgba(0,0,0,.35);font-size:12px}
.dlg .t{height:30px;background:#fff;display:flex;align-items:center;padding-left:10px;font-size:12px}
.dlg .t .x{margin-left:auto;width:44px;text-align:center}
.wb{min-width:84px;height:24px;border:1px solid #adadad;background:#e1e1e1;display:inline-flex;align-items:center;justify-content:center;font-size:12px;padding:0 10px}
.wb.def{border-color:#0078d7;box-shadow:inset 0 0 0 1px #0078d7}
.tabsw{display:flex;gap:0;padding:8px 8px 0;font-size:10.5px;white-space:nowrap}
.tabsw div{padding:4px 6px;border:1px solid #d9d9d9;border-bottom:none;background:#f0f0f0;margin-right:-1px}
.tabsw .on{background:#fff;position:relative;top:1px;border-color:#d9d9d9}
.pane{background:#fff;border:1px solid #d9d9d9;margin:0 8px;padding:12px 14px}
.grp{border:1px solid #dcdcdc;padding:10px 12px;margin:10px 0;position:relative}
.grp>b{position:absolute;top:-9px;left:8px;background:#fff;padding:0 4px;font-weight:400}
.tbl{background:#fff;border:1px solid #828790;font-size:12px;overflow:hidden}
.tbl .h,.tbl .r{display:grid;grid-template-columns:170px 1fr;height:22px;align-items:center;padding:0 6px;white-space:nowrap;overflow:hidden}
.tbl .h{border-bottom:1px solid #e5e5e5;color:#333}
.tbl .r.on{background:#0078d7;color:#fff}
.lst{background:#fff;border:1px solid #828790;font-size:12px}
.lst div{height:22px;line-height:22px;padding:0 6px;white-space:nowrap}
.lst .on{background:#cce8ff;outline:1px solid #99d1ff;outline-offset:-1px}
.lst .ed{background:#fff;outline:1px solid #0078d7;outline-offset:-1px}
.uac{position:absolute;left:371px;top:250px;width:500px;background:#fff;box-shadow:0 12px 50px rgba(0,0,0,.5);border:1px solid #666}
.uac .hd{background:#1f3d8c;color:#fff;padding:12px 18px;font-size:13px}
"""


# ------------------------------------------------------------------ console
TOK = re.compile(r"(?P<s>'[^']*')|(?P<oid>ObjectId|Long|ISODate)|(?P<n>(?<![\w.])-?\d+(\.\d+)?(?![\w]))|(?P<b>\btrue\b|\bfalse\b|\bnull\b)")

def color_mongo(line):
    out, pos = [], 0
    for m in TOK.finditer(line):
        out.append(E(line[pos:m.start()]))
        t = m.group(0)
        cls = "g" if m.group("s") else "c" if m.group("oid") else "y"
        out.append(f'<span class="{cls}">{E(t)}</span>')
        pos = m.end()
    out.append(E(line[pos:]))
    return "".join(out)

def wrap(text, first_offset=0):
    """Coupe une ligne logique en lignes physiques de COLS colonnes."""
    res, s, w = [], text, COLS - first_offset
    while len(s) > w:
        res.append(s[:w]); s = s[w:]; w = COLS
    res.append(s)
    return res

class Console:
    """Historique d'une fenêtre console ; chaque entrée = (texte html, nb de lignes physiques)."""
    def __init__(self, title, prompt):
        self.title, self.prompt, self.lines = title, prompt, []

    def add_raw(self, html_line):
        self.lines.append(html_line)

    def add_cmd(self, prompt, cmd):
        phys = wrap(prompt + cmd)
        first = E(phys[0][:len(prompt)]) + '<span class="w">' + E(phys[0][len(prompt):]) + "</span>"
        self.lines.append(first)
        for p in phys[1:]:
            self.lines.append('<span class="w">' + E(p) + "</span>")

    def add_out(self, text, mongo=False):
        for logical in text.split("\n"):
            for p in wrap(logical):
                self.lines.append(color_mongo(p) if mongo else E(p))

    def clear(self):
        self.lines = []

    def html(self, prompt=None, cursor=True, typed=None):
        lines = list(self.lines)
        if prompt is not None:
            tail = E(prompt) + (f'<span class="w">{E(typed)}</span>' if typed else "") + ('<span class="cur"></span>' if cursor else "")
            lines.append(tail)
        lines = lines[-MAXL:]
        admin = self.title.startswith("Administrateur")
        top = f"""<div class="ct"><div class="tab"><i>&gt;_</i>{E(self.title)}<b>✕</b></div><div class="plus">+ &nbsp;⌄</div>
          <div class="wc"><span>—</span><span>☐</span><span>✕</span></div></div>"""
        return top + f'<div class="cb"><div class="cl">' + "\n".join(lines) + "</div></div>"

def prompt_x(prompt):
    return round(8 + len(prompt) * CW + 1, 1)


# ------------------------------------------------------------------ bureau
def taskbar(active=()):
    def ic(svg, key):
        return f'<div class="ic{" on" if key in active else ""}">{svg}</div>'
    start = '<svg width="22" height="22"><rect x="1" y="1" width="9" height="9" fill="#0a64d6"/><rect x="12" y="1" width="9" height="9" fill="#0a64d6"/><rect x="1" y="12" width="9" height="9" fill="#0a64d6"/><rect x="12" y="12" width="9" height="9" fill="#0a64d6"/></svg>'
    search = '<svg width="22" height="22"><circle cx="9" cy="9" r="6" fill="none" stroke="#333" stroke-width="2"/><path d="M14 14l6 6" stroke="#333" stroke-width="2"/></svg>'
    folder = '<svg width="24" height="22"><path d="M1 4h8l2 3h12v13H1z" fill="#f8c94a"/><path d="M1 8h22v12H1z" fill="#fcd96a"/></svg>'
    browser = '<svg width="24" height="24"><circle cx="12" cy="12" r="10" fill="#1d8ce0"/><path d="M5 14c2-6 12-7 14-1-3-2-8-2-9 2 0 2 2 4 6 3-5 3-11 1-11-4z" fill="#3fd18b"/></svg>'
    term = '<svg width="24" height="22"><rect x="1" y="2" width="22" height="18" rx="3" fill="#2b2b2b"/><path d="M5 8l4 3-4 3" stroke="#fff" stroke-width="1.6" fill="none"/><path d="M11 15h6" stroke="#fff" stroke-width="1.6"/></svg>'
    return f"""<div class="task">{ic(start,'start')}{ic(search,'search')}{ic(folder,'explorer')}{ic(browser,'browser')}{ic(term,'term')}
      <div class="clock">12:45<br>14/11/2026</div></div>"""

def desktop(inner, active=()):
    return f'<div class="desk"></div>{inner}{taskbar(active)}'


# ------------------------------------------------------------------ navigateur
def browser(url, title, page, focus=False, typed=None, x=40, y=96, w=1162, h=860, extra="", tgt_url=False):
    shown = typed if typed is not None else url
    t = ' data-t' if tgt_url else ''
    lock = '<svg width="12" height="14"><rect x="1" y="6" width="10" height="7" rx="1" fill="#555"/><path d="M3 6V4a3 3 0 016 0v2" stroke="#555" fill="none" stroke-width="1.5"/></svg>'
    return f"""<div class="win br" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">
      <div class="tabs"><div class="tab"><svg width="14" height="14"><circle cx="7" cy="7" r="6" fill="#00684a"/></svg>{E(title)}<span style="margin-left:auto">✕</span></div>
      <div class="tab off">+</div><div class="wc"><span>—</span><span>☐</span><span>✕</span></div></div>
      <div class="nav">←&nbsp; →&nbsp; ⟳ <div class="url{' focus' if focus else ''}"{t}>{lock if not focus else ''}<span>{E(shown)}</span>{'<span class="cur" style="background:#202124;width:1px;height:16px"></span>' if focus else ''}</div><span>☆</span><span>⋯</span></div>
      <div class="pg">{page}</div>{extra}</div>"""

def mdb_page(product, version_label, platform, package, open_menu=None, t=None, items=None):
    """Page de téléchargement reconstituée. t = 'version' | item index | 'download'."""
    def tg(k): return ' data-t' if t == k else ''
    PAGES = {
        "server": ("MongoDB Community Server Download", "La version Community de notre base de données distribuée. Elle offre un modèle de données orienté documents flexible, la prise en charge des requêtes ad hoc, l'indexation secondaire et l'agrégation en temps réel.", "MongoDB Community Server"),
        "shell": ("MongoDB Shell Download", "mongosh est un environnement JavaScript et Node.js entièrement fonctionnel pour interagir avec les déploiements MongoDB. Il permet de tester des requêtes et des opérations directement sur la base de données.", "MongoDB Shell"),
        "tools": ("MongoDB Command Line Database Tools Download", "Les Database Tools regroupent les utilitaires en ligne de commande pour travailler avec un déploiement MongoDB : mongoimport, mongoexport, mongodump, mongorestore, bsondump, mongostat, mongotop et mongofiles.", "MongoDB Database Tools"),
    }
    h1, desc, cardt = PAGES[product]
    fields = [("Version", version_label, "version"), ("Platform", platform, None), ("Package", package, None)]
    sels = ""
    for lab, val, key in fields:
        badge = '<span class="badge">current</span>' if (key == "version" and val.startswith("8.")) else ""
        sels += f'<label>{lab}</label><div class="sel"{tg(key) if key else ""}>{E(val)}{badge}</div>'
    menu = ""
    if open_menu is not None:
        rows = ""
        for k, it in enumerate(items):
            rows += f'<div class="{"hv" if open_menu == k else ""}"{tg(k)}>{E(it)}</div>'
        menu = f'<div class="menu" style="left:{1162-28-410+20}px;top:{54+26+18+22+28+4}px;width:370px">{rows}</div>'
    return f"""<div class="mhead"><span class="brand">mongodb.com</span><span style="color:#889397">|</span><span>Download Center</span><span>Products</span><span>Resources</span><span>Solutions</span><span>Company</span><span style="margin-left:auto">Sign In</span></div>
      <div class="mhero"><div><h1>{h1}</h1><p>{desc}</p></div>
      <div class="card"><div style="font-weight:700;font-size:15px">{cardt}</div>{sels}
      <div class="dl"><span class="dlb"{tg('download')}>Download</span><span class="dll">Copy link</span><span class="dll">More Options ⋯</span></div></div></div>
      <div class="mbody">{'<b>Archived releases</b> · Release notes · Changelog' if product=='server' else 'Documentation · Release notes'}</div>{menu}"""

def dl_flyout(fname, size, t=False):
    return f"""<div class="flyout"><div style="display:flex;justify-content:space-between;font-weight:600;margin-bottom:10px">Téléchargements<span style="font-weight:400">📁 ⋯ ✕</span></div>
      <div style="display:flex;gap:10px;align-items:center"><svg width="28" height="32"><path d="M2 1h17l7 7v23H2z" fill="#e9eef3" stroke="#8aa"/><text x="5" y="24" font-size="8" fill="#336">MSI</text></svg>
      <div><div style="font-weight:600">{E(fname)}</div><div style="color:#555">{size} · Terminé</div><div style="color:#0b57d0;margin-top:3px"{' data-t' if t else ''}>Ouvrir le fichier</div></div></div></div>"""


# ------------------------------------------------------------------ explorateur
def explorer(path_parts, rows, sel_row=None, t=None, path_sel=False, x=70, y=110, w=1100, h=760, nav_on="Ce PC", status=None):
    def tg(k): return ' data-t' if t == k else ''
    crumbs = ' <span style="color:#888">›</span> '.join(E(p) for p in path_parts)
    if path_sel:
        crumbs = '<span class="hl">' + E("\\".join(["C:"] + path_parts[2:]) if path_parts[1] == "Disque local (C:)" else "\\".join(path_parts)) + "</span>"
    r = ""
    for k, (name, date, typ, size, icon) in enumerate(rows):
        ico = {"dir": '<svg width="18" height="15"><path d="M1 2h6l2 2h8v10H1z" fill="#f8c94a"/></svg>',
               "exe": '<svg width="16" height="16"><rect x="1" y="2" width="14" height="12" rx="1" fill="#3a7bd5"/><rect x="1" y="2" width="14" height="3" fill="#1f5fb3"/></svg>',
               "dll": '<svg width="16" height="16"><path d="M3 1h7l3 3v11H3z" fill="#eee" stroke="#999"/><circle cx="8" cy="10" r="2.5" fill="#888"/></svg>',
               "msi": '<svg width="16" height="16"><path d="M3 1h7l3 3v11H3z" fill="#e9eef3" stroke="#8aa"/><rect x="5" y="8" width="6" height="4" fill="#3a7bd5"/></svg>',
               "txt": '<svg width="16" height="16"><path d="M3 1h7l3 3v11H3z" fill="#fff" stroke="#999"/><path d="M5 7h6M5 9h6M5 11h4" stroke="#999"/></svg>'}[icon]
        r += f'<div class="row{" on" if k == sel_row else ""}"{tg(k)}><span style="display:flex;gap:8px;align-items:center">{ico}{E(name)}</span><span>{E(date)}</span><span>{E(typ)}</span><span>{E(size)}</span></div>'
    navs = ["Accueil", "Galerie", "Bureau", "Téléchargements", "Documents", "Images", "Ce PC", "Réseau"]
    nav = "".join(f'<div class="{"on" if n == nav_on else ""}">{"🖥" if n=="Ce PC" else "📁"} {E(n)}</div>' for n in navs)
    title = path_parts[-1]
    return f"""<div class="win ex" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">
      <div class="tb" style="background:#eef2f6">📁 {E(title)}<div class="wc"><span>—</span><span>☐</span><span>✕</span></div></div>
      <div class="ab">← → ↑ ⟳<div class="path{' sel' if path_sel else ''}"{tg('path')}>{crumbs}</div><div class="srch">Rechercher dans : {E(title)}</div></div>
      <div class="cmd">⊕ Nouveau ⌄ &nbsp; ✂ &nbsp; ⧉ &nbsp; 📋 &nbsp; 🗑 &nbsp; ⇅ Trier ⌄ &nbsp; ☰ Afficher ⌄ &nbsp; ⋯</div>
      <div class="nav">{nav}</div>
      <div class="list"><div class="hdr"><span>Nom</span><span>Modifié le</span><span>Type</span><span style="text-align:right">Taille</span></div>{r}</div>
      <div class="st">{E(status or f"{len(rows)} élément(s)")}</div></div>"""


# ------------------------------------------------------------------ MSI
LEAF = '<svg width="64" height="90" viewBox="0 0 64 90"><ellipse cx="32" cy="12" rx="28" ry="10" fill="#fff"/><path d="M4 12v62c0 6 12 10 28 10s28-4 28-10V12c0 6-12 10-28 10S4 18 4 12z" fill="#fff" opacity=".85"/><path d="M4 33c0 6 12 10 28 10s28-4 28-10M4 54c0 6 12 10 28 10s28-4 28-10" stroke="#13aa52" stroke-width="2" fill="none"/></svg>'

def msi(title, page, buttons, t=None, x=None, y=None):
    """page = html interne ; buttons = liste (label, state) state in '', 'def', 'dis'; t = label cible."""
    x = (1242 - 744) // 2 if x is None else x
    y = 150 if y is None else y
    b = ""
    for lab, st in buttons:
        if lab == "|":
            b += '<span style="width:10px"></span>'; continue
        b += f'<span class="b {st}"{" data-t" if t == lab else ""}>{E(lab)}</span>'
    return f"""<div class="msi" style="left:{x/1.5}px;top:{y/1.5}px"><div class="t">
      <svg width="14" height="14"><rect x="1" y="1" width="12" height="12" fill="#3a7bd5"/></svg>{E(title)}<span class="x">✕</span></div>
      {page}<div class="bot">{b}</div></div>"""

def msi_banner(h3, p, inner):
    return f'<div class="bn"><h3>{E(h3)}</h3><p>{E(p)}</p><svg class="logo" viewBox="0 0 40 40"><rect width="40" height="40" fill="#13aa52" rx="4"/><ellipse cx="20" cy="11" rx="11" ry="4" fill="#fff"/><path d="M9 11v18c0 2 5 4 11 4s11-2 11-4V11c0 2-5 4-11 4S9 13 9 11z" fill="#fff" opacity=".85"/></svg></div><div class="body">{inner}</div>'

def msi_side(h2, p):
    return f'<div class="side">{LEAF}</div><div class="wel"><h2>{E(h2)}</h2><p style="line-height:1.5">{p}</p></div>'


# ------------------------------------------------------------------ boîtes Windows
def uac(app, editor, t=None):
    return f"""<div class="dim"></div><div class="uac"><div class="hd">Contrôle de compte d'utilisateur<span style="float:right">✕</span></div>
      <div style="padding:18px 22px 6px;font-size:18px;line-height:1.35;color:#1b1b1b">Voulez-vous autoriser cette application à apporter des modifications à votre appareil ?</div>
      <div style="padding:10px 22px;display:flex;gap:12px;align-items:center"><svg width="34" height="34"><rect x="2" y="2" width="30" height="30" rx="4" fill="#3a7bd5"/></svg>
      <div style="font-size:14px;font-weight:600">{E(app)}</div></div>
      <div style="padding:4px 22px 12px;font-size:12.5px;line-height:1.7;color:#333">Éditeur vérifié : {E(editor)}<br>Origine du fichier : Disque dur sur cet ordinateur<br><span style="color:#0067c0">Afficher plus de détails</span></div>
      <div style="background:#f3f3f3;padding:14px 22px;display:flex;gap:10px"><span class="btn pri" style="flex:1;height:32px"{' data-t' if t=='Oui' else ''}>Oui</span><span class="btn" style="flex:1;height:32px">Non</span></div></div>"""

def run_dialog(typed="", t=None):
    return f"""<div class="dlg" style="left:14px;top:640px;width:420px;height:212px"><div class="t">Exécuter<span class="x">✕</span></div>
      <div style="padding:14px 16px;display:flex;gap:14px"><svg width="34" height="34"><rect x="2" y="5" width="30" height="24" rx="2" fill="#3a7bd5"/><rect x="5" y="9" width="24" height="16" fill="#dfeaf7"/></svg>
      <div style="line-height:1.45">Entrez le nom d'un programme, dossier, document ou ressource Internet, et Windows l'ouvrira pour vous.</div></div>
      <div style="padding:0 16px;display:flex;align-items:center;gap:10px">Ouvrir :<div style="flex:1;height:24px;background:#fff;border:1px solid #7a7a7a;padding:0 5px;line-height:22px;font-size:13px"{' data-t' if t=='field' else ''}>{E(typed)}</div></div>
      <div style="position:absolute;right:14px;bottom:14px;display:flex;gap:8px"><span class="wb def"{' data-t' if t=='OK' else ''}>OK</span><span class="wb">Annuler</span><span class="wb">Parcourir...</span></div></div>"""

def sysprops(tab, t=None):
    tabs = ["Nom de l'ordinateur", "Matériel", "Paramètres système avancés", "Protection du système", "Utilisation à distance"]
    th = "".join(f'<div class="{"on" if x == tab else ""}"{" data-t" if t == x else ""}>{E(x)}</div>' for x in tabs)
    if tab == "Paramètres système avancés":
        body = f"""<div style="margin-bottom:8px">Vous devez ouvrir une session d'administrateur pour effectuer la plupart de ces modifications.</div>
          <div class="grp"><b>Performances</b>Effets visuels, planification du processeur, utilisation mémoire et mémoire virtuelle<div style="text-align:right;margin-top:8px"><span class="wb">Paramètres...</span></div></div>
          <div class="grp"><b>Profil des utilisateurs</b>Paramètres du Bureau liés à votre connexion<div style="text-align:right;margin-top:8px"><span class="wb">Paramètres...</span></div></div>
          <div class="grp"><b>Démarrage et récupération</b>Informations de démarrage du système, de défaillance du système et de débogage<div style="text-align:right;margin-top:8px"><span class="wb">Paramètres...</span></div></div>
          <div style="text-align:right;margin-top:10px"><span class="wb"{' data-t' if t=='env' else ''}>Variables d'environnement...</span></div>"""
    else:
        body = """<div style="display:flex;gap:12px;margin-bottom:14px"><svg width="40" height="34"><rect x="2" y="2" width="36" height="24" rx="2" fill="#3a7bd5"/><rect x="14" y="27" width="12" height="5" fill="#777"/></svg>
          <div>Windows utilise les informations suivantes pour identifier votre ordinateur sur le réseau.</div></div>
          <div style="line-height:2.1">Description de l'ordinateur : <span class="fld" style="width:240px"></span><br>Nom complet de l'ordinateur : <b style="font-weight:400">LAPTOP-ASUS</b><br>Groupe de travail : WORKGROUP</div>
          <div style="margin-top:14px">Pour renommer cet ordinateur ou changer de domaine ou de groupe de travail, cliquez sur Modifier.<div style="text-align:right;margin-top:8px"><span class="wb">Modifier...</span></div></div>
          <div style="height:84px"></div>"""
    return f"""<div class="dlg" style="left:330px;top:150px;width:470px;height:560px;zoom:1.25"><div class="t">Propriétés système<span class="x">✕</span></div>
      <div class="tabsw">{th}</div><div class="pane" style="height:440px">{body}</div>
      <div style="position:absolute;right:10px;bottom:10px;display:flex;gap:6px"><span class="wb">OK</span><span class="wb">Annuler</span><span class="wb" style="color:#999">Appliquer</span></div></div>"""

SYSVARS = [("ComSpec", r"C:\WINDOWS\system32\cmd.exe"), ("DriverData", r"C:\Windows\System32\Drivers\DriverData"),
           ("NUMBER_OF_PROCESSORS", "12"), ("OS", "Windows_NT"),
           ("Path", r"C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\System32\WindowsPowerShell\v1.0\;..."),
           ("PATHEXT", ".COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC"), ("PROCESSOR_ARCHITECTURE", "AMD64"),
           ("PSModulePath", r"%ProgramFiles%\WindowsPowerShell\Modules;C:\WINDOWS\system32\..."), ("TEMP", r"C:\WINDOWS\TEMP")]
USERVARS = [("OneDrive", r"C:\Users\ASUS\OneDrive"), ("Path", r"C:\Users\ASUS\AppData\Local\Microsoft\WindowsApps;"),
            ("TEMP", r"C:\Users\ASUS\AppData\Local\Temp"), ("TMP", r"C:\Users\ASUS\AppData\Local\Temp")]

def envvars(sel_path=False, t=None):
    def rows(lst, selectable):
        out = ""
        for k, (n, v) in enumerate(lst):
            on = selectable and sel_path and n == "Path"
            tg = ' data-t' if (selectable and t == "Path" and n == "Path") else ""
            out += f'<div class="r{" on" if on else ""}"{tg}><span>{E(n)}</span><span>{E(v)}</span></div>'
        return out
    return f"""<div class="dlg" style="left:250px;top:120px;width:600px;height:620px;zoom:1.2"><div class="t">Variables d'environnement<span class="x">✕</span></div>
      <div style="padding:10px 14px">Variables utilisateur pour ASUS
      <div class="tbl" style="height:150px;margin-top:6px"><div class="h"><span>Variable</span><span>Valeur</span></div>{rows(USERVARS, False)}</div>
      <div style="text-align:right;margin:8px 0 14px;display:flex;gap:6px;justify-content:flex-end"><span class="wb">Nouvelle...</span><span class="wb">Modifier...</span><span class="wb">Supprimer</span></div>
      Variables système
      <div class="tbl" style="height:200px;margin-top:6px"><div class="h"><span>Variable</span><span>Valeur</span></div>{rows(SYSVARS, True)}</div>
      <div style="text-align:right;margin:8px 0;display:flex;gap:6px;justify-content:flex-end"><span class="wb">Nouvelle...</span><span class="wb"{' data-t' if t=='Modifier' else ''}>Modifier...</span><span class="wb">Supprimer</span></div></div>
      <div style="position:absolute;right:14px;bottom:12px;display:flex;gap:6px"><span class="wb def"{' data-t' if t=='OK' else ''}>OK</span><span class="wb">Annuler</span></div></div>"""

PATH_BASE = [r"%SystemRoot%\system32", r"%SystemRoot%", r"%SystemRoot%\System32\Wbem", r"%SYSTEMROOT%\System32\WindowsPowerShell\v1.0\\".rstrip("\\") + "\\",
             r"%SYSTEMROOT%\System32\OpenSSH\\".rstrip("\\") + "\\", r"C:\Program Files\Git\cmd", r"C:\Program Files\nodejs\\".rstrip("\\") + "\\"]

def editpath(entries, sel=None, editing=None, typed="", t=None):
    rows = ""
    for k, e in enumerate(entries):
        if k == editing:
            rows += f'<div class="ed"{" data-t" if t=="field" else ""}>{E(typed)}<span class="cur" style="background:#000;width:1px;height:14px;vertical-align:-2px"></span></div>'
        else:
            rows += f'<div class="{"on" if k == sel else ""}">{E(e)}</div>'
    btns = ["Nouveau", "Modifier", "Parcourir...", "Supprimer", "|", "Monter", "Descendre", "|", "Modifier le texte..."]
    bh = ""
    for b in btns:
        if b == "|": bh += '<div style="height:16px"></div>'; continue
        bh += f'<div style="margin-bottom:6px"><span class="wb" style="width:130px"{" data-t" if t==b else ""}>{E(b)}</span></div>'
    return f"""<div class="dlg" style="left:250px;top:130px;width:560px;height:520px;zoom:1.25"><div class="t">Modifier la variable d'environnement<span class="x">✕</span></div>
      <div style="display:flex;gap:12px;padding:12px 14px"><div class="lst" style="flex:1;height:420px">{rows}</div><div>{bh}</div></div>
      <div style="position:absolute;right:14px;bottom:12px;display:flex;gap:6px"><span class="wb def"{' data-t' if t=='OK' else ''}>OK</span><span class="wb">Annuler</span></div></div>"""


# ------------------------------------------------------------------ carte de titre
def title_card(title, subtitle, items):
    li = "".join(f"<li>{E(i)}</li>" for i in items)
    return f"""<div style="position:absolute;inset:0;background:linear-gradient(150deg,#001e2b 0%,#023430 55%,#00684a 100%);color:#fff">
      <div style="position:absolute;left:90px;top:170px;right:90px">
      <div style="font:600 15px UI;letter-spacing:3px;color:#71f6ba">BIG DATA AVANCÉE · NoSQL · ISET NABEUL</div>
      <div style="font:700 52px/1.1 UI;margin:18px 0 14px">{E(title)}</div>
      <div style="font:400 21px UI;color:#c1ccd6;margin-bottom:46px">{E(subtitle)}</div>
      <ol style="font:400 18px/2 UI;color:#e8edeb;padding-left:24px;margin:0">{li}</ol></div>
      <div style="position:absolute;left:90px;bottom:70px;font:400 15px UI;color:#9fb4ae">Youssef Belghith · RSI3 · 2026–2027 &nbsp;·&nbsp; Windows 11 · MongoDB 7.0 · mongosh 2.x</div></div>"""
