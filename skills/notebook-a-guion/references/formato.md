# Formato de entrega

Aplica este formato por defecto; las preferencias explícitas del usuario tienen prioridad. Conserva íntegros los bloques orales protegidos.

## Documento y bloques

Conserva un título principal e incluye esta leyenda:

    **Indicaciones de lectura:** El bloque gris con franja roja se dice en voz alta. Las etiquetas azul (figura), verde (tabla) y pizarra (consola) marcan los resultados que se muestran. La caja punteada indica qué mostrar y no se lee.

Antes de cada bloque ## coloca una regla horizontal. Debajo presenta los conteos reales:

    ---

    ## 1. Carga y exploración

    <div style="color:#555; font-size:0.9em; margin:-8px 0 16px;">

    3 celdas · 2 figuras · 2 tablas · 2 consolas

    </div>

Cuenta los grupos ### como celdas y los elementos incluidos como resultados. Una figura con varios paneles cuenta como una figura. Usa singular cuando corresponda. Una sección de preguntas sin celdas ni resultados lleva conteos cero.

## Celda y lectura

Los títulos ### usan el número y nombre visibles del notebook. Si no existen, utiliza etiquetas N.M y una referencia reconocible al código o encabezado original.

    ### 1.2 Balance de diagnósticos

    <div class="oral" style="color: #3b0700; background-color: #e6e6e6; border-left: 5px solid #8a1c0f; padding: 12px 16px; border-radius: 6px; line-height: 1.7;">

    Texto que se dice en voz alta.

    </div>

No uses «Guion:», micrófonos ni citas con sangría. Escribe párrafos breves y naturales. Las respuestas a preguntas pueden utilizar el mismo estilo.

## Grupo de resultado

Cada resultado se agrupa con el guion que lo interpreta dentro de un contenedor exterior. El guion que introduce la celda o presenta el resultado queda fuera y encima del grupo, a ancho completo:

    <div class="oral" style="color: #3b0700; background-color: #e6e6e6; border-left: 5px solid #8a1c0f; padding: 12px 16px; border-radius: 6px; line-height: 1.7;">

    Guion que introduce o presenta el resultado.

    </div>

    <div style="background-color: #f4f6fa; border: 1px solid #cfd6e2; padding: 12px 16px; border-radius: 10px; margin: 20px 0;">

    <div style="border-left: 4px solid #2f6fb5; padding: 4px 0 4px 16px; margin: 0 0 12px;">

    #### <span style="background:#2f6fb5; color:#fff; padding:2px 10px; border-radius:4px; font-size:0.8em;">Figura 1</span> Nombre de la figura

    <div style="border: 1px dashed #999; color: #555; padding: 6px 12px; border-radius: 6px; font-size: 0.9em;">

    Mostrar: la figura «Nombre de la figura» de la celda 1.2.

    </div>

    ![Nombre de la figura](guion_assets/nombre.png)

    </div>

    <div class="oral" style="color: #3b0700; background-color: #e6e6e6; border-left: 5px solid #8a1c0f; padding: 12px 16px; border-radius: 6px; line-height: 1.7;">

    Interpretación oral de este resultado.

    </div>

    </div>

Dentro del grupo va solo el resultado y la lectura que lo interpreta. Reglas:

- Un grupo por resultado. Si una celda tiene varios resultados, cada uno lleva su propio grupo con su lectura.
- El contenedor del resultado usa `margin: 0 0 12px;` para dejar un espacio uniforme con la lectura.
- Si una lectura interpreta dos resultados a la vez, colócala dentro del grupo del último e informa de esa decisión en la respuesta.
- No cambies el texto de las lecturas al moverlas: solo cambia su posición dentro o fuera del grupo.

Orden de lectura: guion fuera (introduce) → resultado dentro del grupo → guion dentro del grupo (interpreta).

| Tipo | Color del borde y etiqueta |
| --- | --- |
| Figura | #2f6fb5 |
| Tabla | #2e8b57 |
| Consola | #475569 |

Para Tabla y Consola sustituye el tipo, el color y el contenido. Usa tablas Markdown fieles a las salidas guardadas y cercas de código con lenguaje text para consola o transcripciones.

Numera por tipo y reinicia en cada celda: Consola 1, Figura 1, Tabla 1, Tabla 2. Conserva los nombres de los resultados cuando reestructures un guion.

Las imágenes usan rutas relativas y texto alternativo corto con el nombre de la figura, sin «figura original» ni número de celda.

## Separación

- Deja una línea en blanco después de cada div de apertura y antes de cada cierre.
- Cierra el contenedor del resultado antes de su lectura y el grupo exterior después de la lectura. Solo las introducciones y las respuestas a preguntas quedan fuera de los grupos.
- La caja punteada identifica el resultado inmediato y la celda N.M.
- Las aclaraciones sobre recortes no se leen. El guion interpreta el resultado completo que se muestra en el notebook.
- Retira tiempos estimados y encabezados auxiliares sin función, e informa de lo retirado.
- Si una lectura está mal ubicada, mueve el bloque completo; no cambies palabras de texto protegido.
