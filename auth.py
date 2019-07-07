from app import app
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

DB = 'site.db'


@app.route('/login')
def login():
    if 'user' in session:
        return redirect(url_for('root'), code=303) 
    else:
        return render_template('login.html') 

@app.route('/register')
def register():
    return render_template('reg.html') 


@app.route('/do_register', methods=['POST']) 
def do_register():
    login = request.form['login']
    password = request.form['pass']
    repeat = request.form['repeat']

    if password != repeat: 
        return redirect(url_for('register'), code=303) 

    db = sqlite3.connect(DB) 
    cur = db.cursor()
    cur.execute('select login from users where login=?', [login])  

    if not cur.fetchone():
        cur.execute('insert into users (login, password) values (?, ?)', [login, password]) 
        db.commit() 
        return redirect(url_for('login'), code=303) 

    else:
        return redirect(url_for('register'), code=303)

@app.route('/do_login', methods = ['POST']) 
def do_login():
    login = request.form['login'] 
    password = request.form['pass'] 
    db = sqlite3.connect(DB)
    cur = db.cursor()
    cur.execute('select login from users where login=? and password=?', [login, password])

    if not cur.fetchone(): 
        return redirect(url_for('login'), code=303)
    else:
        session['user'] = login 
        return redirect(url_for('root'), code=303)

@app.route('/do_logout', methods = ['POST']) 
def do_logout():
    session.pop('user') 
    return redirect(url_for('login'), code=303)
