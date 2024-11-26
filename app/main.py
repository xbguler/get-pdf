import base64
import os
from flask import Flask, request, jsonify
from PIL import Image
import pdfkit
# from io import BytesIO

app = Flask(__name__)

# Base64'ten dosyaya dönüştürme fonksiyonu
def base64_to_file(base64_data, file_name):
    file_data = base64.b64decode(base64_data)
    with open(file_name, "wb") as file:
        file.write(file_data)

# PNG'den PDF'ye dönüştürme fonksiyonu
def png_to_pdf(png_file):
    img = Image.open(png_file)
    pdf_path = png_file.replace(".png", ".pdf")
    img.convert("RGB").save(pdf_path, "PDF")
    return pdf_path

# HTML'den PDF'ye dönüştürme fonksiyonu
# def html_to_pdf(html_file):
    # pdf_path = html_file.replace(".html", ".pdf")
    # # config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    # pdfkit.from_file(html_file, pdf_path) #,configuration=config)
    # return pdf_path
    # HTML(html_file).write_pdf(pdf_path)
    # return pdf_path
    # Base64 kodlanmış HTML verisini decode edip geçici dosyaya kaydediyoruz

def html_to_pdf(html_data, pdf_filename):
    html_content = base64.b64decode(html_data).decode('utf-8')

    # PDF dosyasını oluşturuyoruz
    # config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    #config = pdfkit.configuration(wkhtmltopdf='/app/bin/wkhtmltopdf')
    #pdfkit.from_string(html_content, pdf_filename,configuration=config)
    pdfkit.from_string(html_content, pdf_filename)
    return pdf_filename

# Dosyayı Base64 formatına dönüştürme fonksiyonu
def file_to_base64(file_path):
    with open(file_path, "rb") as file:
        file_data = file.read()
    return base64.b64encode(file_data).decode('utf-8')

@app.route('/')
def init():
    return '<h1>PDF Converter</h1><h2>file_name (png/html) & base64_data</h2>'

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # JSON formatında gelen veriyi alıyoruz
        data = request.get_json()
        file_name = data['file_name']
        base64_data = data['base64_data']

        # Base64 verisini dosyaya dönüştürme
        base64_to_file(base64_data, file_name)

        # Dosya türünü kontrol etme ve dönüşüm yapma
        if file_name.endswith('.png'):
            # PNG'den PDF'ye dönüştür
            pdf_file = png_to_pdf(file_name)
        elif file_name.endswith('.html'):
            # HTML'den PDF'ye dönüştür
            # pdf_file = html_to_pdf(file_name)
            pdf_file = file_name.replace(".html", ".pdf")
            pdf_file = html_to_pdf(base64_data, pdf_file)
        else:
            return jsonify({"error": "Unsupported file type."}), 400

        # PDF'yi Base64'e çevir
        pdf_base64 = file_to_base64(pdf_file)

        # Dönüştürülen PDF dosyasını silme
        os.remove(pdf_file)
        os.remove(file_name)

        # PDF verisini ve dosya adını JSON formatında döndürme
        # return jsonify({"file_name": pdf_file.replace('.pdf', ''), "pdf_base64": pdf_base64})
        return jsonify({"file_name": pdf_file, "pdf_base64": pdf_base64})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
