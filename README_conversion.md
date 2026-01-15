# SVG to PDF/PNG Converter

This script converts SVG files to high-quality PDF and PNG formats for use in LaTeX documents.

## Installation

Install the required dependency:

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install cairosvg
```

## Usage

Convert an SVG file to PDF and PNG:

```bash
python convert_svg.py test.svg
```

Or with custom DPI for PNG:

```bash
python convert_svg.py test.svg --dpi 600
```

## Output

The script creates two files:
- `test.pdf` - Vector-based PDF (best for LaTeX, no blur)
- `test.png` - High-resolution PNG (300 DPI by default)

## For LaTeX

Use the PDF file in your LaTeX document:

```latex
\includegraphics[width=0.88\columnwidth]{test.pdf}
```

## Notes

- PDF is vector-based and will never be blurry, regardless of zoom level
- PNG is raster-based; higher DPI = better quality but larger file size
- The script preserves the original SVG filename, only changing the extension
