#!/usr/bin/env python3
"""Dibuja las láminas del bloque 0 (histología hepática) y las inserta en bloques/b00_histologia.html.

Uso (desde la raíz del repositorio):
    python3 fuentes/guia/figuras/histologia.py
    python3 fuentes/guia/actualizar.py

Cada lámina va entre marcas <!--FIG:nombre--> y <!--/FIG:nombre--> en el bloque; el texto
del bloque se edita a mano y este script solo reemplaza lo que hay entre las marcas.
Los esquemas son originales y deterministas (semillas fijas): regenerarlos no cambia el dibujo.
Colores del H&E fijos; los esquemas usan las variables --h-* de extra.css.
"""
import math, random, re, pathlib
AQUI = pathlib.Path(__file__).resolve().parent


# Paleta H&E fija (lámina de vidrio: no cambia con el tema)
SLIDE = "#fbf3f5"; CELL = "#efb3c3"; CELLS = "#cf8ca1"; NUC = "#4f3c86"
STROMA = "#f5d8e1"; STROMAS = "#d7a0b1"; FIB = "#e6b6c4"; LYM = "#2b2160"
RBC = "#cf4a43"; PLASMA = "#9b86c6"; ACID = "#e66f8d"; LBL = "#3a2a4e"
PLATE = "#b0561c"

def f(v): return f"{v:.1f}".rstrip("0").rstrip(".")

def hexpoly(cx, cy, r, rot):
    return " ".join(f"{f(cx + r*math.cos(rot + k*math.pi/3))},{f(cy + r*math.sin(rot + k*math.pi/3))}" for k in range(6))

def cell(cx, cy, r, rnd, stroke=CELLS, sw=0.8, nuc=True, extra=""):
    rot = rnd.random()*math.pi
    s = f'<polygon points="{hexpoly(cx, cy, r, rot)}" fill="{CELL}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{extra}/>'
    if nuc:
        nr = r*0.3
        ox, oy = (rnd.random()-.5)*r*0.3, (rnd.random()-.5)*r*0.3
        s += f'<circle cx="{f(cx+ox)}" cy="{f(cy+oy)}" r="{f(nr)}" fill="{NUC}"/>'
        if rnd.random() < 0.07:
            s += f'<circle cx="{f(cx-ox+nr*1.6)}" cy="{f(cy+oy)}" r="{f(nr)}" fill="{NUC}"/>'
    return s

def in_ell(x, y, cx, cy, rx, ry):
    return ((x-cx)/rx)**2 + ((y-cy)/ry)**2 <= 1

def field(w, h, sp, avoid, rnd, margin=6):
    pts = []
    dy = sp*0.86
    row = 0
    y = margin
    while y < h - margin + 1:
        x = margin + (sp/2 if row % 2 else 0)
        while x < w - margin + 1:
            px, py = x + (rnd.random()-.5)*sp*0.18, y + (rnd.random()-.5)*sp*0.18
            if not any(a(px, py) for a in avoid):
                pts.append((px, py))
            x += sp
        y += dy; row += 1
    return pts

def lym(x, y, r=2.9):
    return f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{LYM}"/>'

def plasma(x, y, rnd):
    a = rnd.random()*180
    return (f'<g transform="rotate({f(a)} {f(x)} {f(y)})"><ellipse cx="{f(x)}" cy="{f(y)}" rx="5.4" ry="3.8" fill="{PLASMA}"/>'
            f'<circle cx="{f(x+2.2)}" cy="{f(y)}" r="2.2" fill="{LYM}"/></g>')

