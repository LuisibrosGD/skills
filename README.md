# skills

Colección de skills para agentes de IA: OpenCode, Claude Code, Codex, Cursor y cualquier
otro cliente compatible con [Agent Skills](https://agentskills.io).

## Instalación

Requiere Node.js 22.20 o superior.

```bash
# Todas las skills, en todos los agentes detectados, sin preguntas
npx skills add LuisibrosGD/skills -s '*' -a '*' -y

# A nivel global (disponible en todos tus proyectos)
npx skills add LuisibrosGD/skills -s '*' -a '*' -y -g

# Solo una skill
npx skills add LuisibrosGD/skills -s notebook-a-guion -a '*' -y
```

Sin flags, el CLI pregunta interactivamente qué skills instalar y en qué agentes.

```bash
# Ver qué skills incluye el repositorio antes de instalar
npx skills add LuisibrosGD/skills --list

# Ver lo instalado / buscar actualizaciones
npx skills list
npx skills check
```

Por defecto la instalación es a nivel de proyecto (`.agents/skills/` y el directorio
equivalente de cada agente). Añade `-g` para instalarla globalmente.

## Skills incluidas

| Skill | Descripción |
| --- | --- |
| `notebook-a-guion` | Convierte un notebook Jupyter (`.ipynb`) en un guion oral en Markdown, con figuras, tablas y resultados guardados, interpretación en español sencillo y bloques de lectura diferenciados. |

### `notebook-a-guion`

Úsala para exponer un notebook: toma el `.ipynb` y produce un guion de 10–12 minutos
(≈1.400–1.550 palabras) más una carpeta `guion_assets` con las imágenes originales.
No ejecuta ni modifica el análisis salvo petición expresa.

```text
@notebook-a-guion  conviérteme laboratorio.ipynb en un guion de 12 minutos
```

Requiere Python 3.10+ (el helper usa solo la biblioteca estándar). En macOS/Linux usa
`python3` en lugar de `python`.

## Estructura

```text
skills/
└── notebook-a-guion/
    ├── SKILL.md
    ├── references/
    │   └── formato.md
    └── scripts/
        └── notebook_material.py
```

## Añadir una skill nueva

```bash
npx skills init mi-skill-nueva        # crea la plantilla
```

Muévela a `skills/mi-skill-nueva/` y súbela. El CLI descubre hasta tres niveles bajo
`skills/`, así que `skills/<nombre>/SKILL.md` y `skills/<categoria>/<nombre>/SKILL.md`
funcionan igual.

## Licencia

[MIT](LICENSE)
