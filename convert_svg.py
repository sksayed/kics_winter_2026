#!/usr/bin/env python3
"""
Convert SVG to PDF and high-resolution PNG for LaTeX documents.
Uses browser-based conversion for best text rendering (handles foreignObject).
"""

import argparse
import sys
import re
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

try:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF
    HAS_SVGLIB_PDF = True
except ImportError:
    HAS_SVGLIB_PDF = False

try:
    from reportlab.graphics import renderPM
    HAS_RENDERPM = True
except (ImportError, OSError):
    HAS_RENDERPM = False

try:
    import cairosvg
    HAS_CAIROSVG = True
except (ImportError, OSError):
    HAS_CAIROSVG = False


def convert_svg(input_path: str, dpi: int = 300):
    """
    Convert SVG file to PDF and high-resolution PNG.
    
    Args:
        input_path: Path to input SVG file
        dpi: Resolution for PNG output (default: 300)
    """
    in_path = Path(input_path)
    
    if not in_path.exists():
        print(f"Error: Input SVG file not found: {in_path}")
        sys.exit(1)
    
    if not in_path.suffix.lower() == '.svg':
        print(f"Error: Input file must be a .svg file: {in_path}")
        sys.exit(1)
    
    # Output paths (same name, different extensions)
    pdf_path = in_path.with_suffix('.pdf')
    png_path = in_path.with_suffix('.png')
    
    try:
        pdf_created = False
        png_created = False
        
        # Try browser-based conversion first (best for foreignObject text)
        if HAS_PLAYWRIGHT:
            try:
                print(f"Converting {in_path.name} to PDF using Playwright (handles text properly)...")
                svg_content = in_path.read_text(encoding='utf-8')
                
                # Extract SVG dimensions
                width_match = re.search(r'width="(\d+)px"', svg_content)
                height_match = re.search(r'height="(\d+)px"', svg_content)
                svg_width = width_match.group(1) if width_match else '800'
                svg_height = height_match.group(1) if height_match else '600'
                
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{
                            margin: 0;
                            padding: 20px;
                            background: white;
                        }}
                        svg {{
                            display: block;
                            margin: 0 auto;
                        }}
                    </style>
                </head>
                <body>
                    {svg_content}
                </body>
                </html>
                """
                
                with sync_playwright() as p:
                    browser = p.chromium.launch()
                    page = browser.new_page()
                    page.set_content(html_content, wait_until='networkidle')
                    page.pdf(
                        path=str(pdf_path),
                        width=f'{int(svg_width) + 40}px',
                        height=f'{int(svg_height) + 40}px',
                        print_background=True,
                        margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
                    )
                    browser.close()
                
                if pdf_path.exists():
                    print(f"[OK] Created: {pdf_path}")
                    pdf_created = True
                else:
                    print("Warning: PDF file was not created")
            except Exception as e:
                print(f"Warning: Playwright PDF conversion failed: {e}")
        
        # Fallback to svglib if browser method failed
        if not pdf_created and HAS_SVGLIB_PDF:
            try:
                print(f"Converting {in_path.name} to PDF using svglib...")
                drawing = svg2rlg(str(in_path))
                if drawing:
                    renderPDF.drawToFile(drawing, str(pdf_path))
                    if pdf_path.exists():
                        print(f"[OK] Created: {pdf_path}")
                        pdf_created = True
                    else:
                        print("Warning: PDF file was not created")
                else:
                    print("Warning: Could not parse SVG file with svglib")
            except Exception as e:
                print(f"Warning: svglib PDF conversion failed: {e}")
        
        if not pdf_created and HAS_CAIROSVG:
            try:
                print(f"Converting {in_path.name} to PDF using cairosvg...")
                cairosvg.svg2pdf(url=str(in_path), write_to=str(pdf_path))
                print(f"✓ Created: {pdf_path}")
                pdf_created = True
            except Exception as e:
                print(f"Warning: cairosvg PDF conversion failed: {e}")
        
        # Try PNG conversion
        if HAS_RENDERPM:
            try:
                print(f"Converting {in_path.name} to PNG (DPI: {dpi})...")
                drawing = svg2rlg(str(in_path))
                if drawing:
                    renderPM.drawToFile(drawing, str(png_path), fmt='PNG', dpi=dpi)
                    if png_path.exists():
                        print(f"[OK] Created: {png_path}")
                        png_created = True
                    else:
                        print("Warning: PNG file was not created")
            except Exception as e:
                print(f"Warning: PNG conversion failed: {e}")
        
        if HAS_CAIROSVG and not png_created:
            try:
                print(f"Converting {in_path.name} to PNG (DPI: {dpi}) using cairosvg...")
                cairosvg.svg2png(url=str(in_path), write_to=str(png_path), dpi=dpi)
                if png_path.exists():
                    print(f"[OK] Created: {png_path}")
                    png_created = True
                else:
                    print("Warning: PNG file was not created")
            except Exception as e:
                print(f"Warning: PNG conversion failed: {e}")
        
        if not pdf_created:
            print("\nError: Could not convert to PDF. Please install:")
            print("  pip install svglib reportlab")
            sys.exit(1)
        
        print("\nConversion completed successfully!")
        if pdf_created:
            print(f"\nFor LaTeX, use: \\includegraphics[width=0.88\\columnwidth]{{{pdf_path.name}}}")
        if not png_created:
            print("\nNote: PNG conversion skipped (Cairo library not available). PDF is sufficient for LaTeX.")
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert SVG to PDF and high-resolution PNG for LaTeX documents.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python convert_svg.py test.svg
  python convert_svg.py test.svg --dpi 600
  python convert_svg.py test.drawio.svg
        """
    )
    parser.add_argument(
        "svg",
        help="Path to input SVG file (e.g., test.svg or test.drawio.svg)"
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="PNG resolution in DPI (default: 300, higher = better quality but larger file)"
    )
    
    args = parser.parse_args()
    convert_svg(args.svg, dpi=args.dpi)