def portal(cx, cy, rx, ry, rnd, nlym=6, sc=1.0):
    s = f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="{STROMA}" stroke="{STROMAS}" stroke-width="1"/>'
    for k in range(4):
        yy = cy - ry*0.6 + k*ry*0.4
        s += f'<path d="M{f(cx-rx*0.7)} {f(yy)} q{f(rx*0.35)} {f(-ry*0.12)} {f(rx*0.7)} 0 t{f(rx*0.7)} 0" fill="none" stroke="{FIB}" stroke-width="0.9"/>'
    vx, vy = cx - rx*0.22, cy + ry*0.05
    s += f'<ellipse cx="{f(vx)}" cy="{f(vy)}" rx="{f(rx*0.36)}" ry="{f(ry*0.24)}" fill="#ffffff" stroke="#c98a9c" stroke-width="1.2"/>'
    s += f'<ellipse cx="{f(vx-3*sc)}" cy="{f(vy+2*sc)}" rx="{f(2.4*sc)}" ry="{f(1.7*sc)}" fill="{RBC}"/><ellipse cx="{f(vx+5*sc)}" cy="{f(vy-1*sc)}" rx="{f(2.4*sc)}" ry="{f(1.7*sc)}" fill="{RBC}"/>'
    ax, ay, ar = cx + rx*0.38, cy - ry*0.36, rx*0.13
    s += f'<circle cx="{f(ax)}" cy="{f(ay)}" r="{f(ar)}" fill="#ffffff" stroke="#c0607d" stroke-width="{f(ar*0.75)}"/>'
    bx, by, br = cx + rx*0.38, cy + ry*0.4, rx*0.15
    s += f'<circle cx="{f(bx)}" cy="{f(by)}" r="{f(br)}" fill="#fff6f8" stroke="{STROMAS}" stroke-width="0.8"/>'
    for k in range(8):
        a = k*math.pi/4
        s += f'<circle cx="{f(bx+br*0.72*math.cos(a))}" cy="{f(by+br*0.72*math.sin(a))}" r="{f(br*0.2)}" fill="{NUC}"/>'
    vessels = [(vx, vy, rx*0.42, ry*0.32), (ax, ay, ar*1.7, ar*1.7), (bx, by, br*1.5, br*1.5)]
    pts = []
    tries = 0
    while len(pts) < nlym and tries < 5000:
        tries += 1
        x = cx + (rnd.random()*2-1)*rx*0.9; y = cy + (rnd.random()*2-1)*ry*0.9
        if not in_ell(x, y, cx, cy, rx*0.9, ry*0.9): continue
        if any(in_ell(x, y, a, b, c, d) for a, b, c, d in vessels): continue
        pts.append((x, y))
    return s, pts

def pill(x, y, text, w=None, anchor="middle"):
    w = w or (len(text)*6.4 + 16)
    rx = x - w/2 if anchor == "middle" else x
    return (f'<rect x="{f(rx)}" y="{f(y-11)}" width="{f(w)}" height="22" rx="11" fill="#ffffff" fill-opacity=".93" stroke="{LBL}" stroke-width=".7"/>'
            f'<text x="{f(rx+w/2)}" y="{f(y+4)}" text-anchor="middle" font-size="11.5" font-weight="600" fill="{LBL}">{text}</text>')

def leader(x1, y1, x2, y2):
    return f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{LBL}" stroke-width=".9"/><circle cx="{f(x2)}" cy="{f(y2)}" r="2" fill="{LBL}"/>'

