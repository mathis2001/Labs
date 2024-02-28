from flask import Flask
import html

r = '#ff0000'
w = '#ffffff'
g = '#00ff55'
dg = '#00b33c'
b = '#0052cc'
p = '#cc00cc'
s = '#ffcc66'

def Design(app:Flask, file:str, title:str, desc='') -> Flask:
    app.config['TITLE'] = title
    with open(file, 'r') as f: app.config['SOURCE_CODE'] = ''.join([i for i in f])

    return app

