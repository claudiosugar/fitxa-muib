from flask import Flask, send_file, request, jsonify, render_template
from fitxa_muib_downloader import download_pdf
import logging
import os
import tempfile
import uuid

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download-pdf', methods=['POST'])
@app.route('/download-pdf/<referencia_catastral>', methods=['GET'])
def download_pdf_endpoint(referencia_catastral=None):
    try:
        # Handle GET request with path parameter
        if request.method == 'GET' and referencia_catastral:
            logger.info("Received GET download request", extra={"referencia": referencia_catastral})
        # Handle POST request with JSON body
        else:
            data = request.get_json()
            if not data or 'referencia_catastral' not in data:
                logger.warning("POST download request missing referencia_catastral")
                return jsonify({'error': 'Missing referencia_catastral parameter'}), 400
            referencia_catastral = data['referencia_catastral']
            logger.info("Received POST download request", extra={"referencia": referencia_catastral})
        
        # Create a temporary file with a unique name
        temp_dir = tempfile.gettempdir()
        temp_filename = f"{uuid.uuid4()}.pdf"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        # Download the PDF
        download_pdf(referencia_catastral, temp_path)
        
        # Send the file and then delete it
        response = send_file(
            temp_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{referencia_catastral}.pdf"
        )
        
        # Delete the temporary file after sending
        @response.call_on_close
        def cleanup():
            try:
                os.remove(temp_path)
                logger.info("Cleaned up temporary file", extra={"temp_path": temp_path})
            except Exception as e:
                logger.error("Error deleting temporary file", extra={"temp_path": temp_path, "error": str(e)})
        
        logger.info("PDF ready for download", extra={"referencia": referencia_catastral})
        return response

    except Exception as e:
        logger.exception("Download request failed", extra={"referencia": referencia_catastral})
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 