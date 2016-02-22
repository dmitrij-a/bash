# -*- coding: UTF-8 -*-

import sqlite3
from flask import Flask, g, redirect, url_for, render_template
from contextlib import closing
import urllib2
import lxml.html as html
import os

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bash.db')
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def bash_scrape():
    posts = []
    req = urllib2.Request('http://bash.im', headers={ 'User-Agent': 'Mozilla/5.0' })
    raw_html = urllib2.urlopen(req).read().decode('cp1251')
    normalized_html = raw_html.replace('<br>', '_br_')
    et = html.document_fromstring(normalized_html)

    for quote in et.xpath("//div[@class='text']/text()"):
        quote = quote.replace('_br_', '<br>')
        posts.append(quote)

    return posts


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def show_entries():
    cur = g.db.execute('select post from entries')
    entries = [dict(post=row[0]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)


@app.route('/add')
def add_entry():
    posts = bash_scrape()
    for quote in posts:
        g.db.execute('''INSERT INTO entries(post)
        VALUES (?)''', (quote,))
        g.db.commit()
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    init_db()
    app.run()
