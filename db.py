from app import app
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

DB = 'site.db'


@app.route('/do_perm', methods = ['POST']) 
def do_perm():
    if 'user' not in session:
        return redirect(url_for('login'), code=303)

    db = sqlite3.connect(DB) 
    cur = db.cursor()
    login = request.form['login']
    current_user = session['user']

    perm = cur.execute('SELECT perm FROM users WHERE login=?', [current_user]).fetchone()
    perm = perm[0] == "Администратор"

    if not perm:
        return render_template("/")

    if login == current_user:
        return redirect(url_for('admin'), code=303)

    admin = ("Администратор",)
    default = ("Обычный пользователь",)
    who = cur.execute('SELECT perm FROM users WHERE login=?', [login]).fetchone()


    if who == admin:
        cur.execute('UPDATE users SET perm="Обычный пользователь" WHERE login=?', [login])
    else:
        cur.execute('UPDATE users SET perm="Администратор" WHERE login=?', [login]) 
    db.commit() 
    return redirect(url_for('admin'), code=303)


@app.route('/do_thread', methods = ['POST']) 
def do_thread(): 
    if 'user' not in session:
        return redirect(url_for('login'), code=303)

    title = request.form['title']
    content = request.form['content']
    db = sqlite3.connect(DB) 
    cur = db.cursor()
    cur.execute('INSERT INTO thread (date, author, title) VALUES (current_timestamp, ?, ?)', [session['user'], title])
    last_id = cur.lastrowid
    cur.execute('INSERT INTO messages (thread_id, title, content, date, author) VALUES (?, ?, ?, current_timestamp, ?)', [last_id, title, content, session['user']])
    db.commit() 
    return redirect(url_for('root'), code=303)

@app.route('/edit_thread/change', methods = ['POST'])
def do_edit_thread():
    if 'user' not in session:
        return redirect(url_for('login'), code=303)

    id = int(request.form['id'])
    title = request.form['title']
    db = sqlite3.connect(DB) 
    cur = db.cursor()
    cur.execute('UPDATE thread SET title=? WHERE id=?', [title, id]).fetchall()
    db.commit()
    return redirect(url_for('root'), code=303)


@app.route('/edit_thread/delete', methods = ['POST'])
def delete_thread ():
    if 'user' not in session:
        return redirect(url_for('login'), code=303)

    id = int(request.form['id'])
    db = sqlite3.connect(DB)
    cur = db.cursor() 
    cur.execute('DELETE FROM thread WHERE id=?', [id])
    cur.execute('DELETE FROM messages WHERE thread_id=?', [id])
    db.commit()
    return redirect(url_for('root'), code=303)


@app.route('/thread/<int:thread_id>/do_comment', methods = ['POST']) 
def do_comment(thread_id):
    if 'user' not in session:
        return redirect(url_for('login'), code=303) 

    db = sqlite3.connect(DB) 
    cur = db.cursor()
    title = request.form['title']
    content = request.form['content']
    cur.execute('INSERT INTO messages (thread_id, title, date, content, author) VALUES (?, ?, current_timestamp, ?, ?)', [thread_id, title, content, session['user']])
    db.commit()
    return redirect(url_for('thread', thread_id=thread_id), code=303)

        
@app.route('/thread/<int:thread_id>/edit/change', methods = ['POST'])
def do_edit(thread_id):
    if 'user' not in session:
        return redirect(url_for('login'), code=303)

    id = int(request.form['id'])
    title = request.form['title']
    content = request.form['content']
    db = sqlite3.connect(DB) 
    cur = db.cursor()
    thread = cur.execute('UPDATE messages SET title=?, content=? WHERE id=?', [title, content, id]).fetchall()
    db.commit()
    return redirect(url_for('thread', thread_id=thread_id), code=303)

@app.route('/thread/<int:thread_id>/edit/delete', methods = ['POST'])
def delete (thread_id):
    if 'user' not in session:
        return redirect(url_for('login'), code=303)

    id = int(request.form['id'])
    db = sqlite3.connect(DB) 
    cur = db.cursor()
    cur.execute('DELETE FROM messages WHERE id = ?', [id])
    db.commit() 
    return redirect(url_for('thread', thread_id=thread_id), code=303)
