#!/usr/bin/env python3
"""
Convert SVG to PDF using headless browser (handles foreignObject text properly).
"""

import argparse
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False


def convert_with_playwright(input_path: Path, pdf_path: Path):
    """Convert SVG to PDF using Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Read SVG content
        svg_content = input_path.read_text(encoding='utf-8')
        
        # Extract SVG dimensions
        import re
        width_match = re.search(r'width="(\d+)px"', svg_content)
        height_match = re.search(r'height="(\d+)px"', svg_content)
        viewbox_match = re.search(r'viewBox="[^"]*"', svg_content)
        
        svg_width = width_match.group(1) if width_match else '800'
        svg_height = height_match.group(1) if height_match else '600'
        
        # Create HTML wrapper with proper sizing
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
        
        page.set_content(html_content, wait_until='networkidle')
        # Use SVG dimensions for PDF page size
        page.pdf(
            path=str(pdf_path),
            width=f'{int(svg_width) + 40}px',
            height=f'{int(svg_height) + 40}px',
            print_background=True,
            margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
        )
        browser.close()


def convert_with_selenium(input_path: Path, pdf_path: Path):
    """Convert SVG to PDF using Selenium."""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Read SVG content
        svg_content = input_path.read_text(encoding='utf-8')
        
        # Create HTML wrapper
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                }}
                svg {{
                    max-width: 100%;
                    height: auto;
                }}
            </style>
        </head>
        <body>
            {svg_content}
        </body>
        </html>
        """
        
        # Save to temp HTML file
        temp_html = input_path.with_suffix('.temp.html')
        temp_html.write_text(html_content, encoding='utf-8')
        
        driver.get(f'file:///{temp_html.absolute()}')
        # Note: Selenium doesn't have direct PDF export, would need Chrome DevTools Protocol
        # For now, suggest using Playwright instead
        print("Selenium method requires additional setup. Please use Playwright method.")
        temp_html.unlink()
        
    finally:
        driver.quit()


def convert_svg(input_path: str):
    """Convert SVG to PDF using available method."""
    in_path = Path(input_path)
    
    if not in_path.exists():
        print(f"Error: Input SVG file not found: {in_path}")
        sys.exit(1)
    
    if not in_path.suffix.lower() == '.svg':
        print(f"Error: Input file must be a .svg file: {in_path}")
        sys.exit(1)
    
    pdf_path = in_path.with_suffix('.pdf')
    
    if HAS_PLAYWRIGHT:
        try:
            print(f"Converting {in_path.name} to PDF using Playwright...")
            convert_with_playwright(in_path, pdf_path)
            if pdf_path.exists():
                print(f"[OK] Created: {pdf_path}")
                print(f"\nFor LaTeX, use: \\includegraphics[width=0.88\\columnwidth]{{{pdf_path.name}}}")
            else:
                print("Error: PDF file was not created")
                sys.exit(1)
        except Exception as e:
            print(f"Error during conversion: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("Error: Playwright not installed.")
        print("Please install it using: pip install playwright")
        print("Then run: playwright install chromium")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert SVG to PDF using headless browser (handles foreignObject text).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python convert_svg_browser.py test.svg
  
Note: Requires Playwright. Install with:
  pip install playwright
  playwright install chromium
        """
    )
    parser.add_argument(
        "svg",
        help="Path to input SVG file"
    )
    
    args = parser.parse_args()
    convert_svg(args.svg)
