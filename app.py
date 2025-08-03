from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Пути загрузки
PENDING_FOLDER = 'static/uploads/pending'
APPROVED_FOLDER = 'static/uploads/approved'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}

app.config['UPLOAD_FOLDER'] = PENDING_FOLDER

# Логин/пароль модератора
MODERATOR_LOGIN = os.getenv('MODERATOR_LOGIN')
MODERATOR_PASSWORD = os.getenv('MODERATOR_PASSWORD')

# Создание папок
os.makedirs(PENDING_FOLDER, exist_ok=True)
os.makedirs(APPROVED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    files = os.listdir(APPROVED_FOLDER)
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file or file.filename == '':
        return 'Файл не выбран'
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(PENDING_FOLDER, filename))
        return redirect(url_for('index'))
    return 'Недопустимый формат файла'

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(APPROVED_FOLDER, filename)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == MODERATOR_LOGIN and password == MODERATOR_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('moderate'))
        else:
            error = "Неверный логин или пароль"
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/moderate')
def moderate():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    files = os.listdir(PENDING_FOLDER)
    return render_template('moderate.html', files=files)

@app.route('/approve/<filename>')
def approve(filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    src = os.path.join(PENDING_FOLDER, filename)
    dst = os.path.join(APPROVED_FOLDER, filename)
    if os.path.exists(src):
        os.rename(src, dst)
    return redirect(url_for('moderate'))

@app.route('/reject/<filename>')
def reject(filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    path = os.path.join(PENDING_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
    return redirect(url_for('moderate'))

@app.route('/from-users')
def from_users():
    files = os.listdir(APPROVED_FOLDER)
    return render_template('from_users.html', files=files)

if __name__ == '__main__':
    app.run(debug=True)
