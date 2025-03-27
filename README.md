# MUIB PDF Downloader

A Python script to automatically download PDF files from the MUIB (Mapa Urbanístic d'Informació Bàsica) website using a referencia catastral.

## Features

- Automatically navigates to the MUIB website
- Handles layer checkboxes and panel expansion
- Searches for a specific referencia catastral
- Clicks on the result to center the map
- Downloads the PDF file

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/fitxa-muib.git
cd fitxa-muib
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install
```

## Usage

Run the script with a referencia catastral as an argument:

```bash
python pdf_downloader.py <referencia_catastral>
```

Example:
```bash
python pdf_downloader.py 7805508DD6870F
```

The script will:
1. Open a browser window
2. Navigate to the MUIB website
3. Configure the layers
4. Search for the provided referencia catastral
5. Download the PDF file
6. Save it as `<referencia_catastral>.pdf` in the current directory

## Requirements

- Python 3.7 or higher
- Playwright
- Internet connection

## License

MIT License 