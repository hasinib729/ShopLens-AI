import os
import shutil
from typing import Optional
from app.utils.config import settings

# Try loading boto3
S3_AVAILABLE = False
_s3_client = None

try:
    import boto3
    if settings.AWS_ACCESS_KEY_ID != "mock-key":
        _s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        S3_AVAILABLE = True
except Exception:
    pass

class StorageService:
    @staticmethod
    def upload_image(file_content: bytes, filename: str) -> str:
        """
        Saves query image uploads.
        If S3 is active, uploads to bucket; otherwise saves to local directory.
        Returns the public URL path or local path.
        """
        local_path = os.path.join(settings.LOCAL_STORAGE_DIR, "images", filename)
        
        # Save locally first
        with open(local_path, "wb") as f:
            f.write(file_content)
            
        if S3_AVAILABLE and _s3_client:
            try:
                _s3_client.upload_file(
                    local_path, 
                    settings.S3_BUCKET_NAME, 
                    f"images/{filename}",
                    ExtraArgs={"ACL": "public-read"}
                )
                # Return S3 URL
                return f"https://{settings.S3_BUCKET_NAME}.s3.amazonaws.com/images/{filename}"
            except Exception as e:
                print(f"S3 upload error: {e}. Falling back to local URL.")
                
        # Return local static path
        return f"/static/images/{filename}"

    @staticmethod
    def save_model_artifact(local_file_path: str, model_name: str) -> Optional[str]:
        """Saves trained model weights to active storage storage."""
        filename = os.path.basename(local_file_path)
        dest_local_path = os.path.join(settings.LOCAL_STORAGE_DIR, "models", filename)
        
        # Copy to storage/models folder
        if os.path.abspath(local_file_path) != os.path.abspath(dest_local_path):
            shutil.copy2(local_file_path, dest_local_path)
            
        if S3_AVAILABLE and _s3_client:
            try:
                s3_key = f"models/{model_name}/{filename}"
                _s3_client.upload_file(local_file_path, settings.S3_BUCKET_NAME, s3_key)
                return f"s3://{settings.S3_BUCKET_NAME}/{s3_key}"
            except Exception as e:
                print(f"S3 save model error: {e}")
                
        return dest_local_path
