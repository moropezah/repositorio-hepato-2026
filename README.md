# Repositorio Hepatología 2026

Material de estudio de hepatología para postgrado de gastroenterología, con el marco chileno (GES 88, Ley Ricarte Soto) declarado donde cambia la conducta.

**Autor:** Dr. Moisés Oropeza — Médico Internista, Residente de Gastroenterología, Universidad de los Andes (Clínica Dávila / Clínica Universidad de los Andes). Santiago de Chile, octubre 2026. Uso personal de estudio.

## Contenido

| Módulo | Qué es | Estado |
|---|---|---|
| 01 | **Guía de estudio Hepatología 2026** — 16 bloques. Cada uno abre con "qué cambió" frente a la guía previa, trae algoritmos con fármaco, dosis y criterio de falla, marcadores (idea clave, error frecuente, Chile) y cierra con caso clínico, flashcards y preguntas con corrección razonada. | 16 / 16 bloques escritos |
| 02 | **Consulta rápida** — 19 tarjetas con buscador: HPCS (Baveno VIII), hemorragia variceal, enfermedad vascular hepática (trombosis portal, Budd-Chiari, PSVD), ascitis, PBE, HRS-AKI, encefalopatía, ACLF, hepatitis alcohólica, FHA, DILI, VHB, VHC, BCLC, trasplante, GES 88, MASLD, autoinmunes y embarazo. En `index.html#rapida`. | Escrito |
| 03 | **Vademécum hepatológico** — 77 fármacos en 13 grupos: mecanismo, indicación, dosis, ajustes, monitoreo y criterio de falla, efectos adversos y cobertura en Chile (canasta GES 88 según la Res. Exenta 1452, GES 68 y 69, Ley Ricarte Soto, sin registro). Filtros por grupo y cobertura. En `index.html#vademecum`. | Escrito |
| 04 | **Calculadoras** — 26: Child-Pugh, MELD / MELD-Na / MELD 3.0, ALBI, cACLD y HPCS con ANTICIPATE / ANTICIPATE-NASH (Baveno VIII), riesgo quirúrgico (con enlace a VOCAL-Penn), Liver Frailty Index, puntaje PSVD/NCPF y anticoagulación en trombosis portal no cirrótica (Baveno VIII), ACLF (grado y CLIF-C), CLIF-C AD, LRA (ICA-ADQI), líquido ascítico, Maddrey, Lille, GAHS, ABIC, FIB-4, APRI, NFS, HAI simplificado, respuesta al AUDC, Leipzig, factor R y ley de Hy, King's College, BCLC con criterios de trasplante (Milán, UCSF, up-to-seven, Metroticket 2.0, AFP francés), PAGE-B. Cada una con ficha (qué mide, cuándo usarla, limitaciones), escala completa con la fila del paciente marcada, ejemplos por categoría (Child A/B/C, ACLF 0–3…) y clasificación de uso (rutina / situacional / referencia) resumida en `calc/#curaduria`. En `calc/`. | Escrito |
| 05 | **Quiz Hepatología** — 240 casos propios (15 por bloque; 117 de estudio, 123 de examen; 80 de nivel fellow y 46 staff) con explicación, por qué no las otras, perla y referencias; examen cronometrado, flashcards, progreso por tema, temario enlazado a la guía, siglas y exportación (HTML, CSV, Anki, JSON, PDF). Sincroniza con el Sheet propio «Quiz Hepatología 2026 · Progreso» vía Apps Script (`fuentes/quiz/Code.gs`, ver `INSTRUCCIONES.md`). En `quiz/`. | Escrito |

### Bloques de la guía

