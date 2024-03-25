import re
from flask import Flask, render_template, request, redirect, send_file, send_from_directory, make_response
import requests
import urllib.request
from io import BytesIO
from weasyprint import HTML
from lxml import etree
from ignore.design import design
import os
from werkzeug.utils import secure_filename

app = design.Design(Flask(__name__), __file__, 'SSRF - Lab')
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ssrf1')
def fetch_ssrf1():
    url = request.args.get('url')
    if not url:
        return render_template('ssrf1.html', result='No URL provided!')
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read()
        
        return render_template('ssrf1.html', result=content)
    except Exception as e:
        return render_template('ssrf1.html', result=f'Error: {str(e)}')

@app.route('/ssrf2')
def fetch_ssrf2():
    url = request.args.get('url')
    if not url:
        return render_template('ssrf2.html', result='No URL provided!')
    try:
        if not url.startswith(('http://', 'https://')):
            return render_template('ssrf2.html', result='URL must start with http:// or https://')
        
        response = requests.get(url)
        if response.status_code == 200:
            return render_template('ssrf2.html', result=response.text)
        else:
            return render_template('ssrf2.html', result=f'Failed to fetch URL: {response.status_code}')
    except Exception as e:
        return render_template('ssrf2.html', result=f'Error: {str(e)}')

@app.route('/ssrf3')
def fetch_ssrf3():
    url = request.args.get('url')
    if not url:
        return render_template('ssrf3.html', result='No URL provided!')
    try:
        if not url.startswith(('http://', 'https://')):
            return render_template('ssrf3.html', result='URL must start with http:// or https://')
        
        response = requests.get(url)
        if response.status_code == 200:
            return render_template('ssrf3.html', result='Request sent successfully.')
        else:
            return render_template('ssrf3.html', result=f'Failed to fetch URL: {response.status_code}')
    except Exception as e:
        return render_template('ssrf3.html', result=f'Error: {str(e)}')

@app.route('/ssrf4')
def fetch_ssrf4():
    url = request.args.get('url')
    if not url:
        return render_template('ssrf4.html', result='No URL provided!')
    try:
        if not url.startswith(('http://', 'https://')):
            return render_template('ssrf4.html', result='URL must start with http:// or https://')

        if not url.endswith(('.png', '.jgg', '.webp', '.svg', '.gif')):
            return render_template('ssrf4.html', result='Invalid file extension')
        
        response = requests.get(url)
        if response.status_code == 200:
            return render_template('ssrf4.html', result='Request sent successfully.')
        else:
            return render_template('ssrf4.html', result=f'Failed to fetch URL: {response.status_code}')
    except Exception as e:
        return render_template('ssrf4.html', result=f'Error: {str(e)}')

@app.route('/ssrf5')
def fetch_ssrf5():
    url = request.args.get('url')
    if not url:
        return render_template('ssrf5.html', result='No URL provided!')
    try:
        if not url.startswith(('http://', 'https://')):
            return render_template('ssrf5.html', result='URL must start with http:// or https://')

        if not 'example.com' in url:
            return render_template('ssrf5.html', result='Domain not whitelisted.')
        
        response = requests.get(url)
        if response.status_code == 200:
            return render_template('ssrf5.html', result='Request sent successfully..')
        else:
            return render_template('ssrf5.html', result=f'Failed to fetch URL: {response.status_code}')
    except Exception as e:
        return render_template('ssrf5.html', result=f'Error: {str(e)}')

@app.route('/ssrf6')
def fetch_ssrf6():
    url = request.args.get('url')
    if not url:
        return render_template('ssrf6.html', result='No URL provided!')
    try:
        if not url.startswith(('http://example.com', 'https://example.com')):
            return render_template('ssrf6.html', result='URL not whitelisted.')
        
        response = requests.get(url)
        if response.status_code == 200:
            return render_template('ssrf6.html', result='Request sent successfully.')
        else:
            return render_template('ssrf6.html', result=f'Failed to fetch URL: {response.status_code}')
    except Exception as e:
        return render_template('ssrf6.html', result=f'Error: {str(e)}')

@app.route('/ssrf7')
def fetch_ssrf7():
    url = request.args.get('url')
    if not url:
        return render_template('ssrf7.html', result='No URL provided!')
    try:
        if not url.startswith(('http://localhost:1337/')):
            return render_template('ssrf7.html', result='URL not whitelisted.')
        
        response = requests.get(url)
        if response.status_code == 200:
            return render_template('ssrf7.html', result='Request sent successfully.')
        else:
            return render_template('ssrf7.html', result=f'Failed to fetch URL: {response.status_code}')
    except Exception as e:
        return render_template('ssrf7.html', result=f'Error: {str(e)}')

@app.route('/redirect')
def open_redirect():
    redirect_url = request.args.get('redirect_url')
    if redirect_url:
        return redirect(redirect_url)
    else:
        return render_template('ssrf7.html', result='No redirect URL provided.')

@app.route('/download_example_xml')
def download_example_xml():
    example_xml_content = """
<product>
    <name>DefaultName</name>
    <id>DefaultID</id>
</product>
    """
    response = make_response(example_xml_content)
    response.headers['Content-Disposition'] = 'attachment; filename=template.xml'
    response.headers['Content-Type'] = 'text/xml'
    return response


@app.route('/ssrf8', methods=['GET', 'POST'])
def submit_product():
    try:
        uploaded_file = request.files['file']

        if not uploaded_file:
            return render_template('ssrf8.html', error='Please, upload a file.')

        xml_data = uploaded_file.read()

        if not xml_data:
            return render_template('ssrf8.html', error='File empty')

        parser = etree.XMLParser(resolve_entities=True)
        root = etree.fromstring(xml_data, parser)

        if root is None:
            return render_template('ssrf8.html', error='Root empty')

        name = root.find('name').text if root.find('name') is not None else 'DefaultName'
        product_id = root.find('.//id').text if root.find('.//id') is not None else 'DefaultID'

        return render_template('ssrf8.html', result='Data successfully updated.', name=name, product_id=product_id)

    except Exception as e:
        return render_template('ssrf8.html', error=f'Please, upload a valid xml file.')

@app.route('/ssrf9')
def fetch_ssrf9():
    text = request.args.get('text')
    if not text:
        return render_template('ssrf9.html', error='Please provide your text')

    try:
        # Generate PDF from HTML content
        pdf_bytes = HTML(string=text).write_pdf()

        # Create BytesIO object and write PDF bytes to it
        pdf = BytesIO()
        pdf.write(pdf_bytes)

        # Seek to the beginning of the BytesIO object
        pdf.seek(0)

        return send_file(pdf, mimetype='application/pdf', download_name='safe.pdf', as_attachment=True)

    except Exception as e:
        return render_template('ssrf9.html', error=f'Error: {str(e)}')


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/ssrf10', methods=['GET', 'POST'])
def fetch_ssrf10():
    if 'file' not in request.files:
        return render_template('ssrf10.html', error='No file part')

    file = request.files['file']

    if file.filename == '':
        return render_template('ssrf10.html', error='No selected file')

    if not allowed_file(file.filename):
        return render_template('ssrf10.html', error='Invalid file extension')

    filename = secure_filename(file.filename)
    file.save(os.path.join('uploads', filename))
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1337)
