from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
socketio = SocketIO(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store active users
users = {}

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return render_template('login.html')

@socketio.on('connect')
def handle_connect():
    if 'username' in session:
        users[request.sid] = session['username']
        emit('user_list', list(users.values()), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in users:
        username = users.pop(request.sid)
        emit('user_left', username, broadcast=True)
        emit('user_list', list(users.values()), broadcast=True)

@socketio.on('message')
def handle_message(data):
    emit('message', {
        'user': session['username'],
        'message': data['message']
    }, broadcast=True)

@socketio.on('file')
def handle_file(data):
    filename = secure_filename(data['filename'])
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    with open(filepath, 'wb') as f:
        f.write(data['file'])
    
    emit('file_shared', {
        'user': session['username'],
        'filename': filename,
        'filepath': f'/static/uploads/{filename}'
    }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
