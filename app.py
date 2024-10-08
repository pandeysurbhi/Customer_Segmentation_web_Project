from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

app = Flask(__name__)

# Directory to save the plots
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def load_data(file_path):
    """Load the dataset from the given file path."""
    return pd.read_csv(file_path, sep=",", encoding='ISO-8859-1', header=0)

def clean_data(retail):
    """Clean the dataset by handling missing values and converting data types."""
    retail = retail.dropna()
    retail['CustomerID'] = retail['CustomerID'].astype(str)
    return retail

def calculate_monetary(retail):
    """Calculate the monetary value of transactions."""
    retail['Amount'] = retail['Quantity'] * retail['UnitPrice']
    rfm_m = retail.groupby('CustomerID')['Amount'].sum().reset_index()
    return rfm_m

def calculate_frequency(retail):
    """Calculate the frequency of transactions."""
    rfm_f = retail.groupby('CustomerID')['InvoiceNo'].count().reset_index()
    rfm_f.columns = ['CustomerID', 'Frequency']
    return rfm_f

def calculate_recency(retail):
    """Calculate the recency of the last purchase."""
    retail['InvoiceDate'] = pd.to_datetime(retail['InvoiceDate'], format='%d/%m/%Y %H:%M', errors='coerce')
    max_date = retail['InvoiceDate'].max()
    retail['Diff'] = max_date - retail['InvoiceDate']
    rfm_p = retail.groupby('CustomerID')['Diff'].min().reset_index()
    rfm_p['Diff'] = rfm_p['Diff'].dt.days
    return rfm_p

def create_rfm_table(rfm_m, rfm_f, rfm_p):
    """Combine monetary, frequency, and recency into a single DataFrame."""
    rfm = pd.merge(rfm_m, rfm_f, on='CustomerID', how='inner')
    rfm = pd.merge(rfm, rfm_p, on='CustomerID', how='inner')
    rfm.columns = ['CustomerID', 'Amount', 'Frequency', 'Recency']
    return rfm

def plot_recency(rfm):
    plt.figure(figsize=(10, 6))
    sns.histplot(rfm['Recency'], bins=30, kde=True)
    plt.title('Recency Distribution')
    plt.xlabel('Recency (Days)')
    plt.ylabel('Frequency')
    plot_path = os.path.join(app.config['UPLOAD_FOLDER'], 'recency_plot.png')
    plt.savefig(plot_path)
    plt.close()
    return 'uploads/recency_plot.png'

def plot_monetary(rfm):
    plt.figure(figsize=(10, 6))
    sns.histplot(rfm['Amount'], bins=30, kde=True)
    plt.title('Monetary Distribution')
    plt.xlabel('Monetary Value')
    plt.ylabel('Frequency')
    plot_path = os.path.join(app.config['UPLOAD_FOLDER'], 'monetary_plot.png')
    plt.savefig(plot_path)
    plt.close()
    return 'uploads/monetary_plot.png'

def plot_frequency(rfm):
    plt.figure(figsize=(10, 6))
    sns.histplot(rfm['Frequency'], bins=30, kde=True)
    plt.title('Frequency Distribution')
    plt.xlabel('Frequency of Purchases')
    plt.ylabel('Frequency')
    plot_path = os.path.join(app.config['UPLOAD_FOLDER'], 'frequency_plot.png')
    plt.savefig(plot_path)
    plt.close()
    return 'uploads/frequency_plot.png'


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            retail = load_data(file_path)
            retail = clean_data(retail)
            rfm_m = calculate_monetary(retail)
            rfm_f = calculate_frequency(retail)
            rfm_p = calculate_recency(retail)
            rfm = create_rfm_table(rfm_m, rfm_f, rfm_p)

            recency_plot = plot_recency(rfm)
            monetary_plot = plot_monetary(rfm)
            frequency_plot = plot_frequency(rfm)

            return render_template('results.html', recency_plot=recency_plot,
                                   monetary_plot=monetary_plot,
                                   frequency_plot=frequency_plot)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
