import re
from flask import Flask, render_template, request, redirect, send_file, send_from_directory
import requests
import urllib.request
from io import BytesIO
from weasyprint import HTML
from ignore.design import design
from werkzeug.utils import secure_filename

app = design.Design(Flask(__name__), __file__, 'SSRF - Lab')
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/ssrf1')
def fetch_ssrf1():
    url = request.args.get('url')
    if not url:
        return render_template('index.html', result='No URL provided!')
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read()
        
        return render_template('index.html', result=content)
    except Exception as e:
        return render_template('index.html', result=f'Error: {str(e)}')

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


@app.route('/ssrf8')
def fetch_ssrf8():
    internal_ip_regex = re.compile(r'(^127\.)|(^10\.)|(^172\.1[6-9]\.)|(^172\.2[0-9]\.)|(^172\.3[0-1]\.)|(^192\.168\.)')
    url = request.args.get('url')
    if not url:
        return 'No URL provided!'

    # Check if the URL contains a private IP address
    if private_ip_regex.search(url):
        return 'Private IP address detected. Access denied.'
    else:
        return 'No private IP address detected. Access allowed.'


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
