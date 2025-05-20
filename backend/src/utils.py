from src.extensions import db
from datetime import datetime, timezone
from flask import request, current_app
from werkzeug.utils import secure_filename
import uuid
import os
import secrets
import string

def CreatedAt():
    return db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now()
    )

def UpdatedAt():
    return db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=db.func.now()
    )

class SaveFile:
    def __init__(self, file, subfolder="files"):
        self.filename = secure_filename(file.filename)
        self.unique_filename = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{self.filename.rsplit('.', 1)[-1]}"

        upload_folder = current_app.config['UPLOAD_FOLDER']
        self.folder_path = os.path.join(upload_folder, subfolder)
        os.makedirs(self.folder_path, exist_ok=True)

        self.file_path = os.path.join(self.folder_path, self.unique_filename)
        base_url = request.host_url.rstrip('/')
        self.file_url = f"uploads/{subfolder}/{self.unique_filename}"
        self.full_url = f"{base_url}/{self.file_url}"

        self._file = file

    def save(self):
        self._file.save(self.file_path)

def generate_secure_code(length=8):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))