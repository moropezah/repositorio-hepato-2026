#!/usr/bin/env python3
"""Ensambla guia-2026.html a partir de fuentes/guia/.

Uso (desde la raíz del repositorio):  python3 fuentes/guia/actualizar.py

- bloques.json define el orden, los grupos y qué bloques están escritos.
- Cada bloque escrito vive en bloques/<archivo>.html y empieza con su <h2 id="bN">.
- Un bloque con "archivo": null aparece en el índice como pendiente y con un aviso en el cuerpo.
Solo regenera guia-2026.html; no toca ningún otro módulo.
"""
import json, re, html, pathlib, datetime

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
cfg = json.loads((AQUI / "bloques.json").read_text(encoding="utf-8"))

css = (AQUI / "estilos.css").read_text(encoding="utf-8") + (AQUI / "extra.css").read_text(encoding="utf-8")
pwa_css = (AQUI / "pwa.css").read_text(encoding="utf-8")
js = (AQUI / "guia.js").read_text(encoding="utf-8")

escritos, total, nfc, npreg = 0, 0, 0, 0
nav, cuerpo = [], []
for g in cfg["grupos"]:
    nav.append(f'  <div class="grp">{html.escape(g["nombre"])}</div>')
    for i, b in enumerate(g["bloques"]):
        total += 1
        clase = "" if i == 0 else ' class="sub"'
        if b["archivo"] and (AQUI / "bloques" / b["archivo"]).exists():
            escritos += 1
            frag = (AQUI / "bloques" / b["archivo"]).read_text(encoding="utf-8")
            if f'id="{b["id"]}"' not in frag:
                raise SystemExit(f'El bloque {b["archivo"]} no contiene id="{b["id"]}"')
            nfc += frag.count('class="fc"')
            for m in re.finditer(r'<script type="application/json" class="qz-data"[^>]*>(.*?)</script>', frag, re.S):
                npreg += len(json.loads(m.group(1)))
            nav.append(f'  <a href="#{b["id"]}"{clase}>{b["num"]} · {html.escape(b["corto"])}</a>')
            cuerpo.append(f'\n<!-- ================= BLOQUE {b["num"]} ================= -->\n' + frag.strip() + "\n")
        else:
            cl = ' class="sub off"' if i else ' class="off"'
            nav.append(f'  <a href="#{b["id"]}"{cl}>{b["num"]} · {html.escape(b["corto"])}</a>')
            cuerpo.append(
                f'\n<!-- ================= BLOQUE {b["num"]} (pendiente) ================= -->\n'
                f'<h2 id="{b["id"]}"><span class="num">{b["num"]}</span>{html.escape(b["titulo"])}</h2>\n'
                f'<div class="pend"><b>Bloque en preparación.</b> Se construirá con el programa del Curso de Becados 2026, '
                f'el Curso de Cirrosis y Trasplante Hepático de Clínica Dávila 2026 y las guías vigentes, con el mismo formato '
                f'de los bloques de cirrosis.</div>\n')

nav.append('  <div class="grp">Cierre</div>')
nav.append('  <a href="#fuentes">Fuentes del curso</a>')

hoy = datetime.date.today().isoformat()
doc = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="author" content="Dr. Moisés Oropeza">
<title>Módulo 1 · Guía de estudio Hepatología 2026</title>
<style>
{css}
</style>
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
</head>
<body>
<div id="wrap">
<aside id="nav">
  <div class="brand"><span>Guía de estudio</span><b>Hepatología 2026</b></div>
  <input id="navsearch" type="search" placeholder="Filtrar secciones…" autocomplete="off">
  <div id="navlinks">
  <a href="#inicio">Cómo usar esta guía</a>
{chr(10).join(nav)}
  </div>
</aside>

