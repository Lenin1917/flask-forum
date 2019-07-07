from app import app
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3


DB = 'site.db'

class MsgData:

    def __init__(self):
        self.id = None
        self.title = None
        self.author = None
        self.content = None
        self.date = None
        self.row = None
        self.last = None
        self.editable = None

class Thread:

    def __init__(self):
        self.id = None
        self.thread_id = None
        self.title = None
        self.content = None
        self.date = None
        self.author = None
        self.editable = None

@app.route('/') 
def root():
    if 'user' not in session:
        return redirect(url_for('login'), code=303)

    user        = session['user']
    db          = sqlite3.connect(DB) 
    cur         = db.cursor() 
    editable    = False
    t1          = datetime.utcnow()
    thread      = cur.execute('SELECT count(*), max(messages.date) as lastmsg, thread.id, thread.author, thread.date, thread.title FROM thread INNER JOIN messages ON thread.id = messages.thread_id GROUP BY thread.id ORDER BY thread.date DESC').fetchall()
    perm        = cur.execute('SELECT perm from users where login=?', [user]).fetchone()
    permission  = perm[0] == "Администратор"
    data        = []

    for t in thread:
        rec         = MsgData()
        rec.id      = t[2]
        rec.author  = t[3]
        rec.date    = datetime.strptime(t[4], "%Y-%m-%d %H:%M:%S")
        rec.title   = t[5]
        rec.row     = t[0]
        rec.last    = t[1]
        difference  = t1 - rec.date
        rec.editable = (difference.total_seconds() < 1800 and rec.author == user) or permission
        data.append(rec)

    return render_template('index.html', perm=permission, user=user, thread=data) 

@app.route('/thread/<int:thread_id>')
def thread(thread_id):
    if 'user' not in session:
        return redirect(url_for('login'), code=303)

    db          = sqlite3.connect(DB)
    cur         = db.cursor()
    editable    = False
    t1          = datetime.utcnow()
    
    thread      = cur.execute('SELECT title FROM thread WHERE id=?', [thread_id]).fetchone()
    if thread == None:
        return redirect(url_for('login'), code=303)

    comments    = cur.execute('SELECT * FROM messages WHERE thread_id=?', [thread_id]).fetchall()
    user        = session['user']
    perm        = cur.execute('SELECT perm FROM users WHERE login=?', [user]).fetchone()
    permission  = perm[0] == "Администратор"
    comment     = []

    for t in comments:
        r           = Thread()
        r.id        = t[0]
        r.thread_id = t[1]
        r.title     = t[2]
        r.content   = t[3]
        r.date      = datetime.strptime(t[4], "%Y-%m-%d %H:%M:%S")
        r.author    = t[5]
        difference  = t1 - r.date
        r.editable  = (difference.total_seconds() < 1800 and r.author == user) or permission
        comment.append(r)

    return render_template('thread.html', perm=permission, user=user, thread=thread[0], comments=comment, thread_id=thread_id) 

@app.route('/edit_thread/<int:id>') 
def edit_thread(id):

    if 'user' not in session:
        return redirect(url_for('login'), code=303)

    db          = sqlite3.connect(DB)
    cur         = db.cursor()
    user        = session['user']
    author      = cur.execute('SELECT author, date, title FROM thread WHERE id=?', [id]).fetchone()
    perm        = cur.execute('SELECT perm FROM users WHERE login=?', [user]).fetchone()


    editable    = False
    t2          = datetime.strptime(author[1], "%Y-%m-%d %H:%M:%S")
    t1          = datetime.utcnow()
    difference  = t1 - t2
    
    permission  = perm[0] == "Администратор"
    time_edit   = difference.total_seconds() < 1800
    who         = author[0] == user

    editable    = time_edit and who or permission

    if editable:
        return render_template('edit_thread.html', id=id, user=user, perm=permission, title=author[2])

    return redirect(url_for('login'), code=303)

@app.route('/edit/<int:id>') 
def edit(id):

    if 'user' not in session:
        return redirect(url_for('login'), code=303)

    db          = sqlite3.connect(DB)
    cur         = db.cursor()
    user        = session['user']
    author      = cur.execute('SELECT author, date FROM messages WHERE id=?', [id]).fetchone()
    perm        = cur.execute('SELECT perm FROM users WHERE login=?', [user]).fetchone()
    comments    = cur.execute('SELECT * FROM messages WHERE id=?', [id]).fetchone()

    editable    = False
    t2          = datetime.strptime(author[1], "%Y-%m-%d %H:%M:%S")
    t1          = datetime.utcnow()
    difference  = t1 - t2
    
    permission  = perm[0] == "Администратор"
    time_edit   = difference.total_seconds() < 1800
    who         = author[0] == user

    editable    = time_edit and who or permission

    editable = difference.total_seconds() < 1800 and author[0] == user or permission

    if editable:
        return render_template('edit.html', id=id, thread_id=comments[1], comments=comments, user=user, perm=permission)

    return redirect(url_for('login'), code=303)

@app.route('/admin')
def admin():
    if 'user' in session:
        db = sqlite3.connect(DB) 
        cur = db.cursor()
        user = session['user'] 
        perm = cur.execute('SELECT perm FROM users WHERE login=?', [session['user']]).fetchone()
        perm = perm[0] == "Администратор"

        if not perm:
            return redirect(url_for('login'), code=303)

        users = cur.execute('SELECT * FROM users').fetchall()

        return render_template('admin.html', perm=perm, user=user, users=users)