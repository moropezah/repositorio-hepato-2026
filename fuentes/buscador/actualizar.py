#!/usr/bin/env python3
"""Genera buscador-indice.json (raíz del repositorio) para el buscador global.

Uso:  python3 fuentes/buscador/actualizar.py
Lo ejecutan solos fuentes/guia/actualizar.py y fuentes/repositorio/actualizar.py al terminar;
córrelo a mano solo si cambiaste calc/index.html.

Cada entrada: m (módulo: g guía · r consulta rápida · v vademécum · l líneas de tratamiento · c calculadoras),
t (título), s (contexto), k (palabras clave con más peso), x (texto plano), h (enlace relativo a la raíz).
"""
import html, json, pathlib, re

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent


def plano(frag):
    frag = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", frag, flags=re.S | re.I)
    frag = re.sub(r"<br\s*/?>|</(p|li|tr|td|th|dd|dt|div|h\d)>", " · ", frag, flags=re.I)
    t = html.unescape(re.sub(r"<[^>]+>", " ", frag))
    t = t.replace("Clic para ver", " ")
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"(\s·\s*)+", " · ", t)
    return t.strip(" ·")


def guia():
    doc = (RAIZ / "guia-2026.html").read_text(encoding="utf-8")
    ini = doc.find('<h2 id="b')
    fin = doc.find('<h2 id="fuentes"')
    cuerpo = doc[ini:fin]
    out = []
    # trozos por h2 (bloque) y h3 (sección)
    partes = re.split(r'(?=<h2 id="b|<h3\b)', cuerpo)
    bloque, bid = "", ""
    for p in partes:
        m2 = re.match(r'<h2 id="(b\d+)">(.*?)</h2>', p, re.S)
        if m2:
            bid = m2.group(1)
            num = re.search(r'<span class="num">(.*?)</span>', m2.group(2))
            tit = plano(re.sub(r'<span class="num">.*?</span>', "", m2.group(2)))
            bloque = (f"Bloque {plano(num.group(1))} · " if num else "") + tit
            resto = p[m2.end():]
            x = plano(resto)
            if x:
                out.append({"m": "g", "t": tit, "s": bloque.split(" · ")[0], "k": "", "x": x, "h": f"guia-2026.html#{bid}"})
            continue
        m3 = re.match(r'<h3 id="([^"]+)"[^>]*>(.*?)</h3>', p, re.S)
        if not m3:
            continue
        sid, tit = m3.group(1), plano(m3.group(2))
        cuerpo3 = p[m3.end():]
        claves = [plano(x) for x in re.findall(r'<div class="pt"><span>Perlas</span>(.*?)</div>', cuerpo3, re.S)]
        claves += [plano(x) for x in re.findall(r"<h4[^>]*>(.*?)</h4>", cuerpo3, re.S)]
        x = plano(cuerpo3)
        # las preguntas viven en JSON: se indexan sus enunciados
        qs = re.findall(r'<script type="application/json" class="qz-data"[^>]*>(.*?)</script>', cuerpo3, re.S)
        for q in qs:
            try:
                x += " " + " ".join(pr.get("p", "") for pr in json.loads(q))
            except Exception:
                pass
        out.append({"m": "g", "t": tit, "s": bloque, "k": " · ".join(c for c in claves if c), "x": x.strip(), "h": f"guia-2026.html#{sid}"})
    return out


def rapida():
    idx = (RAIZ / "index.html").read_text(encoding="utf-8")
    zona = idx[idx.find("<!-- RAPIDA:INICIO -->"):idx.find("<!-- RAPIDA:FIN -->")]
    out = []
    for m in re.finditer(r'<details class="ac" id="(r-\d+)"([^>]*)>\s*<summary>(.*?)</summary>(.*?)</details>', zona, re.S):
        k = re.search(r'data-k="([^"]*)"', m.group(2))
        out.append({"m": "r", "t": plano(m.group(3)), "s": "", "k": html.unescape(k.group(1)) if k else "",
                    "x": plano(m.group(4)), "h": f"index.html#rapida/{m.group(1)}"})
    return out


def vademecum():
    d = json.loads((RAIZ / "fuentes/vademecum/farmacos.json").read_text(encoding="utf-8"))
    G = dict((g[0], g[1]) for g in d["grupos"])
    C = d["cobertura"]
    out = []
    for f in d["farmacos"]:
        campos = [f.get(c, "") for c in ("cl", "ind", "lin", "dos", "aj", "resp", "mon", "ea", "ch", "ev")]
        campos += [" ".join(r) for r in f.get("plan", [])]
        out.append({"m": "v", "t": plano(f["n"]), "s": G.get(f["g"], ""),
                    "k": " · ".join(C[c][0] for c in f["cob"] if c in C),
                    "x": plano(" · ".join(campos)), "h": f"index.html#vademecum/f-{f['id']}"})
    for i, l in enumerate(d.get("lineas", [])):
        x = " · ".join(" ".join(r) for r in l["r"])
        out.append({"m": "l", "t": plano(l["e"]), "s": "Vademécum · líneas de tratamiento", "k": "",
                    "x": plano(x), "h": f"index.html#vademecum/l-{i}"})
    return out


def calculadoras():
    src = (RAIZ / "calc/index.html").read_text(encoding="utf-8")
    Q = r"""(?:'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)")"""
    meta = {}
    mi = src.find("const META={")
    if mi >= 0:
        bloque = src[mi:src.find("\n};", mi)]
        for m in re.finditer(r"\n(\w+):\{uso:'\w'(.*?)(?=\n\w+:\{uso:|\Z)", bloque, re.S):
            txt = " ".join((a or b).replace("\\'", "'") for a, b in re.findall(r"(?:que|cuando|ojo):" + Q, m.group(2)))
            meta[m.group(1)] = plano(txt)
    out = []
    for m in re.finditer(r"\{id:'(\w+)',g:" + Q + r",t:" + Q + r",d:" + Q, src):
        v = [(m.group(i) or m.group(i + 1) or "").replace("\\'", "'") for i in (2, 4, 6)]
        cid, (g, t, d) = m.group(1), v
        out.append({"m": "c", "t": plano(t), "s": "Calculadora · " + g, "k": "",
                    "x": plano(d + " · " + meta.get(cid, "")), "h": f"calc/#{cid}"})
    return out


def main():
    items = guia() + rapida() + vademecum() + calculadoras()
    for it in items:
        if not it["k"]:
            del it["k"]
        if not it["s"]:
            del it["s"]
    j = json.dumps(items, ensure_ascii=False, separators=(",", ":"))
    (RAIZ / "buscador-indice.json").write_text(j, encoding="utf-8")
    cuenta = {}
    for it in items:
        cuenta[it["m"]] = cuenta.get(it["m"], 0) + 1
    print(f"buscador-indice.json: {len(items)} entradas ({', '.join(f'{k} {v}' for k, v in cuenta.items())}), {len(j)//1024} KB")


if __name__ == "__main__":
    main()
