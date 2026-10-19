# Repositorio Hepatología 2026

Material de estudio de hepatología para postgrado de gastroenterología, con el marco chileno (GES 88, Ley Ricarte Soto) declarado donde cambia la conducta.

**Autor:** Dr. Moisés Oropeza — Médico Internista, Residente de Gastroenterología, Universidad de los Andes (Clínica Dávila / Clínica Universidad de los Andes). Santiago de Chile, octubre 2026. Uso personal de estudio.

## Contenido

| Módulo | Qué es | Estado |
|---|---|---|
| 01 | **Guía de estudio Hepatología 2026** — 16 bloques. Cada uno abre con "qué cambió" frente a la guía previa, trae algoritmos con fármaco, dosis y criterio de falla, marcadores (idea clave, error frecuente, Chile) y cierra con caso clínico, flashcards y preguntas con corrección razonada. | 16 / 16 bloques escritos |
| 02 | **Consulta rápida** — umbrales y conductas para el paciente delante. | En preparación |
| 03 | **Vademécum hepatológico** — mecanismo, dosis, ajuste por Child-Pugh y función renal, criterio de falla y cobertura en Chile verificada contra los decretos vigentes. | En preparación |
| 04 | **Calculadoras** — Child-Pugh, MELD, MELD-Na, MELD 3.0, CLIF-C ACLF, Maddrey, Lille, HAI simplificado, FIB-4, ANTICIPATE, Liver Frailty Index, VOCAL-Penn, BCLC, Milán, Metroticket y otras, validadas con casos de prueba. | En preparación |
| 05 | **Quiz Hepatología** — banco propio de casos clínicos con flashcards y progreso en Google Sheets (Sheet propio, independiente del de EII). | En preparación |

### Bloques de la guía

1. **Perfil hepático alterado, hepatitis aguda y falla hepática aguda**
2. **Cirrosis: diagnóstico, cACLD, HPCS y recompensación**
3. **Hipertensión portal: várices, hemorragia, TIPS y trombosis portal**
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
index.html          · portada del repositorio (#inicio, #fuentes)
guia-2026.html      · módulo 01, GENERADO por fuentes/guia/actualizar.py — no editar a mano
manifest.webmanifest, sw.js, icons/   · app instalable (funciona sin conexión)
fuentes/guia/
  bloques.json      · orden, grupos y estado de los 16 bloques
  bloques/bNN_*.html· un archivo por bloque (empieza con <h2 id="bN">)
  estilos.css, extra.css, pwa.css, guia.js · diseño y comportamiento (heredados del repositorio EII)
  actualizar.py     · ensambla guia-2026.html
.nojekyll           · evita el procesamiento Jekyll en GitHub Pages
```

## Cómo actualizar

| Cambio | Dónde | Luego |
|---|---|---|
| Escribir o corregir un bloque | `fuentes/guia/bloques/bNN_*.html` (y `"archivo"` en `bloques.json` si es nuevo) | `python3 fuentes/guia/actualizar.py` |
| Portada | `index.html` | — |
| Nueva versión de la app | subir la versión de `CACHE` en `sw.js` solo si cambia la lista de archivos | — |

Cada bloque declara sus preguntas en `<script type="application/json" class="qz-data" data-b="bN">` y su contenedor `<div class="qz" data-b="bN"></div>`; el motor de `guia.js` las pinta y corrige.

Reglas: antes de subir, `git pull --rebase origin main`; agregar solo los archivos del módulo que cambió.

## Fuentes

Curso de Cirrosis y Trasplante Hepático, Clínica Dávila (31 de julio y 1 de agosto de 2026) · Curso de Hepatología para Becados 2026 (17 y 18 de abril de 2026) · Máster de Hepatología Clínica · Curso de Hepatología Gastro Online · Baveno VIII (J Hepatol 2026;85:993–1018) y guías EASL, AASLD, ACG, AGA e ISTH vigentes, citadas al final de cada bloque.
