#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract:  printed label  |  widget field name  |  tooltip
Save to:  widgets.csv
"""
import fitz  # PyMuPDF
import csv, os, glob

INPUT_DIR = "./bondforms10"
OUTPUT_CSV = "./csv/widgets.csv"

def best_label(widget_rect, text_blocks):
    """Return the text block most likely to be the widget's label."""
    wy0, wy1 = widget_rect.y0, widget_rect.y1
    same_line = [b for b in text_blocks
                 if abs((b["bbox"][1] + b["bbox"][3]) / 2 - (wy0 + wy1) / 2) < 5]
    left_of_widget = [b for b in same_line if b["bbox"][2] < widget_rect.x0]
    if not left_of_widget:
        return ""
    # pick the one whose right edge is closest
    label = min(left_of_widget,
               key=lambda b: widget_rect.x0 - b["bbox"][2])["text"].strip()
    return label.replace(",", " ")


def find_label(widget_rect, blocks):
    """Return the label text most likely describing widget_rect."""
    best_txt, best_metric = None, 1e9
    for rect, txt in blocks:
        if not txt:
            continue
        # same line, left
        if abs(rect.y1 - widget_rect.y0) < 12 and rect.x1 < widget_rect.x0:
            dx = widget_rect.x0 - rect.x1
            if dx < best_metric:
                best_txt, best_metric = txt, dx
        # directly above
        elif rect.y1 < widget_rect.y0 and abs(rect.x0 - widget_rect.x0) < 5:
            dy = widget_rect.y0 - rect.y1
            if dy < best_metric:
                best_txt, best_metric = txt, dy
    return best_txt  

def page_text_blocks(page):
    """Return every text line with coordinates."""
    blocks = page.get_text("dict")["blocks"]
    lines = []
    for b in blocks:
        for l in b.get("lines", []):
            txt = " ".join(s["text"] for s in l["spans"]).strip()
            if txt:
                x0, y0, x1, y1 = l["bbox"]
                lines.append({"text": txt, "bbox": (x0, y0, x1, y1)})
    return lines

rows = []
for pdf_path in glob.glob(os.path.join(INPUT_DIR, "*.pdf")):
    doc = fitz.open(pdf_path)
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text_blocks = page_text_blocks(page)

        # PyMuPDF ≥1.23: page.widgets; older: page._get_widgets()
        for w in page.widgets():
            name     = w.field_name or ""
            tooltip  = getattr(w, "field_label", "")  # empty string if missing
            label    = best_label(w.rect, text_blocks)
            rows.append([os.path.basename(pdf_path),
                         
                         name, tooltip, label])
    doc.close()

# write CSV
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["file","field_name", "tooltip", "label"])
    writer.writerows(rows)

print(f"✓ Done. {len(rows)} widgets written to {OUTPUT_CSV}")