<main>
<header class="hero"><div class="inner">
  <div class="kicker">Postgrado de Gastroenterología · Repaso integrado</div>
  <h1>Hepatología 2026</h1>
  <p>Clase de repaso de la patología hepática que un residente de gastroenterología debe manejar: cirrosis y sus complicaciones,
  etiologías, hepatocarcinoma y trasplante. Construida sobre el programa del Curso de Hepatología para Becados 2026 y del Curso de
  Cirrosis y Trasplante Hepático de Clínica Dávila 2026, contrastada con Baveno VIII y las guías EASL, AASLD, ACG y AGA vigentes,
  y con el marco chileno (GES, guías MINSAL, consensos ACHHEP) declarado donde cambia la conducta.</p>
  <div class="meta">
    <div><b>Actualizado</b> · {cfg["actualizado"]}</div>
    <div><b>Nivel</b> · residente de gastroenterología</div>
    <div><b>Marco local</b> · GES 88 · MINSAL</div>
    <div><b>{escritos} de {total} bloques</b> · {nfc} flashcards · {npreg} preguntas</div>
  </div>
  <div class="autor-g">
    <span class="ini-g">MO</span>
    <div>
      <div class="n-g">Dr. Moisés Oropeza</div>
      <div class="r-g">Residente de Gastroenterología, Universidad de los Andes · Clínica Dávila / Clínica Universidad de los Andes — autoría y edición</div>
    </div>
  </div>
</div></header>

<div class="inner">

<h2 id="inicio">Cómo usar esta guía</h2>
<p class="lead">Cada bloque es autosuficiente y sigue la misma estructura, para que se pueda estudiar por separado o repasar en orden.</p>
<div class="cards">
  <div class="card"><h5>Contenido</h5><p>Definiciones y clasificaciones vigentes, umbrales numéricos y algoritmos con fármaco, dosis y criterio de falla.</p></div>
  <div class="card"><h5>Qué cambió</h5><p>Tabla al inicio de cada bloque con lo nuevo frente a la guía previa (Baveno VIII frente a Baveno VII, EASL 2026 frente a 2016, etc.).</p></div>
  <div class="card"><h5>Marcadores</h5><p><b>Idea clave</b> para el examen oral, <b>error frecuente</b>, <b>perla</b> y <b>Chile</b> cuando el GES o la disponibilidad cambian la conducta.</p></div>
  <div class="card"><h5>Autoevaluación</h5><p>Cada bloque cierra con un caso clínico, flashcards (clic para ver la respuesta) y preguntas con corrección razonada.</p></div>
</div>
<div class="box nue"><div class="t">Sobre la evidencia</div>
<p>Baveno VIII se publicó en agosto de 2026 (J Hepatol 2026;85:993–1018). Los umbrales que aquí se le atribuyen provienen de su resumen
oficial y de las charlas del curso que ya los incorporaron; donde la redacción exacta del consenso importa para la conducta, el texto lo indica.
El listado de fármacos de la canasta del GES 88 se verifica en el Módulo 03 (vademécum). La Ley Ricarte Soto no cubre fármacos de hepatología (su única condición hepática es la tirosinemia tipo 1, con nitisinona).</p></div>
{"".join(cuerpo)}