# ---------------- Lámina A: lobulillo y acino (esquema, colores de tema) ----------------
def lam_a():
    s = ['<svg viewBox="0 0 640 290" role="img" aria-label="Lobulillo clásico con zonas concéntricas y acino de Rappaport con zonas alrededor del eje portal">']
    cx, cy, R = 160, 140, 115
    def hp(sc):
        return " ".join(f"{f(cx+R*sc*math.cos(math.radians(-90+60*k)))},{f(cy+R*sc*math.sin(math.radians(-90+60*k)))}" for k in range(6))
    s.append(f'<polygon points="{hp(1)}" style="fill:color-mix(in srgb,var(--acento) 36%,var(--panel));stroke:var(--line-2)"/>')
    s.append(f'<polygon points="{hp(.66)}" style="fill:color-mix(in srgb,var(--acento) 18%,var(--panel));stroke:var(--line-2)" stroke-dasharray="4 3"/>')
    s.append(f'<polygon points="{hp(.33)}" style="fill:color-mix(in srgb,var(--acento) 5%,var(--panel));stroke:var(--line-2)" stroke-dasharray="4 3"/>')
    for k in range(12):
        a = math.radians(-90+30*k)
        rr = R if k % 2 == 0 else R*math.cos(math.radians(30))
        s.append(f'<line x1="{f(cx+13*math.cos(a))}" y1="{f(cy+13*math.sin(a))}" x2="{f(cx+(rr-12)*math.cos(a))}" y2="{f(cy+(rr-12)*math.sin(a))}" style="stroke:var(--fg-3)" stroke-width=".6" opacity=".55"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="10" style="fill:var(--panel);stroke:var(--fg-2)" stroke-width="1.4"/>')
    for k in range(6):
        a = math.radians(-90+60*k)
        px, py = cx+R*math.cos(a), cy+R*math.sin(a)
        s.append(triad(px, py))
    for txt, x in (("3", cx+22), ("2", cx+50), ("1", cx+82)):
        s.append(f'<text x="{f(x)}" y="{cy+5}" text-anchor="middle" font-size="14" font-weight="700" style="fill:var(--fg)">{txt}</text>')
    s.append(f'<text x="{cx}" y="282" text-anchor="middle" font-size="12.5" font-weight="600" style="fill:var(--fg)">Lobulillo clásico</text>')
    # Acino
    ax, ay = 470, 140
    s.append('<defs><clipPath id="clipAcino"><polygon points="470,28 572,140 470,252 368,140"/></clipPath></defs>')
    s.append('<polygon points="470,28 572,140 470,252 368,140" style="fill:color-mix(in srgb,var(--acento) 5%,var(--panel));stroke:var(--line-2)"/>')
    s.append('<g clip-path="url(#clipAcino)">'
             '<ellipse cx="470" cy="140" rx="104" ry="68" style="fill:color-mix(in srgb,var(--acento) 18%,var(--panel));stroke:var(--line-2)" stroke-dasharray="4 3"/>'
             '<ellipse cx="470" cy="140" rx="104" ry="31" style="fill:color-mix(in srgb,var(--acento) 36%,var(--panel));stroke:var(--line-2)" stroke-dasharray="4 3"/></g>')
    s.append('<line x1="380" y1="140" x2="560" y2="140" style="stroke:var(--marino)" stroke-width="2.2"/>')
    for vy in (28, 252):
        s.append(f'<circle cx="470" cy="{vy}" r="10" style="fill:var(--panel);stroke:var(--fg-2)" stroke-width="1.4"/>')
    s.append(triad(368, 140)); s.append(triad(572, 140))
    s.append('<text x="488" y="32" font-size="11.5" style="fill:var(--fg-2)">VC</text><text x="488" y="256" font-size="11.5" style="fill:var(--fg-2)">VC</text>')
    s.append('<text x="368" y="117" text-anchor="middle" font-size="11.5" style="fill:var(--fg-2)">EP</text><text x="572" y="117" text-anchor="middle" font-size="11.5" style="fill:var(--fg-2)">EP</text>')
    for txt, y in (("1", 127), ("2", 98), ("3", 62)):
        s.append(f'<text x="470" y="{y}" text-anchor="middle" font-size="14" font-weight="700" style="fill:var(--fg)">{txt}</text>')
    s.append('<text x="470" y="282" text-anchor="middle" font-size="12.5" font-weight="600" style="fill:var(--fg)">Acino de Rappaport</text>')
    s.append('</svg>')
    return "".join(s)

def triad(px, py, r=10):
    return (f'<circle cx="{f(px)}" cy="{f(py)}" r="{r}" style="fill:var(--panel);stroke:var(--marino)" stroke-width="1.3"/>'
            f'<circle cx="{f(px-3.2)}" cy="{f(py+1.5)}" r="2.6" style="fill:var(--marino-2)"/>'
            f'<circle cx="{f(px+3.4)}" cy="{f(py-3)}" r="1.8" style="fill:var(--rojo)"/>'
            f'<circle cx="{f(px+3.4)}" cy="{f(py+3.6)}" r="1.8" style="fill:var(--verde)"/>')

