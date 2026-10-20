#!/usr/bin/env python3
"""Ensambla quiz/index.html (Módulo 05) desde la plantilla y el banco de preguntas.

  fuentes/quiz/plantilla.html   · motor del quiz (estudio, examen, flashcards, progreso, temario, siglas, exportar)
  fuentes/quiz/banco/*.js       · preguntas, un archivo por grupo de bloques (const Q1..Q4 = [...])
  fuentes/quiz/config.json      · URL del Apps Script y clave (opcional; también se configura desde la app)

Valida cada pregunta con Node (ids únicos, respuesta correcta en rango, "por qué no" para cada distractor).
Uso: python3 fuentes/quiz/actualizar.py
"""
import json, pathlib, subprocess, sys

RAIZ = pathlib.Path(__file__).resolve().parents[2]
F = RAIZ / "fuentes/quiz"

TMAP = {
    "Perfil hepático y FHA": [1, "BA"], "Cirrosis y HPCS": [2, "CI"], "Hipertensión portal y HDA": [3, "CI"],
    "Ascitis, PBE y HRS-AKI": [4, "CI"], "Encefalopatía": [5, "CI"], "ACLF": [6, "CI"], "Cirrótico integral": [7, "CI"],
    "MASLD y alcohol": [8, "ET"], "Hepatitis virales": [9, "ET"], "Autoinmunes": [10, "ET"], "Metabólicas": [11, "ET"],
    "DILI": [12, "ET"], "Embarazo": [13, "ET"], "Lesiones focales y HCC": [14, "OT"], "Trasplante": [15, "OT"],
    "Imágenes y Fibroscan": [16, "OT"],
}

SIG = [
    ["AAD", "Antivirales de acción directa (VHC)"], ["ACLF", "Insuficiencia hepática aguda sobre crónica"],
    ["ACOD", "Anticoagulantes orales directos"], ["AFP", "Alfafetoproteína"], ["AMA", "Anticuerpos antimitocondriales"],
    ["ANA", "Anticuerpos antinucleares"], ["AUDC", "Ácido ursodesoxicólico"], ["BBNS", "Betabloqueador no selectivo"],
    ["BCLC", "Barcelona Clinic Liver Cancer"], ["cACLD", "Enfermedad hepática crónica avanzada compensada"],
    ["CAP", "Parámetro de atenuación controlada (esteatosis)"], ["CBP", "Colangitis biliar primaria"],
    ["CEP", "Colangitis esclerosante primaria"], ["CEUS", "Ecografía con contraste"], ["CIE", "Colestasis intrahepática del embarazo"],
    ["CLIF-C", "Chronic Liver Failure Consortium (scores ACLF y AD)"], ["DILI", "Daño hepático inducido por fármacos"],
    ["EH", "Encefalopatía hepática"], ["EUS", "Endosonografía"], ["EUS-LB", "Biopsia hepática por endosonografía"],
    ["EUS-PPG", "Gradiente de presión portal por endosonografía"], ["EVPS", "Enfermedad vascular porto-sinusoidal"],
    ["FA", "Fosfatasa alcalina"], ["FHA", "Falla hepática aguda"], ["FIB-4", "Índice de fibrosis 4"],
    ["GASA", "Gradiente de albúmina suero-ascitis"], ["GES", "Garantías Explícitas en Salud"],
    ["GPVH", "Gradiente de presión venosa hepática"], ["HAI", "Hepatitis autoinmune"], ["HCC", "Hepatocarcinoma"],
    ["HNF", "Hiperplasia nodular focal"], ["HPCS", "Hipertensión portal clínicamente significativa"],
    ["HPoP", "Hipertensión portopulmonar"], ["HRS-AKI", "Síndrome hepatorrenal con lesión renal aguda"],
    ["IQR", "Rango intercuartílico"], ["LEP", "Listado de Prestaciones Específico (GES)"], ["LFI", "Liver Frailty Index"],
    ["LI-RADS", "Liver Imaging Reporting and Data System"], ["LOLA", "L-ornitina L-aspartato"], ["LRA", "Lesión renal aguda"],
    ["LRS", "Ley Ricarte Soto"], ["LSM", "Rigidez hepática (liver stiffness measurement)"], ["LSN", "Límite superior normal"],
    ["MASH", "Esteatohepatitis asociada a disfunción metabólica"], ["MASLD", "Enfermedad hepática esteatósica asociada a disfunción metabólica"],
    ["MELD", "Model for End-stage Liver Disease"], ["MetALD", "MASLD con consumo de alcohol aumentado"],
    ["NAC", "N-acetilcisteína"], ["PAPm", "Presión arterial pulmonar media"], ["PBE", "Peritonitis bacteriana espontánea"],
    ["PEth", "Fosfatidiletanol"], ["PMN", "Polimorfonucleares"], ["RVP", "Resistencia vascular pulmonar"],
    ["RVS", "Respuesta virológica sostenida"], ["SHP", "Síndrome hepatopulmonar"], ["SSM", "Rigidez esplénica"],
    ["TACE", "Quimioembolización transarterial"], ["TARE", "Radioembolización transarterial"], ["TAF", "Tenofovir alafenamida"],
    ["TDF", "Tenofovir disoproxil fumarato"], ["TIPS", "Derivación portosistémica intrahepática transyugular"],
    ["UCI/UPC", "Unidad de paciente crítico"], ["VCTE", "Elastografía de transición (Fibroscan)"],
    ["VHB, VHC, VHD, VHE", "Virus de hepatitis B, C, D, E"],
]

