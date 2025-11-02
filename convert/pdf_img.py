#!/usr/bin/env python3
# pdf_dir_to_images.py
# Convert all PDFs in a directory to images named: <filename>-pageNNN.<ext>

import argparse
import concurrent.futures as futures
import os
import sys
import fitz  # PyMuPDF
from pathlib import Path

def pdf_pages_to_png_bytes(pdf_path: Path, dpi: int):
    """Yield (page_index_1based, png_bytes) for each page in pdf_path."""
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"[SKIP-OPEN] {pdf_path}: {e}", file=sys.stderr)
        return
    if doc.needs_pass:
        print(f"[SKIP-ENCRYPTED] {pdf_path}", file=sys.stderr)
        doc.close()
        return
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    for i in range(doc.page_count):
        try:
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            png_bytes = pix.tobytes("png")
            yield (i + 1), png_bytes
        except Exception as e:
            print(f"[SKIP-PAGE] {pdf_path} page {i+1}: {e}", file=sys.stderr)
    doc.close()

def sanitize_stem(stem: str) -> str:
    # Cross-platform conservative cleanup
    bad = '<>:"/\\|?*'
    return "".join("_" if c in bad else c for c in stem).strip()

def convert_one_pdf(pdf_path: Path, out_dir: Path, dpi: int, ext: str) -> int:
    stem = sanitize_stem(pdf_path.stem)
    written = 0
    for page_idx, png_bytes in pdf_pages_to_png_bytes(pdf_path, dpi):
        out_name = f"{stem}-page{page_idx:03d}.{ext}"
        out_path = out_dir / out_name
        try:
            # Always write PNG bytes; extension is user-controlled.
            with open(out_path, "wb") as f:
                f.write(png_bytes)
            written += 1
        except Exception as e:
            print(f"[SKIP-WRITE] {out_path}: {e}", file=sys.stderr)
    if written == 0:
        print(f"[NO-OUTPUT] {pdf_path}", file=sys.stderr)
    else:
        if ext.lower() != "png":
            print(f"[NOTE] {pdf_path.name}: wrote PNG bytes with .{ext} extension", file=sys.stderr)
    return written

def find_pdfs(in_dir: Path):
    for p in sorted(in_dir.iterdir()):
        if p.is_file() and p.suffix.lower() == ".pdf":
            yield p

def main():
    ap = argparse.ArgumentParser(description="Convert all PDFs in a directory to per-page images.")
    ap.add_argument("--in", dest="in_dir", required=True, help="Input directory containing PDFs")
    ap.add_argument("--out", dest="out_dir", required=True, help="Output directory for images")
    ap.add_argument("--dpi", type=int, default=144, help="Render DPI (default: 144)")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4, help="Parallel workers per PDF (default: CPU count)")
    ap.add_argument("--ext", type=str, default="png", help="Output extension (default: png). If set to 'pgn', PNG bytes are still written.")
    args = ap.parse_args()

    in_dir = Path(args.in_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_dir.exists() or not in_dir.is_dir():
        print(f"[ERROR] Input directory not found: {in_dir}", file=sys.stderr)
        sys.exit(2)

    pdfs = list(find_pdfs(in_dir))
    if not pdfs:
        print(f"[ERROR] No PDFs found in: {in_dir}", file=sys.stderr)
        sys.exit(3)

    ext = args.ext.lstrip(".")
    dpi = max(36, args.dpi)

    # One job per PDF
    total_pages = 0
    with futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        futs = {ex.submit(convert_one_pdf, p, out_dir, dpi, ext): p for p in pdfs}
        for fut in futures.as_completed(futs):
            p = futs[fut]
            try:
                n = fut.result()
                total_pages += n
                print(f"[DONE] {p.name}: {n} pages")
            except Exception as e:
                print(f"[FAIL] {p}: {e}", file=sys.stderr)

    print(f"[SUMMARY] PDFs: {len(pdfs)} | Images written: {total_pages} | Output: {out_dir}")

if __name__ == "__main__":
    main()
