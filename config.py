import os

class Config:
    SECRET_KEY = 'yoursecretkey'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///movies.db'
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'mp4', 'mkv', 'mov', 'srt'}
