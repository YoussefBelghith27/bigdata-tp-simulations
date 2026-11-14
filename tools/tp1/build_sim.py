"""Rend toutes les diapositives et écrit sims/<id>.js (format du lecteur WAN) + PNG pour l'approj et le CR."""
import json, base64, io, pathlib, sys
from PIL import Image
from render import Renderer
from screens import CSS
import importlib
story = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "story")
SIM_ID = sys.argv[2] if len(sys.argv) > 2 else "tp1-installation"
OUT = pathlib.Path(sys.argv[3] if len(sys.argv) > 3 else "/home/claude/tp1/build"); (OUT / "png").mkdir(parents=True, exist_ok=True); (OUT / "cap").mkdir(exist_ok=True)

slides_out, images, keymap, meta, caps = [], [], {}, [], []
with Renderer() as r:
    for k, s in enumerate(story.slides):
        png, box = r.render(s["html"], CSS)
        p = OUT / "png" / f"s{k:03d}.png"; p.write_bytes(png)
        if s.get("cap"):
            pending = (s["cap"], k + 1 if s["kind"] == "type" else k)
            caps.append(pending)
        h = hash(png)
        if h not in keymap:
            im = Image.open(io.BytesIO(png)).convert("RGB"); buf = io.BytesIO(); im.save(buf, "WEBP", quality=82, method=6)
            keymap[h] = len(images); images.append("data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode())
        sl = {"img": keymap[h], "step": s["step"], "text": s["text"], "kind": s["kind"]}
        if s["kind"] == "show":
            sl["dur"] = s["dur"]
        elif s["kind"] == "click":
            assert box, f"slide {k} sans cible"; sl["box"] = box; sl["hint"] = s["hint"]
        else:
            sl["answers"] = s["answers"]
            if s.get("box"):
                assert box, f"slide {k} sans champ"; sl["box"] = box
            else:
                sl["x"] = s["x"]
        slides_out.append(sl)
        meta.append({**{k2: v for k2, v in sl.items()}, "png": str(p)})
        print(k, s["kind"], box, s["text"][:60], file=sys.stderr)

import shutil
for name, idx in caps:
    shutil.copy(OUT / "png" / f"s{idx:03d}.png", OUT / "cap" / f"{name}.png")
data = {"id": SIM_ID, "w": 1242, "h": 1060, "images": images, "slides": slides_out}
pathlib.Path(OUT / f"{SIM_ID}.js").write_text("window.SIM_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
json.dump(meta, open(OUT / "slides_meta.json", "w"), ensure_ascii=False, indent=1)
st = {"slides": len(slides_out), "commands": sum(1 for s in slides_out if s["kind"] == "type"), "clicks": sum(1 for s in slides_out if s["kind"] == "click"),
      "size_kb": round(len(json.dumps(data)) / 1024)}
json.dump(st, open(OUT / "stats.json", "w"))
print(st)
