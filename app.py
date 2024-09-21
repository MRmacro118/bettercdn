from flask import Flask, render_template, redirect, url_for, request, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import os
from werkzeug.utils import secure_filename
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# --- Models ---
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    movie_file = db.Column(db.String(300), nullable=False)
    subtitle_file = db.Column(db.String(300))

class User(UserMixin):
    id = 1
    username = "admin"
    password = "password"  # Hardcoded credentials

# --- Utility Functions ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@login_manager.user_loader
def load_user(user_id):
    return User()

# --- Routes ---
@app.route('/')
def movie_list():
    movies = Movie.query.all()
    return render_template('movie_list.html', movies=movies)

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    return render_template('movie_detail.html', movie=movie)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        if 'movie_file' not in request.files:
            flash('No movie file uploaded', 'error')
            return redirect(request.url)

        movie_file = request.files['movie_file']
        subtitle_file = request.files.get('subtitle_file')

        if movie_file and allowed_file(movie_file.filename):
            filename = secure_filename(movie_file.filename)
            movie_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            subtitle_filename = None
            if subtitle_file and allowed_file(subtitle_file.filename):
                subtitle_filename = secure_filename(subtitle_file.filename)
                subtitle_file.save(os.path.join(app.config['UPLOAD_FOLDER'], subtitle_filename))

            new_movie = Movie(title=title, description=description, movie_file=filename, subtitle_file=subtitle_filename)
            db.session.add(new_movie)
            db.session.commit()
            flash('Movie uploaded successfully', 'success')
            return redirect(url_for('admin_panel'))

    movies = Movie.query.all()
    return render_template('admin.html', movies=movies)

@app.route('/admin/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    
    # Delete the movie file from the uploads folder
    movie_file_path = os.path.join(app.config['UPLOAD_FOLDER'], movie.movie_file)
    if os.path.exists(movie_file_path):
        os.remove(movie_file_path)
    
    # Delete the subtitle file if it exists
    if movie.subtitle_file:
        subtitle_file_path = os.path.join(app.config['UPLOAD_FOLDER'], movie.subtitle_file)
        if os.path.exists(subtitle_file_path):
            os.remove(subtitle_file_path)
    
    # Delete the movie from the database
    db.session.delete(movie)
    db.session.commit()
    
    flash('Movie and associated files deleted successfully', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            user = User()
            login_user(user)
            return redirect(url_for('admin_panel'))
        else:
            flash('Invalid credentials', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=50500)
