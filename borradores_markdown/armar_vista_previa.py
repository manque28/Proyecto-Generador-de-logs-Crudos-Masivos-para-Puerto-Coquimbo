"""Arma vista_previa.ipynb: copia del notebook original con las celdas Markdown de los
borradores insertadas en su lugar. El original no se modifica.

Cada bloque de los .md parte con un marcador
    <!-- ===== CELDA 1.2 · TIPO · antes de Hito 1.3 ===== -->
y se inserta antes de la celda de codigo cuya primera linea es "# Hito 1.3: ...".
Si un hito se repite, las celdas siguientes se nombran con sufijo b, c, ... (Hito 6.3b, Hito 6.3c).

Los bloques de INTERPRETACION y CONCLUSIONES no se insertan: esas celdas las genera el propio
notebook con celdas de codigo "# Interpretacion X.Y (CELDA X.Y): ..." que arman el texto con los
valores de cada corrida. En los .md quedan solo como copia de la ejecucion de referencia; si se
insertaran, cada interpretacion apareceria dos veces, una con numeros fijos y otra con los reales.

Uso: python armar_vista_previa.py <carpeta de borradores> <notebook> [salida]
Sin salida, escribe <carpeta>/vista_previa.ipynb.
"""
import glob
import json
import os
import re
import sys

carpeta, ruta_original = sys.argv[1], sys.argv[2]
salida = sys.argv[3] if len(sys.argv) > 3 else os.path.join(carpeta, "vista_previa.ipynb")

nb = json.load(open(ruta_original, encoding="utf-8"))

# etiqueta de cada celda de codigo -> indice
indice = {}
for i, celda in enumerate(nb["cells"]):
    primera = "".join(celda["source"]).split("\n", 1)[0]
    m = re.match(r"#\s*(Hito [\d.]+|Cierre)\s*:", primera)
    if not m:
        continue
    base = etiqueta = m.group(1).rstrip(".")
    sufijos = iter("bcdefgh")
    while etiqueta in indice:
        etiqueta = base + next(sufijos)
    indice[etiqueta] = i

# celdas que el notebook ya genera con codigo: "# Interpretacion 1.2 (CELDA 1.2): ..."
dinamicas = set()
for celda in nb["cells"]:
    m = re.match(r"#\s*Interpretacion\s+\S+\s+\(CELDA ([\d.]+[a-z]?)\)", "".join(celda["source"]))
    if celda["cell_type"] == "code" and m:
        dinamicas.add(m.group(1))

# bloques markdown agrupados por la celda de codigo a la que anteceden
por_destino = {}
total = 0
for ruta in sorted(glob.glob(os.path.join(carpeta, "[0-9][0-9]_*.md"))):
    texto = open(ruta, encoding="utf-8").read()
    for bloque in re.split(r"(?m)^(?=<!-- ===== CELDA)", texto):
        bloque = bloque.strip()
        if not bloque:
            continue
        m = re.match(r"<!-- ===== CELDA ([\d.]+[a-z]?) ·.*?· antes de (.+?) =====", bloque)
        if not m:
            sys.exit(f"marcador sin destino en {os.path.basename(ruta)}: {bloque[:70]}")
        if m.group(1) in dinamicas:
            print(f"  CELDA {m.group(1):<4} omitida: la genera una celda de codigo con los valores de la corrida")
            continue
        destino = m.group(2).strip()
        if destino not in indice:
            sys.exit(f"CELDA {m.group(1)}: no existe la celda de codigo '{destino}'")
        por_destino.setdefault(indice[destino], []).append((m.group(1), bloque))
        total += 1

celdas = []
for i, celda in enumerate(nb["cells"]):
    for numero, bloque in por_destino.get(i, []):
        celdas.append({"cell_type": "markdown", "metadata": {}, "source": bloque.splitlines(keepends=True)})
        print(f"  CELDA {numero:<4} -> antes de [{i:>2}] {''.join(celda['source']).split(chr(10), 1)[0][:60]}")
    # el markdown que ya traiga el original lo reemplazan los borradores, salvo el de las celdas
    # que no se insertan (por ejemplo el titulo de Conclusiones, que acompana a la celda 9.1)
    marca = re.match(r"<!-- ===== CELDA ([\d.]+[a-z]?) ·", "".join(celda["source"]))
    if celda["cell_type"] == "markdown" and not (marca and marca.group(1) in dinamicas):
        print(f"  omitida markdown original [{i:>2}] {''.join(celda['source']).split(chr(10), 1)[0][:60]}")
        continue
    celdas.append(celda)

nb["cells"] = celdas
with open(salida, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
n_md = sum(c["cell_type"] == "markdown" for c in celdas)
print(f"{total} celdas markdown insertadas, {n_md - total} conservadas del original, "
      f"{len(celdas) - n_md} de codigo -> {salida}")
