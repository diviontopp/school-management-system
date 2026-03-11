import boto3
import os
from flask import url_for, current_app
from botocore.exceptions import NoCredentialsError

def get_s3_client():
    """Initialize and return a boto3 S3 client."""
    config = current_app.config
    
    s3_params = {
        'aws_access_key_id': config.get('S3_KEY'),
        'aws_secret_access_key': config.get('S3_SECRET'),
        'region_name': config.get('S3_REGION')
    }
    
    # Add endpoint_url if provided (for Railway/Minio)
    if config.get('S3_ENDPOINT'):
        s3_params['endpoint_url'] = config.get('S3_ENDPOINT')
        
    return boto3.client('s3', **s3_params)

def get_storage_url(filename, folder='images'):
    """
    Returns the URL for a file. 
    If STORAGE_TYPE is 's3', it returns the S3 URL.
    Otherwise, it returns the local static URL.
    """
    # If filename starts with static/, remove it as url_for/S3 will handle prefixes
    if filename.startswith('static/'):
        filename = filename.replace('static/', '', 1)

    if current_app.config.get('STORAGE_TYPE') == 's3':
        bucket = current_app.config.get('S3_BUCKET')
        endpoint = current_app.config.get('S3_ENDPOINT')
        
        # In S3, we typically store everything in a flat or structured way.
        # We'll assume the filename passed in matches the S3 key structure.
        
        # If endpoint is provided (Railway/Minio), we use it to build the URL
        if endpoint:
            # Clean endpoint (remove trailing slash)
            base_url = endpoint.rstrip('/')
            return f"{base_url}/{bucket}/{filename}"
        else:
            # Default AWS S3 URL format
            region = current_app.config.get('S3_REGION', 'us-east-1')
            return f"https://{bucket}.s3.{region}.amazonaws.com/{filename}"
            
    # Fallback to local static serving
    # If the filename already has a path (like 'images/dbx/img.jpg'), we don't need folder prefix
    if '/' in filename:
        return url_for('static', filename=filename)
    return url_for('static', filename=f"{folder}/{filename}")

def upload_to_storage(file, filename):
    """
    Uploads a file to the configured storage.
    """
    if current_app.config.get('STORAGE_TYPE') == 's3':
        try:
            s3 = get_s3_client()
            bucket = current_app.config.get('S3_BUCKET')
            
            # Reset file pointer to beginning
            file.seek(0)
            
            s3.upload_fileobj(
                file,
                bucket,
                filename
                # Removed 'public-read' ACL to prevent crashes on strict buckets
            )
            return True
        except Exception as e:
            print(f"Error uploading to S3: {e}")
            return False
            
    # Local storage upload
    try:
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.seek(0)
        file.save(upload_path)
        return True
    except Exception as e:
        print(f"Error saving file locally: {e}")
        return False