1. **Perfil hepático alterado, hepatitis aguda y falla hepática aguda**
2. **Cirrosis: diagnóstico, cACLD, HPCS y recompensación**
3. **Hipertensión portal: várices, hemorragia, TIPS y enfermedad vascular hepática** (trombosis portal, Budd-Chiari, PSVD/NCPF)
4. **Ascitis, PBE, HRS-AKI e hiponatremia**
5. **Encefalopatía hepática**
6. **ACLF: insuficiencia hepática aguda sobre crónica**
7. **El cirrótico integral: hemostasia, nutrición, consulta (GES 88) y cirugía**
8. **MASLD/MASH y enfermedad hepática por alcohol**
9. **Hepatitis virales B, C, D y E**
10. **Enfermedades autoinmunes: HAI, CBP, CEP, IgG4**
11. **Enfermedades metabólicas: Wilson, hemocromatosis, A1AT**
12. **DILI y hepatotoxicidad por hierbas**
13. **Hígado y embarazo**
14. **Lesiones focales, hepatocarcinoma y colangiocarcinoma**
15. **Trasplante hepático**
16. **Imágenes, Fibroscan y endohepatología**

## Estructura de archivos

```
index.html          · portada (#inicio), consulta rápida (#rapida), vademécum (#vademecum), fuentes (#fuentes)
calc/index.html     · módulo 04, calculadoras (autocontenido; se edita directamente)
quiz/index.html     · módulo 05, GENERADO por fuentes/quiz/actualizar.py — no editar a mano
guia-2026.html      · módulo 01, GENERADO por fuentes/guia/actualizar.py — no editar a mano
manifest.webmanifest, sw.js, icons/   · app instalable (funciona sin conexión)
fuentes/guia/
  bloques.json      · orden, grupos y estado de los 16 bloques
  bloques/bNN_*.html· un archivo por bloque (empieza con <h2 id="bN">)
  estilos.css, extra.css, pwa.css, guia.js · diseño y comportamiento (heredados del repositorio EII)
  actualizar.py     · ensambla guia-2026.html
fuentes/rapida/rapida.html      · contenido del módulo 02
fuentes/vademecum/farmacos.json · datos del módulo 03 (grupos, códigos de cobertura, fármacos)
fuentes/repositorio/actualizar.py · inserta 02 y 03 en index.html entre sus marcas
fuentes/quiz/plantilla.html     · motor del quiz (derivado del Quiz EII)
fuentes/quiz/banco/*.js         · preguntas (Q1–Q6: cuatro archivos por grupos de bloques y dos de ampliación)
fuentes/quiz/actualizar.py      · valida el banco con Node y genera quiz/index.html
fuentes/quiz/Code.gs, INSTRUCCIONES.md · conexión con Google Sheets
.nojekyll           · evita el procesamiento Jekyll en GitHub Pages
```

## Cómo actualizar

| Cambio | Dónde | Luego |
|---|---|---|
| Escribir o corregir un bloque | `fuentes/guia/bloques/bNN_*.html` (y `"archivo"` en `bloques.json` si es nuevo) | `python3 fuentes/guia/actualizar.py` |
| Consulta rápida o vademécum | `fuentes/rapida/rapida.html` o `fuentes/vademecum/farmacos.json` | `python3 fuentes/repositorio/actualizar.py` |
| Calculadoras | `calc/index.html` (arreglos `CALCS` y `META`: ficha, escala, ejemplos y uso) | — |
| Preguntas del quiz | `fuentes/quiz/banco/*.js` | `python3 fuentes/quiz/actualizar.py` |
| Portada | `index.html` (fuera de las marcas RAPIDA y VADEMECUM) | — |
| Nueva versión de la app | subir la versión de `CACHE` en `sw.js` solo si cambia la lista de archivos | — |

Cada bloque declara sus preguntas en `<script type="application/json" class="qz-data" data-b="bN">` y su contenedor `<div class="qz" data-b="bN"></div>`; el motor de `guia.js` las pinta y corrige.

Reglas: antes de subir, `git pull --rebase origin main`; agregar solo los archivos del módulo que cambió.

## Fuentes

Curso de Cirrosis y Trasplante Hepático, Clínica Dávila (31 de julio y 1 de agosto de 2026) · Curso de Hepatología para Becados 2026 (17 y 18 de abril de 2026) · Máster de Hepatología Clínica · Curso de Hepatología Gastro Online · Baveno VIII (J Hepatol 2026;85:993–1018) y guías EASL, AASLD, ACG, AGA e ISTH vigentes, citadas al final de cada bloque.
