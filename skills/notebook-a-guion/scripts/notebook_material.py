#!/usr/bin/env python3
import argparse
import base64
from collections import Counter
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ORAL_STYLE = (
    "color: #3b0700; background-color: #e6e6e6; border-left: 5px solid #8a1c0f; "
    "padding: 12px 16px; border-radius: 6px; line-height: 1.7;"
)
ORAL_RE = re.compile(r'<div\b[^>]*class="oral"[^>]*>.*?</div>', re.S)
GROUP_STYLE = (
    "background-color: #f4f6fa; border: 1px solid #cfd6e2; "
    "padding: 12px 16px; border-radius: 10px; margin: 20px 0;"
)
RESULT_MARGIN = "margin: 0 0 12px;"
BADGE_RE = re.compile(
    r'^#### <span[^>]*>(Figura|Tabla|Consola) (\d+)</span> (.+)$', re.M
)
FENCE_START = re.compile(r'^ {0,3}(' + chr(96) + r'{3,}|~{3,})(.*)$')
MIMES = {"image/png": ".png", "image/jpeg": ".jpg", "image/svg+xml": ".svg"}


def text(value):
    if isinstance(value, list):
        return "".join(value)
    return "" if value is None else str(value)


def read_utf8(path):
    return Path(path).read_bytes().decode("utf-8-sig")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_notebook(path):
    obj = json.loads(read_utf8(path))
    require(obj.get("nbformat") == 4 and isinstance(obj.get("cells"), list),
            "Se requiere un notebook Jupyter de formato 4.")
    return obj


def image_items(notebook):
    for ci, cell in enumerate(notebook["cells"], 1):
        for oi, output in enumerate(cell.get("outputs", []), 1):
            for mime, value in output.get("data", {}).items():
                if mime not in MIMES:
                    continue
                raw = text(value)
                if mime == "image/svg+xml":
                    content = raw.encode("utf-8")
                else:
                    content = base64.b64decode("".join(raw.split()), validate=True)
                yield ci, oi, mime, content


