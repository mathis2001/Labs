import re
from flask import Flask, json, render_template, request
from ignore.design import design

app = design.Design(Flask(__name__), __file__, 'ReDoS - Introduction')

def is_valid_email(email):
    email_regex = re.compile(r'^\S+@([a-zA-Z0-9._-]+)*\.[a-zA-Z0-9._-]+$')
    return bool(re.match(email_regex, email))

@app.route('/')
def index():
    email = request.args.get('email')

    if email is None:
        return render_template('index.html', result='No search query was provided!')


    if is_valid_email(email):
        return render_template('index.html', result='Valid email! You can create an account with this email.')
    else:
        return render_template('index.html', result='User input does not match the regex ^\S+@([a-zA-Z0-9._-]+)*\.[a-zA-Z0-9._-]+$')

# Start the vulnerable server:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1337, debug=True)
