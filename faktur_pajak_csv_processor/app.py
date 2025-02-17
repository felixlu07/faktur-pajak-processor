from flask import Flask, request, send_file, render_template
import pandas as pd
from datetime import datetime
import os
import math

app = Flask(__name__)

# Expected header for the CSV file
EXPECTED_HEADER = ["FK", "KD_JENIS_TRANSAKSI", "FG_PENGGANTI", "NOMOR_FAKTUR", "MASA_PAJAK", 
                  "TAHUN_PAJAK", "TANGGAL_FAKTUR", "NPWP", "NAMA", "ALAMAT_LENGKAP", 
                  "JUMLAH_DPP", "JUMLAH_PPN", "JUMLAH_PPNBM", "ID_KETERANGAN_TAMBAHAN",
                  "FG_UANG_MUKA", "UANG_MUKA_DPP", "UANG_MUKA_PPN", "UANG_MUKA_PPNBM",
                  "REFERENSI", "KODE_DOKUMEN_PENDUKUNG"]

def process_csv(df):
    try:
        # Find the correct header row
        header_row_idx = -1
        for idx, row in df.iterrows():
            if row[0] == "FK" and row[1] == "KD_JENIS_TRANSAKSI":
                header_row_idx = idx
                break
        
        if header_row_idx >= 0:
            # Get the data starting from the header row
            df = df.iloc[header_row_idx:].reset_index(drop=True)
            
            # Set the first row as headers
            df.columns = df.iloc[0]
            df = df.iloc[1:].reset_index(drop=True)
        
        # Add double quotes around all fields (pandas will handle this during to_csv)
        
        # Process only rows where first column is "FK"
        mask = df.iloc[:, 0] == "FK"
        
        # For FK rows, round down JUMLAH_DPP and JUMLAH_PPN
        df.loc[mask, 'JUMLAH_DPP'] = df.loc[mask, 'JUMLAH_DPP'].apply(lambda x: math.floor(float(x)) if pd.notnull(x) else "0")
        df.loc[mask, 'JUMLAH_PPN'] = df.loc[mask, 'JUMLAH_PPN'].apply(lambda x: math.floor(float(x)) if pd.notnull(x) else "0")
        
        # Replace empty numeric fields with "0"
        numeric_columns = ['JUMLAH_DPP', 'JUMLAH_PPN', 'JUMLAH_PPNBM', 'FG_UANG_MUKA', 'UANG_MUKA_DPP', 'UANG_MUKA_PPN', 'UANG_MUKA_PPNBM']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].fillna("0")
        
        # Replace empty text fields with empty quoted strings
        text_columns = df.select_dtypes(include=['object']).columns
        for col in text_columns:
            if col not in numeric_columns:
                df[col] = df[col].fillna("")
        
        # Convert date format for FK rows
        def convert_date(date_str):
            if pd.isna(date_str) or date_str == "":
                return ""
            try:
                # Try parsing different date formats
                for fmt in ['%d-%m-%y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y']:
                    try:
                        date_obj = datetime.strptime(str(date_str), fmt)
                        return date_obj.strftime('%d/%m/%Y')
                    except ValueError:
                        continue
                return date_str
            except:
                return date_str

        if 'TANGGAL_FAKTUR' in df.columns:
            df.loc[mask, 'TANGGAL_FAKTUR'] = df.loc[mask, 'TANGGAL_FAKTUR'].apply(convert_date)
        
        # Remove dots from faktur number for FK rows
        if 'NOMOR_FAKTUR' in df.columns:
            df.loc[mask, 'NOMOR_FAKTUR'] = df.loc[mask, 'NOMOR_FAKTUR'].str.replace('.', '')
        
        return df
    except Exception as e:
        print(f"Error processing CSV: {str(e)}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400
        
    if not file.filename.endswith('.csv'):
        return 'Please upload a CSV file', 400
    
    try:
        # Read the CSV file
        df = pd.read_csv(file, dtype=str)
        
        # Process the CSV
        processed_df = process_csv(df)
        
        # Create output filename with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename_without_ext = os.path.splitext(file.filename)[0]
        output_filename = f"{filename_without_ext}_{timestamp}.csv"
        
        # Save to temporary file
        temp_path = os.path.join(os.path.dirname(__file__), 'temp', output_filename)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        processed_df.to_csv(temp_path, index=False, quoting=1)  # quoting=1 means quote all fields
        
        # Send the file
        return send_file(temp_path, 
                        mimetype='text/csv',
                        as_attachment=True,
                        download_name=output_filename)
    except Exception as e:
        print(f"Error: {str(e)}")
        return f'Error processing file: {str(e)}', 500

if __name__ == '__main__':
    # Create temp directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), 'temp'), exist_ok=True)
    # Use environment variable for port if available (for production)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
