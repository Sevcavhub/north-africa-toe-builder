# OCR Setup Guide for Scanned PDFs

This guide helps you set up OCR (Optical Character Recognition) to extract text from scanned/image-based PDF files.

## Why OCR is Needed

Some PDFs (like scanned books) don't have embedded text - they're just images of pages. Regular PDF text extraction tools can't read these. OCR uses computer vision to recognize and extract text from images.

## Installation Steps

### 1. Install Tesseract OCR

Tesseract is the OCR engine that reads text from images.

#### Windows:
1. Download the installer: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (choose default options)
3. **Important**: Note the installation path (usually `C:\Program Files\Tesseract-OCR`)
4. Add Tesseract to your PATH, or set it in Python:
   ```python
   import pytesseract
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### macOS:
```bash
brew install tesseract
```

### 2. Install Poppler (PDF to Image Converter)

Poppler converts PDF pages to images so Tesseract can read them.

#### Windows:
1. Download from: https://github.com/oschwartz10612/poppler-windows/releases
2. Extract to a folder (e.g., `C:\poppler`)
3. Add `C:\poppler\Library\bin` to your PATH

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get install poppler-utils
```

#### macOS:
```bash
brew install poppler
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `pytesseract` - Python wrapper for Tesseract
- `pdf2image` - Converts PDF pages to images
- `Pillow` - Image processing library

## Usage

### Basic Usage
Extract entire PDF in 10-page chunks:
```bash
npm run ocr:pdf -- "path/to/scanned.pdf"
```

### Custom Chunk Size
Extract in 5-page chunks (smaller = less memory, more frequent saves):
```bash
npm run ocr:pdf -- "path/to/scanned.pdf" --chunk-size 5
```

### Extract Specific Pages
Extract only pages 1-20:
```bash
npm run ocr:pdf -- "path/to/scanned.pdf" --pages 1-20 --chunk-size 10
```

### Example: Desert Rats PDF
```bash
npm run ocr:pdf -- "Resource Documents\British_PRIMARY_SOURCES\682349763-Battle-Orders-028-Desert-Rats-British-8th-Army-in-North-Africa-1941-43.pdf" --pages 1-20 --chunk-size 5
```

## Output

Extracted text files are saved to: `data/output/pdf_extracts/`

Files are named: `{pdf_name}_pages_{start}-{end}.txt`

Example:
- `682349763-Battle-Orders-028-Desert-Rats_pages_1-5.txt`
- `682349763-Battle-Orders-028-Desert-Rats_pages_6-10.txt`

## Performance Notes

- **DPI Setting**: Currently set to 200 DPI (balance between quality and speed)
  - Higher DPI (300) = better accuracy, slower, more memory
  - Lower DPI (150) = faster, less accurate

- **Chunk Size**:
  - Smaller chunks (5 pages) = less memory, more frequent progress updates
  - Larger chunks (20 pages) = faster overall, but uses more memory

- **Speed**: Expect ~5-15 seconds per page depending on your CPU

## Troubleshooting

### "TesseractNotFoundError"
- Tesseract not installed or not in PATH
- **Fix**: Install Tesseract and add to PATH, or set path in Python code

### "PDFInfoNotInstalledError"
- Poppler not installed or not in PATH
- **Fix**: Install Poppler and add `Library/bin` to PATH

### "Out of Memory" Errors
- Chunk size too large
- **Fix**: Use smaller `--chunk-size` (try 5 or even 3)

### Poor OCR Accuracy
- Low image quality in PDF
- **Fix**: Increase DPI in script (edit line `dpi=200` to `dpi=300`)

## Comparison: Regular PDF vs OCR

### Use `extract:pdf` (Node.js) for:
- PDFs with embedded text
- Modern digital PDFs
- Files that work with copy/paste

### Use `ocr:pdf` (Python) for:
- Scanned documents
- Image-based PDFs
- Files where `extract:pdf` returns "[No text content found]"

## Advanced Configuration

Edit `scripts/ocr_pdf_chunks.py` to customize:

```python
# Line ~88: Adjust DPI for quality/speed tradeoff
images = convert_from_path(
    pdf_path,
    dpi=300  # Change from 200 to 300 for better accuracy
)

# Line ~96: Add OCR configuration
page_text = pytesseract.image_to_string(
    image,
    lang='eng',  # Change to 'deu' for German, 'fra' for French, etc.
    config='--psm 6'  # Page segmentation mode
)
```

### Available PSM Modes:
- `--psm 6` - Uniform block of text (default, good for documents)
- `--psm 3` - Fully automatic (slower but more accurate)
- `--psm 11` - Sparse text (good for tables)

## Language Support

Tesseract supports 100+ languages. For historical military documents in other languages:

```bash
# Download additional language data
# Windows: Place in C:\Program Files\Tesseract-OCR\tessdata
# Linux: sudo apt-get install tesseract-ocr-deu tesseract-ocr-fra

# Then modify script to use:
page_text = pytesseract.image_to_string(image, lang='deu')  # German
page_text = pytesseract.image_to_string(image, lang='fra')  # French
page_text = pytesseract.image_to_string(image, lang='ita')  # Italian
```