# ---------------- Lámina B: corte EP → VC en H&E ----------------
def lam_b():
    rnd = random.Random(4)
    W, H = 640, 300
    pcx, pcy, prx, pry = 92, 150, 58, 74
    vcx, vcy, vr = 548, 150, 26
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Corte H&amp;E esquemático desde el espacio porta hasta la vena central con las tres zonas">',
         f'<defs><clipPath id="clipB"><rect width="{W}" height="{H}" rx="10"/></clipPath></defs>',
         f'<rect width="{W}" height="{H}" rx="10" fill="{SLIDE}"/>', '<g clip-path="url(#clipB)">']
    avoid = [lambda x, y: in_ell(x, y, pcx, pcy, prx+9, pry+9), lambda x, y: math.hypot(x-vcx, y-vcy) < vr+8]
    for x, y in field(W, H, 17, avoid, rnd, margin=4):
        s.append(cell(x, y, 8.4, rnd))
    # sinusoides convergiendo en la VC
    n = 44
    for i in range(n):
        a = 2*math.pi*i/n + 0.03
        r0 = vr+1 if i % 4 == 0 else (52 if i % 2 == 0 else 92)
        pts = []
        r = r0
        while r < 700:
            x, y = vcx + r*math.cos(a), vcy + r*math.sin(a)
            if x < -5 or x > W+5 or y < -5 or y > H+5 or in_ell(x, y, pcx, pcy, prx+3, pry+3):
                break
            pts.append((x, y)); r += 6
        if len(pts) < 2: continue
        s.append(f'<polyline points="{" ".join(f"{f(x)},{f(y)}" for x, y in pts)}" fill="none" stroke="#fffafb" stroke-width="3.4" stroke-linecap="round"/>')
        for _ in range(int(len(pts)/14)+1):
            x, y = pts[rnd.randrange(len(pts))]
            s.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="2.1" ry="1.5" fill="{RBC}" transform="rotate({f(math.degrees(a))} {f(x)} {f(y)})"/>')
    pt, lyms = portal(pcx, pcy, prx, pry, rnd, nlym=7)
    s.append(pt); s += [lym(x, y) for x, y in lyms]
    s.append(f'<circle cx="{vcx}" cy="{vcy}" r="{vr}" fill="#ffffff" stroke="#c98a9c" stroke-width="1.3"/>')
    for dx, dy in ((-7, 4), (5, -6), (8, 8)):
        s.append(f'<ellipse cx="{vcx+dx}" cy="{vcy+dy}" rx="2.6" ry="1.8" fill="{RBC}"/>')
    # límites de zona
    s.append(f'<circle cx="{pcx}" cy="{pcy}" r="175" fill="none" stroke="{LBL}" stroke-width="1.3" stroke-dasharray="7 5" opacity=".75"/>')
    s.append(f'<circle cx="{vcx}" cy="{vcy}" r="150" fill="none" stroke="{LBL}" stroke-width="1.3" stroke-dasharray="7 5" opacity=".75"/>')
    s.append('</g>')
    s.append(pill(208, 150, "Zona 1", 64)); s.append(pill(332, 150, "Zona 2", 64)); s.append(pill(456, 150, "Zona 3", 64))
    s.append(pill(92, 262, "Espacio porta")); s.append(pill(548, 204, "Vena central"))
    s.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="none" stroke="{STROMAS}" stroke-width="1"/>')
    s.append('</svg>')
    return "".join(s)

