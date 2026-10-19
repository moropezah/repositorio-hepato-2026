#!/usr/bin/env python3
"""Inserta en index.html la Consulta rápida (Módulo 02) y los datos del Vademécum (Módulo 03).

Fuentes:
  fuentes/rapida/rapida.html        -> entre <!-- RAPIDA:INICIO --> y <!-- RAPIDA:FIN -->
  fuentes/vademecum/farmacos.json   -> entre <!-- VADEMECUM:DATOS:INICIO --> y <!-- VADEMECUM:DATOS:FIN -->

Uso: python3 fuentes/repositorio/actualizar.py
"""
import json, pathlib, re, sys

RAIZ = pathlib.Path(__file__).resolve().parents[2]
INDEX = RAIZ / "index.html"


def reemplazar(texto, marca, contenido):
    ini, fin = f"<!-- {marca}:INICIO -->", f"<!-- {marca}:FIN -->"
    patron = re.compile(re.escape(ini) + r".*?" + re.escape(fin), re.S)
    if not patron.search(texto):
        sys.exit(f"No encuentro las marcas {marca} en index.html")
    return patron.sub(lambda _: f"{ini}\n{contenido}\n{fin}", texto, count=1)


def main():
    html = INDEX.read_text(encoding="utf-8")

    rapida = (RAIZ / "fuentes/rapida/rapida.html").read_text(encoding="utf-8").strip()
    html = reemplazar(html, "RAPIDA", rapida)

    datos = json.loads((RAIZ / "fuentes/vademecum/farmacos.json").read_text(encoding="utf-8"))
    grupos = {g[0] for g in datos["grupos"]}
    cobs = set(datos["cobertura"])
    ids = set()
    for f in datos["farmacos"]:
        assert f["g"] in grupos, f"{f['id']}: grupo desconocido {f['g']}"
        assert f["id"] not in ids, f"id repetido {f['id']}"
        ids.add(f["id"])
        for c in f["cob"]:
            assert c in cobs, f"{f['id']}: cobertura desconocida {c}"
    js = json.dumps(datos, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = reemplazar(html, "VADEMECUM:DATOS",
                      f'<script type="application/json" id="vad-data">{js}</script>')

    INDEX.write_text(html, encoding="utf-8")
    n_r = rapida.count('<details class="ac"')
    print(f"index.html: consulta rápida {n_r} tarjetas · vademécum {len(datos['farmacos'])} fármacos en {len(grupos)} grupos")


if __name__ == "__main__":
    main()
