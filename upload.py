from flask import Flask, request, jsonify, render_template, send_file
import os
import pandas as pd
import matplotlib.pyplot as plt
from app import main  # Import your main function from the correct module

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'  # Directory to store uploaded files
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    """Serve the home page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    print("Upload endpoint hit")  # Debug line
    if 'file' not in request.files:
        print("No file uploaded")  # Debug line
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        print("No selected file")  # Debug line
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.endswith('.csv'):
        print("File must be a CSV")  # Debug line
        return jsonify({'error': 'File must be a CSV'}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    print(f"File saved to {file_path}")  # Debug line

    try:
        # Call your main function to process the file
        segmented_data = main(file_path)  # Ensure this function returns a DataFrame with expected columns
        result = segmented_data.to_json(orient='records')  # Convert DataFrame to JSON format
        print("Data processed successfully")  # Debug line
        return jsonify(result)
    except Exception as e:
        print(f"Error processing file: {str(e)}")  # Debug line
        return jsonify({'error': str(e)}), 500  # Return the error message

@app.route('/recency_plot')
def get_recency_plot():
    return send_file('recency_plot.png', mimetype='image/png')

@app.route('/monetary_plot')
def get_monetary_plot():
    return send_file('monetary_plot.png', mimetype='image/png')

@app.route('/frequency_plot')
def get_frequency_plot():
    return send_file('frequency_plot.png', mimetype='image/png')

@app.route('/elbow_plot')
def get_elbow_plot():
    """Serve the elbow plot image."""
    return send_file('elbow_plot.png', mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