VALIDA = r"""
const fs=require('fs');const files=process.argv.slice(1);let src=files.map(f=>fs.readFileSync(f,'utf8')).join('\n');
src+='\nmodule.exports=[...Q1,...Q2,...Q3,...Q4,...Q5,...Q6];';const m={exports:{}};new Function('module',src)(m);
const T=JSON.parse(process.env.TMAP);const ids=new Set();const err=[];
for(const q of m.exports){
  if(ids.has(q.id))err.push('id repetido '+q.id);ids.add(q.id);
  for(const k of ['id','b','t','n','md','q','o','c','e','w','p','r'])if(q[k]===undefined)err.push(q.id+': falta '+k);
  if(!['BA','CI','ET','OT'].includes(q.b))err.push(q.id+': bloque '+q.b);
  if(!['R','F','S'].includes(q.n))err.push(q.id+': nivel '+q.n);
  if(!['E','X'].includes(q.md))err.push(q.id+': modo '+q.md);
  if(!T[q.t])err.push(q.id+': tema desconocido '+q.t);else if(T[q.t][1]!==q.b)err.push(q.id+': grupo no coincide con el tema');
  if(!(q.c>=0&&q.c<q.o.length))err.push(q.id+': c fuera de rango');
  const wk=Object.keys(q.w).map(Number);
  if(wk.includes(q.c))err.push(q.id+': w explica la correcta');
  for(let i=0;i<q.o.length;i++)if(i!==q.c&&!wk.includes(i))err.push(q.id+': falta w['+i+']');
}
const by={};m.exports.forEach(q=>{by[q.t]=(by[q.t]||0)+1});
console.log(JSON.stringify({n:m.exports.length,err,by,E:m.exports.filter(q=>q.md==='E').length}));
"""


def main():
    banco = sorted((F / "banco").glob("*.js"))
    import os
    r = subprocess.run(["node", "-e", VALIDA, *map(str, banco)], capture_output=True, text=True,
                       env={**os.environ, "TMAP": json.dumps(TMAP, ensure_ascii=False)})
    if r.returncode:
        sys.exit(r.stderr)
    info = json.loads(r.stdout)
    if info["err"]:
        sys.exit("Errores en el banco:\n  " + "\n  ".join(info["err"]))

    cfg = {"api": "", "token": "hepato-2026"}
    if (F / "config.json").exists():
        cfg.update(json.loads((F / "config.json").read_text(encoding="utf-8")))

    html = (F / "plantilla.html").read_text(encoding="utf-8")
    datos = "\n".join(p.read_text(encoding="utf-8") for p in banco)
    html = html.replace("<!-- BANCO -->", "<script>\n" + datos + "\n</script>", 1)
    html = html.replace("__N__", str(info["n"]))
    html = html.replace("__API__", cfg["api"]).replace("__TOKEN__", cfg["token"])
    html = html.replace("__TMAP__", json.dumps(TMAP, ensure_ascii=False))
    html = html.replace("__SIG__", json.dumps(SIG, ensure_ascii=False))
    for ph in ("__N__", "__API__", "__TOKEN__", "__TMAP__", "__SIG__", "<!-- BANCO -->"):
        assert ph not in html, ph

    out = RAIZ / "quiz/index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"quiz/index.html: {info['n']} casos ({info['E']} estudio, {info['n']-info['E']} examen) · "
          f"{len(info['by'])} temas · {len(html)//1024} KB · nube: {'configurada' if cfg['api'] else 'sin configurar'}")


if __name__ == "__main__":
    main()
