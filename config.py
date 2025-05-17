class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///bookhub.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    SECRET_KEY = 'your-secret-key'
    RESTFUL_JSON = {'ensure_ascii': False}