# ---------------- Lámina C: placa limitante, interfase, HAI ----------------
def lam_c(kind):
    rnd = random.Random({"normal": 11, "inter": 12, "hai": 13}[kind])
    W, H = 300, 240
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{kind}">',
         f'<defs><clipPath id="clipC{kind}"><rect width="{W}" height="{H}" rx="10"/></clipPath></defs>',
         f'<rect width="{W}" height="{H}" rx="10" fill="{SLIDE}"/>', f'<g clip-path="url(#clipC{kind})">']
    if kind in ("normal", "inter"):
        cx, cy, rx, ry = 96, 120, 58, 66
        ringrx, ringry = rx+12, ry+12
        sect = lambda ang: -55 <= math.degrees(ang) <= 55  # sector derecho
        avoid = [lambda x, y: in_ell(x, y, cx, cy, rx+25, ry+25)]
        if kind == "inter":
            avoid.append(lambda x, y: in_ell(x, y, cx, cy, rx+46, ry+40) and x > cx+20 and rnd.random() < 0.6)
        for x, y in field(W, H, 21, avoid, rnd, margin=2):
            s.append(cell(x, y, 10.2, rnd))
        # placa limitante
        nring = 24
        ringpts = []
        for k in range(nring):
            a = 2*math.pi*k/nring
            x, y = cx + ringrx*math.cos(a), cy + ringry*math.sin(a)
            if kind == "inter" and sect(a):
                if k % 3 == 0:
                    s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="5" fill="{ACID}" stroke="#c24f6c" stroke-width=".8"/>')
                    ringpts.append(("acid", x, y))
                continue
            s.append(cell(x, y, 9.6, rnd, stroke=PLATE if kind == "normal" else CELLS, sw=1.6 if kind == "normal" else .8))
            ringpts.append(("cell", x, y))
        pt, lyms = portal(cx, cy, rx, ry, rnd, nlym=8 if kind == "normal" else 34)
        s.append(pt)
        for i, (x, y) in enumerate(lyms):
            s.append(plasma(x, y, rnd) if (kind == "inter" and i % 4 == 0) else lym(x, y))
        if kind == "inter":
            k = 0; tries = 0
            while k < 46 and tries < 9000:
                tries += 1
                a = math.radians(-58 + rnd.random()*116)
                t = 0.98 + rnd.random()*0.75
                x, y = cx + rx*t*math.cos(a), cy + ry*t*math.sin(a)
                if x > W-6 or y < 6 or y > H-6: continue
                s.append(plasma(x, y, rnd) if k % 5 == 0 else lym(x, y)); k += 1
        s.append('</g>')
        if kind == "normal":
            _, x2, y2 = min(ringpts, key=lambda p: abs(p[2]-(cy-ry-12)) + abs(p[1]-(cx+40)))
            s.append(leader(220, 26, x2+3, y2-3)); s.append(pill(236, 26, "Placa limitante", 100))
        else:
            acids = [p for p in ringpts if p[0] == "acid"]
            if acids:
                _, x2, y2 = acids[0]
                s.append(leader(232, 212, x2+3, y2+3)); s.append(pill(236, 214, "Cuerpo acidófilo", 108))
            s.append(pill(234, 26, "Infiltrado cruza", 106))
    else:  # HAI: roseta y emperipolesis
        rcx, rcy = 108, 104
        ecx, ecy = 214, 168
        avoid = [lambda x, y: math.hypot(x-rcx, y-rcy) < 50, lambda x, y: math.hypot(x-ecx, y-ecy) < 28]
        for x, y in field(W, H, 21, avoid, rnd, margin=2):
            s.append(cell(x, y, 10.2, rnd))
        # infiltrado alrededor de la roseta
        for k in range(34):
            a = rnd.random()*2*math.pi; r = 38 + rnd.random()*10
            x, y = rcx + r*math.cos(a), rcy + r*math.sin(a)
            s.append(plasma(x, y, rnd) if k % 3 == 0 else lym(x, y))
        for k in range(7):
            a = 2*math.pi*k/7
            x, y = rcx + 19*math.cos(a), rcy + 19*math.sin(a)
            rot = math.degrees(a)
            s.append(f'<g transform="rotate({f(rot)} {f(x)} {f(y)})"><ellipse cx="{f(x)}" cy="{f(y)}" rx="11.5" ry="8" fill="{CELL}" stroke="{CELLS}" stroke-width=".8"/>'
                     f'<circle cx="{f(x+4)}" cy="{f(y)}" r="3" fill="{NUC}"/></g>')
        s.append(f'<circle cx="{rcx}" cy="{rcy}" r="4.5" fill="#ffffff" stroke="{CELLS}" stroke-width=".7"/>')
        # emperipolesis
        s.append(f'<polygon points="{hexpoly(ecx, ecy, 20, .3)}" fill="{CELL}" stroke="{CELLS}" stroke-width=".9" stroke-linejoin="round"/>')
        s.append(f'<circle cx="{ecx-7}" cy="{ecy-4}" r="5" fill="{NUC}"/>')
        s.append(f'<circle cx="{ecx+6}" cy="{ecy+5}" r="6.6" fill="#ffffff"/>')
        s.append(lym(ecx+6, ecy+5, 4))
        s.append('</g>')
        s.append(leader(60, 26, rcx-12, rcy-16)); s.append(pill(64, 26, "Roseta", 62))
        s.append(leader(150, 220, ecx+4, ecy+9)); s.append(pill(110, 220, "Emperipolesis", 96))
    s.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="none" stroke="{STROMAS}" stroke-width="1"/>')
    s.append('</svg>')
    return "".join(s)

# ---------------- Lámina D: patrones zonales (esquema, colores de tema) ----------------
def pip(x, y, poly):
    ins = False; j = len(poly)-1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj-xi)*(y-yi)/(yj-yi+1e-9)+xi: ins = not ins
        j = i
    return ins

