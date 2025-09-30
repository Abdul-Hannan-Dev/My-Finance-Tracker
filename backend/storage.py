import os
from werkzeug.utils import secure_filename
from pathlib import Path

try:
    import boto3
except Exception:
    boto3 = None

class Storage:
    def __init__(self, upload_dir: str = None, s3_bucket: str = None, s3_prefix: str = ''):
        self.upload_dir = Path(upload_dir) if upload_dir else Path.cwd() / 'uploads'
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
        if s3_bucket and not boto3:
            raise RuntimeError('boto3 is required for S3 storage')
        if s3_bucket:
            self.s3 = boto3.client('s3')

    def save_local(self, file_storage):
        filename = secure_filename(file_storage.filename)
        dest = self.upload_dir / filename
        file_storage.save(str(dest))
        return str(dest)

    def upload_to_s3(self, filepath, key=None):
        if not self.s3_bucket:
            raise RuntimeError('S3 bucket not configured')
        key = key or f"{self.s3_prefix}/{Path(filepath).name}".strip('/')
        self.s3.upload_file(str(filepath), self.s3_bucket, key)
        return key
