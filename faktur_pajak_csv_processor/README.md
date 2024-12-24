# Faktur Pajak CSV Processor

A simple web application to process CSV files according to specific formatting requirements for Faktur Pajak documents.

## Features

- Adds double quotes around all fields
- Changes date format to DD/MM/YYYY
- Removes dots from faktur numbers
- Adds "0" for empty numeric fields
- Uses empty quoted strings ("") for empty text fields
- Rounds down JUMLAH_DPP and JUMLAH_PPN values for FK rows

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# On Windows
venv\Scripts\activate
```

3. Install requirements:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Click the "Choose File" button and select your CSV file
2. Click "Process CSV" to upload and process the file
3. The processed file will be automatically downloaded with a timestamp in the filename

## Note

Temporary files are stored in the `temp` directory and are served for download immediately after processing.