class Tables(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.current = None
        self.row = None
        self.cell = None
        self.tables = []

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.depth += 1
            if self.depth == 1:
                self.current = {"rows": [], "complex": False}
            elif self.current:
                self.current["complex"] = True
        elif self.depth == 1 and tag == "tr":
            self.row = []
        elif self.depth == 1 and tag in ("td", "th") and self.row is not None:
            attrs = dict(attrs)
            if attrs.get("colspan", "1") != "1" or attrs.get("rowspan", "1") != "1":
                self.current["complex"] = True
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.depth == 1 and self.cell is not None:
            self.row.append("".join(self.cell).strip())
            self.cell = None
        elif tag == "tr" and self.depth == 1 and self.row is not None:
            self.current["rows"].append(self.row)
            self.row = None
        elif tag == "table":
            if self.depth == 1 and self.current is not None:
                self.tables.append(self.current)
                self.current = None
            self.depth = max(0, self.depth - 1)


def normalized_table(table):
    rows = table["rows"]
    if table["complex"] or not rows:
        return None
    header, body = rows[0].copy(), rows[1:]
    if body and body[0] and body[0][0] and all(not v for v in body[0][1:]):
        header[0], body = body[0][0], body[1:]
    if any(len(row) != len(header) for row in body):
        return None
    return [header] + body


def table_markdown(rows):
    def line(row):
        return "| " + " | ".join(v.replace("|", r"\|").replace("\n", " ") for v in row) + " |"
    return "\n".join([line(rows[0]), line(["---"] * len(rows[0]))]
                     + [line(row) for row in rows[1:]])


def parse_tables(value):
    parser = Tables()
    parser.feed(text(value))
    result = []
    for table in parser.tables:
        rows = normalized_table(table)
        result.append({
            "rows": table["rows"],
            "complex": rows is None,
            "normalized_rows": rows,
            "markdown": table_markdown(rows) if rows else None,
        })
    return result


def extract(notebook_path, assets_dir, manifest_path):
    notebook_path = Path(notebook_path).resolve()
    assets_dir = Path(assets_dir).resolve()
    manifest_path = Path(manifest_path).resolve()
    require(manifest_path != notebook_path, "El manifiesto no puede reemplazar el notebook.")
    before = notebook_path.read_bytes()
    notebook = load_notebook(notebook_path)
    assets_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", notebook_path.stem).strip("-")[:48] or "notebook"
    extracted = {}
    for ci, oi, mime, raw in image_items(notebook):
        digest = hashlib.sha256(raw).hexdigest()
        name = f"{slug}-c{ci:03d}-o{oi:03d}-{digest[:12]}{MIMES[mime]}"
        target = assets_dir / name
        if target.exists():
            require(target.read_bytes() == raw, f"Conflicto de imagen existente: {target}")
        else:
            target.write_bytes(raw)
        extracted[(ci, oi, mime)] = {
            "mime": mime, "path": str(target), "filename": name, "sha256": digest
        }
    heading_path = {}
    cells = []
    for ci, cell in enumerate(notebook["cells"], 1):
        source = text(cell.get("source", ""))
        if cell["cell_type"] == "markdown":
            in_fence = False
            for line in source.splitlines():
                if FENCE_START.match(line):
                    in_fence = not in_fence
                if not in_fence:
                    match = re.match(r"^(#{1,6})\s+(.+)$", line)
                    if match:
                        level = len(match.group(1))
                        heading_path = {k: v for k, v in heading_path.items() if k < level}
                        heading_path[level] = match.group(2).strip()
        record = {
            "position": ci, "id": cell.get("id"), "type": cell["cell_type"],
            "source": source,
            "heading_path": [heading_path[k] for k in sorted(heading_path)],
            "execution_count": cell.get("execution_count"), "outputs": []
        }
        for oi, output in enumerate(cell.get("outputs", []), 1):
            item = {"position": oi, "type": output.get("output_type")}
            if output.get("output_type") == "stream":
                item.update(name=output.get("name"), text=text(output.get("text")))
            if output.get("output_type") == "error":
                item.update(ename=output.get("ename"), evalue=output.get("evalue"),
                            traceback=output.get("traceback"))
            data = output.get("data", {})
            item["mime_types"] = list(data)
            for mime, field in [("text/plain", "text_plain"), ("text/markdown", "text_markdown")]:
                if mime in data:
                    item[field] = text(data[mime])
            if "text/html" in data:
                item["html"] = text(data["text/html"])
                item["tables"] = parse_tables(data["text/html"])
            item["images"] = [value for (c, o, _), value in extracted.items() if c == ci and o == oi]
            record["outputs"].append(item)
        cells.append(record)
    manifest = {
        "notebook": str(notebook_path), "sha256": hashlib.sha256(before).hexdigest(),
        "cells": cells, "images": list(extracted.values())
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    require(notebook_path.read_bytes() == before, "El notebook cambió durante la extracción.")
    return manifest


def fences_and_structure(document):
    plain_lines, fences = [], []
    active, body, language = None, [], ""
    for line in document.replace("\r\n", "\n").splitlines():
        match = FENCE_START.match(line)
        if active is None and match:
            active, language, body = match.group(1), match.group(2).strip(), []
            plain_lines.append("")
        elif active is not None:
            if re.fullmatch(re.escape(active[0]) + "{" + str(len(active)) + r",}\s*", line.strip()):
                fences.append((language, "\n".join(body)))
                active, body = None, []
            else:
                body.append(line)
            plain_lines.append("")
        else:
            plain_lines.append(line)
    require(active is None, "Hay un bloque de código sin cerrar.")
    return "\n".join(plain_lines), fences


class DivCheck(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.counts = Counter()
        self.groups = 0
        self.groups_without_reading = 0
        self.group_state = None

    def handle_starttag(self, tag, attrs):
        if tag != "div":
            return
        attrs = dict(attrs)
        style = attrs.get("style", "")
        if attrs.get("class") == "oral":
            role = "oral"
        elif "background-color: #f4f6fa" in style:
            role = "group"
        elif re.search(r"border-left:\s*4px solid", style):
            role = "result"
        elif "dashed" in style:
            role = "reference"
        else:
            role = "other"

        if role == "group":
            require(not self.stack, "Un grupo de resultado está anidado indebidamente.")
            require(GROUP_STYLE in style, "El grupo de resultado no usa el estilo predeterminado.")
            self.stack.append("group")
            self.group_state = {"result": False, "oral": False}
            self.groups += 1
        elif role == "result":
            require(self.stack == ["group"], "Cada resultado debe estar dentro de su propio grupo.")
            require(not self.group_state["result"], "Un grupo contiene más de un resultado.")
            require(RESULT_MARGIN in style, "El resultado debe usar margin: 0 0 12px;.")
            self.stack.append("result")
            self.group_state["result"] = True
        elif role == "oral":
            if self.stack:
                require(self.stack == ["group"],
                        "Un bloque oral dentro de un grupo debe ser su lectura.")
                require(self.group_state["result"],
                        "La lectura del grupo debe ir después del resultado.")
                require(not self.group_state["oral"],
                        "Un grupo contiene más de una lectura.")
                self.group_state["oral"] = True
            self.stack.append("oral")
        elif role == "reference":
            require(self.stack and self.stack[-1] == "result",
                    "Una caja de referencia quedó fuera del resultado.")
            self.stack.append("reference")
        else:
            require(not self.stack, "Hay un div no reconocido dentro de un grupo de resultado.")
            self.stack.append("other")
        self.counts[role] += 1

    def handle_endtag(self, tag):
        if tag == "div":
            require(bool(self.stack), "Hay un cierre div sin apertura.")
            role = self.stack.pop()
            if role == "group":
                require(self.group_state["result"], "Un grupo no contiene ningún resultado.")
                if not self.group_state["oral"]:
                    self.groups_without_reading += 1
                self.group_state = None


def markdown_tables(structure):
    groups = re.findall(r"^\|.*(?:\n\|.*)*", structure, re.M)
    result = []
    for group in groups:
        rows = []
        for line in group.splitlines():
            cells = re.split(r"(?<!\\)\|", line.strip())[1:-1]
            cells = [unescape(v.strip().replace(r"\|", "|")) for v in cells]
            if cells and all(re.fullmatch(r":?-{3,}:?", v) for v in cells):
                continue
            rows.append(cells)
        if rows:
            result.append(rows)
    return result


def header_projections(wanted, original, start=0, selected=()):
    if not wanted:
        yield selected
    else:
        for index in range(start, len(original)):
            if wanted[0] == original[index]:
                yield from header_projections(wanted[1:], original, index + 1, selected + (index,))


def table_is_selection(document_rows, original_rows):
    for indices in header_projections(document_rows[0], original_rows[0]):
        projected = [[row[i] for i in indices] for row in original_rows[1:]]
        cursor = 0
        for row in document_rows[1:]:
            while cursor < len(projected) and projected[cursor] != row:
                cursor += 1
            if cursor == len(projected):
                break
            cursor += 1
        else:
            return True
    return False


def validate(guide_path, notebook_path=None, preserve_from=None, allow_custom_style=False):
    guide_path = Path(guide_path).resolve()
    document = read_utf8(guide_path)
    oral = ORAL_RE.findall(document)
    require(bool(oral), "No se encontraron bloques de lectura.")
    preserved = 0
    if preserve_from:
        previous = ORAL_RE.findall(read_utf8(preserve_from))
        require(bool(previous), "El guion anterior no contiene bloques orales.")
        require(Counter(oral) == Counter(previous),
                "Se modificó, eliminó o duplicó un bloque oral protegido.")
        preserved = len(previous)
    if not allow_custom_style and not preserve_from:
        expected = '<div class="oral" style="' + ORAL_STYLE + '">'
        require(all(block.startswith(expected) for block in oral),
                "Un bloque oral no utiliza el estilo predeterminado.")
    structure, fences = fences_and_structure(document)
    checker = DivCheck()
    checker.feed(structure)
    checker.close()
    require(not checker.stack, "Hay div sin cerrar.")
    require(checker.groups == checker.counts["result"],
            "Cada resultado debe tener su propio grupo.")
    blank_check = ORAL_RE.sub("", structure) if preserve_from else structure
    lines = blank_check.splitlines()
    for i, line in enumerate(lines):
        if re.fullmatch(r"<div\b[^>]*>", line.strip()):
            require(i + 1 < len(lines) and not lines[i + 1].strip(),
                    "Falta una línea en blanco después de un div.")
        if line.strip() == "</div>":
            require(i > 0 and not lines[i - 1].strip(),
                    "Falta una línea en blanco antes de un cierre div.")
    structural = ORAL_RE.sub("", structure)
    badges = BADGE_RE.findall(structural)
    require(len(badges) == checker.counts["result"] == checker.counts["reference"],
            "Los encabezados, contenedores y referencias no coinciden.")
    cells = re.findall(r"^### (\d+\.\d+)\s+.+$", structural, re.M)
    require(len(cells) == len(set(cells)), "Hay identificadores de celda duplicados.")
    current, counters, references = None, Counter(), []
    for line in structural.splitlines():
        cell = re.match(r"^### (\d+\.\d+)\s+", line)
        badge = BADGE_RE.fullmatch(line)
        if cell:
            current, counters = cell.group(1), Counter()
        if badge:
            require(current is not None, "Resultado sin título de celda.")
            kind, number, _ = badge.groups()
            counters[kind] += 1
            require(int(number) == counters[kind], "Numeración por tipo incorrecta.")
        if line.startswith("Mostrar:"):
            match = re.search(r"\bcelda (\d+\.\d+)\.\s*$", line)
            require(match is not None and match.group(1) == current,
                    "Una referencia no corresponde a su celda.")
            references.append(line)
    require(len(references) == len(badges), "Falta una referencia por resultado.")
    sections = list(re.finditer(r"^## .+$", structural, re.M))
    for i, section in enumerate(sections):
        require(structural[:section.start()].rstrip().endswith("---"),
                "Falta un separador antes de un bloque.")
        end = sections[i + 1].start() if i + 1 < len(sections) else len(structural)
        body = structural[section.end():end]
        count = re.findall(
            r"(\d+) celdas? · (\d+) figuras? · (\d+) tablas? · (\d+) consolas?", body
        )
        require(len(count) == 1, "Falta el conteo del bloque o está duplicado.")
        actual = Counter(kind for kind, _, _ in BADGE_RE.findall(body))
        expected = (len(re.findall(r"^### ", body, re.M)), actual["Figura"],
                    actual["Tabla"], actual["Consola"])
        require(tuple(map(int, count[0])) == expected, "Conteo de bloque incorrecto.")
    images = re.findall(r"!\[([^\]]*)\]\((?:<([^>]+)>|([^)\n]+))\)", structure)
    require(len(images) == sum(kind == "Figura" for kind, _, _ in badges),
            "No coincide el número de figuras e imágenes.")
    notebook = load_notebook(notebook_path) if notebook_path else None
    original_images = {hashlib.sha256(raw).hexdigest()
                       for _, _, _, raw in image_items(notebook)} if notebook else set()
    for alt, angle_path, bare_path in images:
        target = angle_path or bare_path
        url = urlsplit(target)
        path = Path(unquote(url.path))
        require(not url.scheme and not url.netloc and not path.is_absolute() and not path.drive,
                "Las imágenes deben usar rutas relativas.")
        require(not re.search(r"figura original|\bcelda\s+\d", alt, re.I),
                "El texto alternativo debe contener solo el nombre de la figura.")
        asset = guide_path.parent / path
        require(asset.is_file(), f"No existe la imagen: {asset}")
        if notebook:
            require(hashlib.sha256(asset.read_bytes()).hexdigest() in original_images,
                    f"La imagen no coincide con una original guardada: {asset.name}")
    verified_tables = 0
    if notebook:
        streams, original_tables = [], []
        for cell in notebook["cells"]:
            for output in cell.get("outputs", []):
                if output.get("output_type") == "stream":
                    streams.append(text(output.get("text")))
                data = output.get("data", {})
                if "text/plain" in data:
                    streams.append(text(data["text/plain"]))
                if "text/html" in data:
                    original_tables.extend(table["normalized_rows"]
                                           for table in parse_tables(data["text/html"])
                                           if table["normalized_rows"])
        for language, content in fences:
            if language in ("text", "console", "plaintext"):
                wanted = [line for line in content.splitlines() if line]
                require(any(all(line in original.splitlines() for line in wanted)
                            for original in streams),
                        "Un fragmento de consola no coincide con una salida guardada.")
        for table in markdown_tables(structural):
            require(any(table_is_selection(table, candidate) for candidate in original_tables),
                    "Una tabla no es una selección literal de una tabla original simple.")
            verified_tables += 1
    main = document.split("## Preguntas posibles del profesor")[0]
    spoken = " ".join(re.sub(r"<[^>]+>", "", block) for block in ORAL_RE.findall(main))
    return {
        "ok": True, "file": str(guide_path), "oral_blocks": len(oral),
        "protected_blocks_identical": preserved, "cells": len(cells),
        "figures": len(images), "tables_verified": verified_tables,
        "results": len(badges), "groups": checker.groups,
        "groups_without_reading": checker.groups_without_reading,
        "consoles": sum(k == "Consola" for k, _, _ in badges),
        "spoken_words": len(unescape(spoken).split()),
        "notebook_provenance_checked": notebook is not None,
        "div_balanced": True
    }


def main():
    parser = argparse.ArgumentParser(description="Extraer evidencia y comprobar guiones de notebooks.")
    sub = parser.add_subparsers(dest="command", required=True)
    ex = sub.add_parser("extract")
    ex.add_argument("notebook")
    ex.add_argument("--assets-dir", required=True)
    ex.add_argument("--manifest", required=True)
    val = sub.add_parser("validate")
    val.add_argument("guide")
    val.add_argument("--notebook")
    val.add_argument("--preserve-from")
    val.add_argument("--allow-custom-style", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "extract":
            manifest = extract(args.notebook, args.assets_dir, args.manifest)
            report = {
                "ok": True, "manifest": str(Path(args.manifest).resolve()),
                "cells": len(manifest["cells"]), "images": len(manifest["images"]),
                "saved_outputs": sum(len(c["outputs"]) for c in manifest["cells"])
            }
        else:
            report = validate(args.guide, args.notebook, args.preserve_from, args.allow_custom_style)
        print(json.dumps(report, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