def mini(kind, idx):
    rnd = random.Random(100+idx)
    cx, cy, R = 100, 92, 74
    V = [(cx+R*math.cos(math.radians(-90+60*k)), cy+R*math.sin(math.radians(-90+60*k))) for k in range(6)]
    def hx(sc): return [(cx+(x-cx)*sc, cy+(y-cy)*sc) for x, y in V]
    def ps(poly): return " ".join(f"{f(x)},{f(y)}" for x, y in poly)
    cid = f"clipM{idx}"
    s = [f'<svg viewBox="0 0 200 184" role="img" aria-label="{kind}">',
         f'<defs><clipPath id="{cid}"><polygon points="{ps(V)}"/></clipPath></defs>',
         f'<polygon points="{ps(V)}" style="fill:var(--panel-2);stroke:var(--line-2)" stroke-width="1"/>']
    if kind == "ref":
        s.append(f'<polygon points="{ps(V)}" style="fill:color-mix(in srgb,var(--acento) 36%,var(--panel))"/>')
        s.append(f'<polygon points="{ps(hx(.66))}" style="fill:color-mix(in srgb,var(--acento) 18%,var(--panel))"/>')
        s.append(f'<polygon points="{ps(hx(.33))}" style="fill:color-mix(in srgb,var(--acento) 5%,var(--panel))"/>')
    s.append(f'<polygon points="{ps(hx(.66))}" fill="none" style="stroke:var(--line-2)" stroke-dasharray="3 3"/>')
    s.append(f'<polygon points="{ps(hx(.33))}" fill="none" style="stroke:var(--line-2)" stroke-dasharray="3 3"/>')
    for k in range(12):
        a = math.radians(-90+30*k)
        rr = R if k % 2 == 0 else R*math.cos(math.radians(30))
        s.append(f'<line x1="{f(cx+10*math.cos(a))}" y1="{f(cy+10*math.sin(a))}" x2="{f(cx+(rr-9)*math.cos(a))}" y2="{f(cy+(rr-9)*math.sin(a))}" style="stroke:var(--fg-3)" stroke-width=".5" opacity=".5"/>')

    def sample(n, cond, r=2.0, style="fill:var(--rojo)", shape="c"):
        out = []; t = 0
        while len(out) < n and t < 20000:
            t += 1
            x, y = cx-R + rnd.random()*2*R, cy-R + rnd.random()*2*R
            if not pip(x, y, V) or not cond(x, y): continue
            if any(math.hypot(x-a, y-b) < r*2.1 for a, b in out): continue
            out.append((x, y))
        for x, y in out:
            if shape == "c":
                s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" style="{style}"/>')
            elif shape == "fat":
                rr = r*(0.6+rnd.random()*0.6)
                s.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rr)}" style="fill:var(--panel);stroke:var(--ambar)" stroke-width="1"/>')
            elif shape == "rbc":
                s.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(r*1.3)}" ry="{f(r*0.9)}" style="{style}"/>')

    NEC = 'style="fill:url(#necro);stroke:var(--rojo)" stroke-width="1"'
    inner = lambda sc: (lambda x, y: pip(x, y, hx(sc)))
    band = lambda a, b: (lambda x, y: pip(x, y, hx(b)) and not pip(x, y, hx(a)))
    nearV = lambda d: (lambda x, y: min(math.hypot(x-a, y-b) for a, b in V) < d)
    if kind == "z3":
        s.append(f'<polygon points="{ps(hx(.42))}" {NEC}/>')
    elif kind == "z1":
        s.append(f'<g clip-path="url(#{cid})">' + "".join(f'<circle cx="{f(x)}" cy="{f(y)}" r="27" {NEC}/>' for x, y in V) + '</g>')
    elif kind == "z2":
        s.append(f'<path d="M{ps(hx(.68))}Z M{ps(list(reversed(hx(.34))))}Z" fill-rule="evenodd" {NEC}/>')
    elif kind == "pc":
        for k in (0, 2):
            x, y = V[k]
            s.append(f'<line x1="{f(x)}" y1="{f(y)}" x2="{cx}" y2="{cy}" style="stroke:var(--rojo)" stroke-width="15" stroke-linecap="round" opacity=".35"/>')
    elif kind == "pp":
        (x1, y1), (x2, y2) = V[1], V[2]
        s.append(f'<g clip-path="url(#{cid})"><line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" style="stroke:var(--rojo)" stroke-width="26" opacity=".35"/></g>')
    elif kind == "pan":
        s.append(f'<polygon points="{ps(V)}" {NEC}/>')
    elif kind == "fat":
        sample(34, inner(.5), r=5.4, shape="fat")
        sample(5, band(.5, .7), r=4, shape="fat")
    elif kind == "iron":
        sample(70, nearV(30), r=1.7, style="fill:var(--marino-2)")
        sample(18, lambda x, y: 30 <= min(math.hypot(x-a, y-b) for a, b in V) < 50, r=1.5, style="fill:var(--marino-2)")
    elif kind == "cong":
        sample(70, inner(.48), r=2.2, style="fill:var(--rojo)", shape="rbc")
    elif kind == "chol":
        sample(26, inner(.48), r=2.3, style="fill:var(--verde)")
    elif kind == "inter":
        for x, y in V:
            for k in range(60):
                a = rnd.random()*2*math.pi; r = 9 + rnd.random()*20
                px, py = x + r*math.cos(a), y + r*math.sin(a)
                if pip(px, py, V):
                    s.append(f'<circle cx="{f(px)}" cy="{f(py)}" r="2.1" style="fill:var(--acento)"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="8" style="fill:var(--panel);stroke:var(--fg-2)" stroke-width="1.2"/>')
    for x, y in V:
        s.append(triad(x, y, 8))
    if kind == "ref":
        for txt, x in (("3", cx+18), ("2", cx+41), ("1", cx+57)):
            s.append(f'<text x="{f(x)}" y="{cy+4}" text-anchor="middle" font-size="12" font-weight="700" style="fill:var(--fg)">{txt}</text>')
    s.append('</svg>')
    return "".join(s)


