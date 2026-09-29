"""
Geometric sanity-check renderer for the .drawio files in this repo.
Not a substitute for opening them in diagrams.net -- this only parses each
mxCell's own geometry/style and draws it, to catch overlapping boxes,
off-canvas elements, or dangling edges before submission.
"""
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sys
import os

def render(path, out_path):
    tree = ET.parse(path)
    root = tree.getroot()
    cells = {}
    edges = []
    for cell in root.iter("mxCell"):
        cid = cell.get("id")
        geom = cell.find("mxGeometry")
        if cell.get("edge") == "1":
            edges.append((cell.get("source"), cell.get("target"), cell.get("value") or ""))
            continue
        if geom is None or cell.get("vertex") != "1":
            continue
        x, y = float(geom.get("x", 0)), float(geom.get("y", 0))
        w, h = float(geom.get("width", 0)), float(geom.get("height", 0))
        style = cell.get("style", "")
        fill = "#dddddd"
        if "fillColor=#" in style:
            fill = "#" + style.split("fillColor=#")[1].split(";")[0]
        valign_top = "verticalAlign=top" in style
        cells[cid] = (x, y, w, h, (cell.get("value") or "").replace("&#10;", "\n"), valign_top)

    fig, ax = plt.subplots(figsize=(16, 13))
    max_y = 0
    for cid, (x, y, w, h, label, valign_top) in cells.items():
        ax.add_patch(patches.Rectangle((x, y), w, h, linewidth=1, edgecolor="black", facecolor="#dae8fc", alpha=0.3 if valign_top else 0.6, zorder=1))
        ty_label = y + 14 if valign_top else y + h / 2
        va = "top" if valign_top else "center"
        ax.text(x + w / 2, ty_label, label, ha="center", va=va, fontsize=6, wrap=True, zorder=2)
        max_y = max(max_y, y + h)

    for src, tgt, label in edges:
        if src in cells and tgt in cells:
            sx, sy, sw, sh, _, _ = cells[src]
            tx, ty, tw, th, _, _ = cells[tgt]
            ax.annotate("", xy=(tx + tw / 2, ty + th / 2), xytext=(sx + sw / 2, sy + sh / 2),
                        arrowprops=dict(arrowstyle="->", lw=0.5, color="gray"))

    ax.set_xlim(-50, 1650)
    ax.set_ylim(max_y + 100, -50)
    ax.set_aspect("equal")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(out_path, dpi=130)
    plt.close()

    # overlap check
    ids = list(cells.keys())
    overlaps = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            x1, y1, w1, h1, _, _ = cells[ids[i]]
            x2, y2, w2, h2, _, _ = cells[ids[j]]
            if x1 < x2 + w2 and x2 < x1 + w1 and y1 < y2 + h2 and y2 < y1 + h1:
                overlaps.append((ids[i], ids[j]))
    dangling = [(s, t, l) for s, t, l in edges if s not in cells or t not in cells]
    return overlaps, dangling

if __name__ == "__main__":
    outdir = sys.argv[1] if len(sys.argv) > 1 else "."
    for name in ["context", "container", "component-read-model"]:
        src = f"diagrams/{name}.drawio"
        out = os.path.join(outdir, f"check_{name}.png")
        overlaps, dangling = render(src, out)
        print(name, "-> overlaps:", overlaps, "dangling edges:", dangling)
