from src.extensions import db
from datetime import datetime, timezone
from flask import request, current_app
from werkzeug.utils import secure_filename
from supabase import create_client, Client
import uuid
import os
import secrets
import string
from io import BytesIO
import tempfile
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

SUPABASE_URL = "https://kchehkuemznwkpsltwpg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjaGVoa3VlbXpud2twc2x0d3BnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY1MTE2NzEsImV4cCI6MjA2MjA4NzY3MX0.6hvJe8hU6qzF4JUVuj6n-vE3vQRgd9PbZzp5VcM-n6I"
BUCKET_NAME = "profile-images"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_image_to_bucket(file, bucket_name=BUCKET_NAME, folder="uploads") -> str | None:
    try:
        ext = os.path.splitext(file.filename)[1] or ".jpg"
        unique_name = f"{uuid.uuid4().hex}{ext}"
        path_in_bucket = f"{folder}/{unique_name}"

        # Create a temporary file safely on Windows
        fd, temp_path = tempfile.mkstemp(suffix=ext)
        try:
            with os.fdopen(fd, 'wb') as tmp:
                tmp.write(file.read())
                tmp.flush()

            # Upload file by path
            response = supabase.storage.from_(bucket_name).upload(path_in_bucket, temp_path)

        finally:
            # Delete temp file manually
            if os.path.exists(temp_path):
                os.remove(temp_path)

        print(f"[DEBUG] Upload response: {response}")

        public_url = supabase.storage.from_(bucket_name).get_public_url(path_in_bucket)
        print(f"[DEBUG] Public URL: {public_url}")

        return public_url

    except Exception as e:
        print(f"[EXCEPTION] Exception during upload: {e}")
        return None