# ---------------- Inserción en el bloque ----------------
MINIS = [
    ("ref", "Zonas en el lobulillo", "Zona 1 en los vértices (espacios porta), zona 3 alrededor de la vena central."),
    ("z3", "Necrosis centrolobulillar (zona 3)", "Paracetamol, hepatitis isquémica, congestión grave, halotano. También HAI de presentación aguda."),
    ("z1", "Necrosis periportal (zona 1)", "Eclampsia y HELLP (con fibrina periportal), fósforo amarillo, intoxicación por hierro."),
    ("z2", "Necrosis mediozonal (zona 2)", "Fiebre amarilla, con cuerpos de Councilman. Rara."),
    ("pc", "Necrosis en puente porta–central", "Hepatitis aguda grave o HAI. Peor pronóstico que el puente porta–porta."),
    ("pp", "Necrosis en puente porta–porta", "Une espacios porta vecinos; antecede a los septos porta–porta."),
    ("pan", "Necrosis panacinar o multiacinar", "Todo el acino colapsado: falla hepática aguda viral, por fármacos o por HAI."),
    ("fat", "Esteatosis y balonamiento (zona 3)", "MASH del adulto y alcohol. En niños el patrón puede ser periportal (tipo 2)."),
    ("iron", "Siderosis periportal (zona 1)", "Hemocromatosis HFE: gradiente zona 1 → 3 en hepatocitos con Perls. La sobrecarga secundaria carga células de Kupffer."),
    ("cong", "Congestión centrolobulillar", "Insuficiencia cardiaca derecha, pericarditis constrictiva, Budd-Chiari, síndrome de obstrucción sinusoidal."),
    ("chol", "Colestasis centrolobulillar", "Tapones biliares canaliculares en zona 3: sepsis, estrógenos y anabólicos, obstrucción temprana."),
    ("inter", "Hepatitis de interfase", "Infiltrado que desborda los espacios porta hacia la zona 1: HAI, hepatitis B y C crónicas, DILI, Wilson."),
]
PLATES = [
    ("normal", "Placa limitante íntegra", "La primera hilera de hepatocitos rodea el espacio porta sin interrupciones. El infiltrado, si existe, queda dentro del estroma."),
    ("inter", "Hepatitis de interfase", "Linfocitos y plasmocitos cruzan la placa, aíslan hepatocitos periportales y dejan cuerpos acidófilos (apoptosis)."),
    ("hai", "Rosetas y emperipolesis", "Hepatocitos regenerativos en anillo alrededor de una luz y un linfocito dentro de un hepatocito. Frecuentes en HAI, pero el consenso IAIHPG 2022 ya no los considera específicos."),
]
ARIA = {"normal": "Espacio porta con placa limitante íntegra",
        "inter": "Hepatitis de interfase: infiltrado linfoplasmocitario que rompe la placa limitante",
        "hai": "Roseta de hepatocitos y emperipolesis"}

TOK = {"panel-2": "h-panel2", "panel": "h-panel", "fg": "h-fg", "fg-2": "h-fg2", "fg-3": "h-fg3",
       "line-2": "h-line2", "marino": "h-marino", "marino-2": "h-marino2", "rojo": "h-rojo",
       "verde": "h-verde", "ambar": "h-ambar", "acento": "h-zona"}

