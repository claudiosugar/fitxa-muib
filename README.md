# FITXA MUIB Downloader

A web service that automates the download of property information sheets (fitxes) from the MUIB (Mapa Urbanístic de les Illes Balears) system.

## Features

- Web interface for easy access
- RESTful API endpoint for programmatic access
- Automated browser interaction using Playwright
- Deployable to fly.io with production-ready configuration
- Automatic scaling and memory management

## Live Demo

The application is deployed and available at: https://fitxa-muib.fly.dev

## Usage

### Web Interface

1. Visit https://fitxa-muib.fly.dev
2. Enter your referencia catastral in the input field
3. Click "Download PDF"
4. Wait for the PDF to be generated and downloaded

### API Endpoint

You can also use the REST API endpoint directly:

```bash
# Using curl
curl -X POST https://fitxa-muib.fly.dev/download-pdf \
  -H "Content-Type: application/json" \
  -d '{"referencia_catastral": "7805508DD6870F"}' \
  --output output.pdf

# Using path parameter
curl https://fitxa-muib.fly.dev/download-pdf/7805508DD6870F \
  --output output.pdf
```

## Local Development

### Prerequisites

- Python 3.11+
- pip
- Google Chrome or Chromium

### Installation

1. Clone the repository:
```bash
git clone https://github.com/claudiosugar/fitxa-muib.git
cd fitxa-muib
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
playwright install-deps
```

4. Run the development server:
```bash
python app.py
```

The application will be available at http://localhost:5000

## Deployment

The application is configured for deployment on fly.io.

1. Install the Fly CLI:
```bash
curl -L https://fly.io/install.sh | sh
```

2. Login to Fly:
```bash
fly auth login
```

3. Deploy the application:
```bash
fly deploy
```

## Configuration

The application uses the following configuration:

- `fly.toml`: Fly.io deployment configuration
  - 2GB RAM allocation
  - Madrid region for optimal latency
  - Auto-scaling enabled
  
- `Dockerfile`: Container configuration
  - Python 3.11 slim base image
  - Playwright and Chrome dependencies
  - Gunicorn with optimized settings
    - 300 second timeout
    - 2 workers
    - 2 threads per worker

## Technical Details

- **Framework**: Flask
- **Browser Automation**: Playwright
- **Production Server**: Gunicorn
- **Deployment**: fly.io
- **Container**: Docker

## License

MIT License

## Author

Claudio Sugar 