<!-- ================= FUENTES ================= -->
<h2 id="fuentes">Fuentes del curso</h2>
<p class="lead">Material docente sobre el que se construyó la guía. Las referencias bibliográficas de cada tema están al final de su bloque.</p>
<div class="tw"><table class="sm">
<thead><tr><th style="width:28%">Fuente</th><th>Contenido usado</th></tr></thead>
<tbody>
<tr><td><b>Curso de Cirrosis y Trasplante Hepático · Clínica Dávila</b><br><span class="small">31 de julio y 1 de agosto de 2026</span></td><td>Actualizaciones en cirrosis (Oropeza), ACLF (Olivares), futilidad del trasplante en ACLF (Berenguer), anticoagulación (Vélez), manejo ambulatorio (Lazarte), elastografía esplénica (Ginesta), riesgo quirúrgico (Poniachik), GES 88 (Godoy), sarcopenia en trasplante (Wolff), hepatitis asociada al alcohol (Díaz), terapia de MASLD (Arrese), enfermedades colestásicas (Brahm).</td></tr>
<tr><td><b>Curso de Hepatología para Becados 2026</b><br><span class="small">17 y 18 de abril de 2026</span></td><td>Hemorragia en hipertensión portal (Urzúa), ascitis refractaria y síndrome hepatorrenal (Henríquez), encefalopatía hepática (Ginesta), sarcopenia y fragilidad (Benítez), ACLF (Mezzano), consulta ambulatoria del cirrótico (Arnold), Fibroscan (Cattaneo), endohepatología (Vargas), falla hepática aguda (Rivas), MASLD y fibrosis (Barrera), farmacoterapia de MASLD (Arrese), MASH sistémica (Poniachik), hepatitis B (Zapata), hepatitis C (Soza), tamizaje y eliminación de hepatitis virales (Aravena), hepatitis autoinmune (Castro), CBP (Lazarte), CEP y sus imitadores (Jiménez), trastornos metabólicos raros (Brahm), DILI (Domínguez), hepatopatías agudas del embarazo (Catalán).</td></tr>
<tr><td><b>Máster de Hepatología Clínica</b></td><td>Puntos clave de las asignaturas Cirrosis I, II y III, Enfermedad hepática metabólica, Hepatitis virales y Enfermedad hepática autoinmune.</td></tr>
<tr><td><b>Consenso ACHHEP-SOCHIDIAB</b></td><td>Esteatosis hepática en DM2 en atención primaria (Díaz y cols., Rev Med Chile 2026).</td></tr>
<tr><td><b>Curso de Hepatología Gastro Online</b></td><td>Diagnóstico de cirrosis, hemorragia variceal y su profilaxis, infecciones bacterianas, ACLF, alteración del perfil hepático (Urzúa), hepatitis aguda (Yaquich), falla hepática aguda (Norero), epidemiología de hepatitis B y C (Soza), enfermedades metabólicas (Zapata), hepatopatías autoinmunes (Brahm).</td></tr>
</tbody></table></div>
<p class="small">Generado con <code>fuentes/guia/actualizar.py</code> el {hoy}.</p>

</div>
</main>
</div>
<a class="volver" href="./">← Repositorio</a>
<script>
{js}
</script>
<style>
{pwa_css}
</style>
<div id="pwa-ui"></div>
<script>
(function(){{
  var SW="sw.js", KEY="pwa-ios-hepato", APP="Hepatología 2026";
  var standalone=window.matchMedia('(display-mode: standalone)').matches||window.navigator.standalone===true;
  if('serviceWorker' in navigator&&/^https?:$/.test(location.protocol)&&!/claude\\.ai|claudeusercontent/.test(location.hostname)){{
    window.addEventListener('load',function(){{navigator.serviceWorker.register(SW).catch(function(){{}})}});
  }}
  if(standalone)return;
  var ui=document.getElementById('pwa-ui'),dp=null;
  window.addEventListener('beforeinstallprompt',function(e){{e.preventDefault();dp=e;
    var b=document.createElement('button');b.type='button';b.textContent='Instalar '+APP;
    b.onclick=function(){{dp.prompt();dp.userChoice.finally(function(){{b.remove()}})}};ui.appendChild(b)}});
  var ios=/iphone|ipad|ipod/i.test(navigator.userAgent)&&/safari/i.test(navigator.userAgent)&&!/crios|fxios/i.test(navigator.userAgent);
  var seen=false;try{{seen=localStorage.getItem(KEY)==='1'}}catch(e){{}}
  if(ios&&!seen){{var d=document.createElement('div');d.id='pwa-ios';
    d.innerHTML='<button class="x" type="button" aria-label="Cerrar">✕</button><b>Instalar '+APP+'</b>Toca <span aria-label="Compartir">Compartir ⬆︎</span> y luego «Agregar a inicio». Funcionará sin conexión.';
    d.querySelector('.x').onclick=function(){{d.remove();try{{localStorage.setItem(KEY,'1')}}catch(e){{}}}};ui.appendChild(d)}}
}})();
</script>
</body>
</html>
"""
(RAIZ / "guia-2026.html").write_text(doc, encoding="utf-8")
print(f"guia-2026.html: {escritos}/{total} bloques, {nfc} flashcards, {npreg} preguntas, {len(doc)//1024} KB")