# Atributos repetidos miles de veces en los campos de hepatocitos: se pasan a clases de extra.css (.histo .hc/.hn/.hl)
CLASES = [(f' fill="{CELL}" stroke="{CELLS}" stroke-width="0.8" stroke-linejoin="round"', ' class="hc"'),
          (f' fill="{NUC}"/>', ' class="hn"/>'), (f' fill="{LYM}"/>', ' class="hl"/>')]

def tokens(svg):
    svg = re.sub(r"var\(--([a-z0-9-]+)\)", lambda m: f"var(--{TOK.get(m.group(1), m.group(1))})", svg)
    for viejo, clase in CLASES:
        svg = svg.replace(viejo, clase)
    svg = svg.replace('id="clip', 'id="hclip').replace("url(#clip", "url(#hclip").replace("url(#necro)", "url(#hnecro)")
    return svg

def aria(svg, viejo, nuevo):
    return svg.replace('aria-label="%s"' % viejo, 'aria-label="%s"' % nuevo, 1)

def ley(items):
    return '<div class="h-ley">' + "".join(f'<span><i style="{st}"></i>{t}</span>' for st, t in items) + "</div>"

def figuras():
    zona = lambda p: f"background:color-mix(in srgb,var(--h-zona) {p}%,var(--h-panel))"
    F = {}
    F["lobulillo"] = (f'<div class="h-wide">{tokens(lam_a())}</div>' + ley([
        (zona(36), "Zona 1 · periportal"), (zona(18), "Zona 2 · mediozonal"),
        (zona(5) + ";border:1px solid var(--h-line2)", "Zona 3 · centrolobulillar")]))
    F["corte"] = (f'<div class="h-wide he">{tokens(lam_b())}</div>' + ley([
        (f"background:{CELL}", "Hepatocito"), (f"background:{NUC}", "Núcleo"),
        (f"background:{STROMA};border:1px solid {STROMAS}", "Estroma portal"),
        (f"background:{LYM}", "Linfocito"), (f"background:{RBC}", "Eritrocito en sinusoide")]))
    pans = "".join(
        f'<figure class="lam">{aria(tokens(lam_c(k)), k, ARIA[k])}'
        f'<figcaption><b>{t}.</b> {d}</figcaption></figure>' for k, t, d in PLATES)
    F["interfase"] = (f'<div class="lam-g h-tres">{pans}</div>' + ley([
        (f"background:{PLATE}", "Placa limitante resaltada"), (f"background:{PLASMA}", "Plasmocito"),
        (f"background:{LYM}", "Linfocito"), (f"background:{ACID}", "Cuerpo acidófilo")]))
    defs = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
            '<pattern id="hnecro" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            '<rect width="6" height="6" style="fill:color-mix(in srgb,var(--h-rojo) 22%,var(--h-panel2))"/>'
            '<line x1="0" y1="0" x2="0" y2="6" style="stroke:var(--h-rojo)" stroke-width="1.4" opacity=".7"/></pattern></defs></svg>')
    minis = "".join(
        f'<figure class="lam">{aria(tokens(mini(k, i)), k, t)}'
        f'<figcaption><b>{t}.</b> {d}</figcaption></figure>' for i, (k, t, d) in enumerate(MINIS))
    F["patrones"] = (defs + f'<div class="lam-g h-minis">{minis}</div>' + ley([
        ("background:repeating-linear-gradient(45deg,var(--h-rojo) 0 2px,transparent 2px 5px)", "Necrosis"),
        ("background:var(--h-panel);border:1.5px solid var(--h-ambar)", "Vacuola de grasa"),
        ("background:var(--h-marino2)", "Hierro (Perls)"), ("background:var(--h-verde)", "Bilirrubinostasis"),
        ("background:var(--h-zona)", "Infiltrado inflamatorio"), ("background:var(--h-rojo)", "Eritrocitos (congestión)")]))
    return F

if __name__ == "__main__":
    destino = AQUI.parent / "bloques" / "b00_histologia.html"
    txt = destino.read_text(encoding="utf-8")
    for nombre, contenido in figuras().items():
        patron = re.compile(r"(<!--FIG:%s-->).*?(<!--/FIG:%s-->)" % (nombre, nombre), re.S)
        if not patron.search(txt):
            raise SystemExit(f"Falta la marca <!--FIG:{nombre}--> en {destino.name}")
        txt = patron.sub(lambda m: m.group(1) + "\n" + contenido + "\n" + m.group(2), txt)
    destino.write_text(txt, encoding="utf-8")
    print(f"{destino.name}: figuras insertadas ({len(txt)//1024} KB)")
