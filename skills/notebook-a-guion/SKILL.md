---
name: notebook-a-guion
description: Genera o reestructura guiones orales en Markdown a partir de notebooks Jupyter (.ipynb), con figuras y resultados guardados, interpretación sencilla y bloques de lectura diferenciados. Úsala para exponer un notebook; no para ejecutar o modificar el análisis salvo petición expresa.
---

# Guion oral desde notebook

Convierte el notebook proporcionado en un guion que siga sus bloques y muestre qué resultados pertenecen a cada celda. Lee [references/formato.md](references/formato.md) para reproducir la jerarquía y los estilos aprobados.

## Entrada y entrega

- Recibe un .ipynb y, opcionalmente, un guion previo, idioma, duración y destino.
- Por defecto: español sencillo, tercera persona y objetivo de 10–12 minutos, aproximadamente 1.400–1.550 palabras orales. Adapta la extensión al material sin añadir relleno ni tiempos estimados dentro del archivo.
- Entrega Markdown y una carpeta guion_assets. Nombre predeterminado: guion_<nombre-del-notebook>.md en la carpeta solicitada o el espacio de trabajo. Si existe y no se pidió actualizarlo, elige el siguiente sufijo _v2, _v3, etc.
- No generes un HTML independiente; el Markdown contiene los div y estilos aprobados.
- Adapta los bloques al notebook real. No impongas el dataset, las técnicas ni las cifras del laboratorio de ejemplo.

## Evidencia del notebook

1. Inspecciona código, encabezados y salidas guardadas. No ejecutes celdas ni instales paquetes por defecto. Un execution_count nulo no invalida una salida guardada.
2. Extrae material con el helper, cuya ruta es relativa a esta skill:

       python3 scripts/notebook_material.py extract <notebook.ipynb> --assets-dir <carpeta/guion_assets> --manifest <ruta-temporal/evidencia.json>

   Usa `python3` en macOS y Linux; en Windows, `python`. Requiere Python 3.10 o superior y ninguna dependencia externa.

   El manifiesto incluye código, encabezados, consola, tablas e imágenes extraídas. Consulta las partes relevantes y elimina los temporales de la tarea antes de entregar.
3. Conserva las figuras completas: no recortes, recolorees ni regeneres sus imágenes. Inspecciónalas cuando la interpretación dependa de su forma. Si una misma salida ofrece varias representaciones de imagen, elige una original (preferentemente PNG), sin duplicar la figura por sus formatos. Los nombres con huella de contenido evitan sustituir imágenes de guiones anteriores.
4. Copia los valores guardados de tablas y consola. En tablas grandes suelen bastar 3–5 filas y columnas pertinentes; conserva completas las pequeñas. No recalcules métricas ni cambies su presentación numérica. El equivalente porcentual de una métrica puede explicarse oralmente con redondeo coherente.
5. Evita advertencias técnicas, descripciones Markdown y mensajes redundantes como texto de exposición. Selecciona resultados que aporten a lo que se explica.
6. Si faltan resultados, explica el código y señala la ausencia en la referencia correspondiente; no inventes cifras ni atribuyas resultados. Para gráficos interactivos sin imagen estática guardada, indica esa limitación y no fabriques una figura sustitutiva. La ejecución o exportación adicional requiere petición del usuario.

## Organización y lectura

- Conserva los títulos visibles del notebook, incluidos número y nombre cuando existan. Si faltan títulos individuales, da al grupo un nombre descriptivo y cita un encabezado o inicio de código reconocible. No dependas exclusivamente de posiciones ocultas ni contadores de ejecución.
- No modifiques el notebook de entrada. Si se pide sincronizar títulos, cambia solo esa presentación y conserva código y salidas.
- Orden: bloque y conteos reales; celda; guion que introduce; grupo con el resultado y su lectura; repite el grupo por cada resultado de la celda.
- Numera Figura, Tabla y Consola por separado, reiniciando en cada celda. Cuenta los elementos incluidos; los paneles de una misma imagen no son figuras separadas.
- Los párrafos para pronunciar van en div class="oral". La introducción de la celda o la presentación de un resultado queda fuera y encima del grupo; la lectura que interpreta ese resultado va dentro del grupo, después del resultado. Los rótulos y las cajas de referencia no se leen.
- Evita repetir las definiciones que ya ve el público. Usa «En esta tabla…», «Aquí se observa…» y «Al comparar…» para interpretar valores y conectar ideas.
- Incluye introducción, conclusión sustentada en resultados y, por defecto, cinco preguntas con respuestas breves fuera del tiempo de exposición. Adapta la conclusión al objetivo real del notebook.
- Propón transiciones fuera del archivo solo si el usuario las solicita.

## Guion previo y texto protegido

Si se pide conservar los div orales, captura cada bloque completo antes de editar. Reubícalo íntegro sin cambiar palabras, entidades HTML, espacios, CRLF/LF ni estilos. No dividas, fusiones o dupliques el texto para forzar el formato. Reporta rótulos eliminados y correcciones de numeración. El nuevo estilo se aplica al exterior salvo autorización para cambiar el bloque protegido. Al agrupar, reubica cada lectura íntegra después de su resultado: el agrupamiento no autoriza a cambiar su texto.

## Comprobación y respuesta

Ejecuta:

    python3 scripts/notebook_material.py validate <guion.md> --notebook <notebook.ipynb>

Para texto protegido añade --preserve-from <guion-anterior.md>. Si el usuario pidió otro estilo, añade --allow-custom-style y verifica sus valores manualmente.

El helper comprueba div, grupos de resultado, anidamiento y orden resultado→lectura, conteos, numeración, referencias, rutas relativas, imágenes originales, fragmentos de consola y selecciones de tablas simples. Revisa aparte las salidas complejas que necesiten HTML o texto plano. Confirma además que los títulos y las interpretaciones correspondan a sus resultados; la validación estructural no equivale a ejecutar el análisis.

Entrega un enlace al Markdown y las comprobaciones relevantes. Señala resultados ausentes, confirma cuántos bloques protegidos quedaron idénticos e informa cualquier cambio fuera del encargo.
