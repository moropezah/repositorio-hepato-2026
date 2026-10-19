# Quiz Hepatología 2026 · conexión con Google Sheets

El progreso se guarda siempre en el navegador. Para sincronizarlo entre dispositivos se usa una hoja propia, separada de la del quiz de EII:

**Hoja:** [Quiz Hepatología 2026 · Progreso](https://docs.google.com/spreadsheets/d/1jjXQ4fYkFmnXrcsOX_vUJsEZd2VfthEUTMvnIKEaQ_g/edit)

## Activar la conexión (una sola vez, ~3 minutos)

1. Abra la hoja → **Extensiones → Apps Script**.
2. Borre el contenido de `Código.gs` y pegue el de `fuentes/quiz/Code.gs`. Guarde.
3. **Implementar → Nueva implementación** → tipo **Aplicación web**.
   - Ejecutar como: **Yo**.
   - Quién tiene acceso: **Cualquier usuario**.
4. Autorice los permisos (cuenta propia) y copie la **URL de la aplicación web** (termina en `/exec`).
5. En el quiz → pestaña **Progreso** → **Conexión con Google Sheets**: pegue la URL, clave `hepato-2026` → **Guardar y reconectar**.

Para que quede fija en todos los dispositivos sin pegarla en cada uno, se escribe en `fuentes/quiz/config.json`:

```json
{"api": "https://script.google.com/macros/s/…/exec", "token": "hepato-2026"}
```

y se ejecuta `python3 fuentes/quiz/actualizar.py`.

## Qué guarda

- Hoja **estado**: el progreso completo del quiz (una fila por quiz, JSON partido en celdas de 45.000 caracteres).
- Hoja **respuestas**: una fila por respuesta (fecha, pregunta, tema, opción elegida, correcta, acierto), útil para analizar temas débiles.

Si cambia la clave, cámbiela en `Code.gs` (`TOKEN`) y en el quiz.
