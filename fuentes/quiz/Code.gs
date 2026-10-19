/**
 * Quiz Hepatología 2026 · conexión con Google Sheets (Apps Script)
 * Hoja: "Quiz Hepatología 2026 · Progreso" (independiente del quiz de EII)
 *
 * GET  ?action=load&quizId=…&token=…   → {ok:true, estado:{…}|null}
 * POST {token, action:"save", quizId, estado, respuestas:[…]} → {ok:true}
 *
 * Instrucciones en INSTRUCCIONES.md (misma carpeta).
 */
const SHEET_ID = '1jjXQ4fYkFmnXrcsOX_vUJsEZd2VfthEUTMvnIKEaQ_g';
const TOKEN = 'hepato-2026';          // debe coincidir con la clave configurada en el quiz
const TROZO = 45000;                  // caracteres por celda (límite de Sheets: 50.000)

function hoja_(nombre, encabezados) {
  const ss = SpreadsheetApp.openById(SHEET_ID);
  let sh = ss.getSheetByName(nombre);
  if (!sh) {
    sh = ss.insertSheet(nombre);
    sh.appendRow(encabezados);
    sh.setFrozenRows(1);
  }
  return sh;
}

function salida_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function leerEstado_(quizId) {
  const sh = hoja_('estado', ['quizId', 'actualizado', 'json']);
  const datos = sh.getDataRange().getValues();
  for (let i = 1; i < datos.length; i++) {
    if (datos[i][0] === quizId) {
      const json = datos[i].slice(2).join('');
      return json ? JSON.parse(json) : null;
    }
  }
  return null;
}

function guardarEstado_(quizId, estado) {
  const sh = hoja_('estado', ['quizId', 'actualizado', 'json']);
  const txt = JSON.stringify(estado || {});
  const trozos = [];
  for (let i = 0; i < txt.length; i += TROZO) trozos.push(txt.slice(i, i + TROZO));
  const fila = [quizId, new Date()].concat(trozos);
  const datos = sh.getDataRange().getValues();
  let r = -1;
  for (let i = 1; i < datos.length; i++) if (datos[i][0] === quizId) { r = i + 1; break; }
  if (r < 0) { sh.appendRow(fila); return; }
  sh.getRange(r, 1, 1, Math.max(sh.getLastColumn(), fila.length)).clearContent();
  sh.getRange(r, 1, 1, fila.length).setValues([fila]);
}

function doGet(e) {
  const p = (e && e.parameter) || {};
  if (p.token !== TOKEN) return salida_({ ok: false, error: 'token inválido' });
  if (p.action === 'load') {
    try { return salida_({ ok: true, estado: leerEstado_(p.quizId || 'quizHepato_2026') }); }
    catch (err) { return salida_({ ok: false, error: String(err) }); }
  }
  return salida_({ ok: true, info: 'Quiz Hepatología 2026' });
}

function doPost(e) {
  let d = {};
  try { d = JSON.parse(e.postData.contents); } catch (err) { return salida_({ ok: false, error: 'JSON inválido' }); }
  if (d.token !== TOKEN) return salida_({ ok: false, error: 'token inválido' });
  if (d.action !== 'save') return salida_({ ok: false, error: 'acción desconocida' });
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    guardarEstado_(d.quizId || 'quizHepato_2026', d.estado);
    const rs = d.respuestas || [];
    if (rs.length) {
      const sh = hoja_('respuestas', ['fecha', 'quizId', 'preguntaId', 'tema', 'elegida', 'correcta', 'acierto']);
      sh.getRange(sh.getLastRow() + 1, 1, rs.length, 7).setValues(rs.map(r => [
        r.fecha ? new Date(r.fecha) : new Date(), d.quizId || '', r.preguntaId || '', r.tema || '',
        r.elegida === '' ? '' : r.elegida, r.correcta, String(r.elegida) === String(r.correcta) ? 1 : 0
      ]));
    }
    return salida_({ ok: true });
  } catch (err) {
    return salida_({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}
