"""
S3/Minio operations for handling file uploads and retrievals
"""
from minio import Minio as MinioClient

# Example configuration for MinioClient
MINIO_CONFIG = {
    "endpoint": "your-minio-endpoint:9000",  # Replace with your actual endpoint
    "access_key": "your-access-key",         # Replace with your access key
    "secret_key": "your-secret-key",         # Replace with your secret key
    "secure": False                          # Set to True if using HTTPS
}

def get_minio_client():
    """
    Create and return a configured MinioClient instance
    """
    return MinioClient(
        endpoint=MINIO_CONFIG["endpoint"],
        access_key=MINIO_CONFIG["access_key"],
        secret_key=MINIO_CONFIG["secret_key"],
        secure=MINIO_CONFIG["secure"]
    )

def upload_file(file_path, bucket_name, object_name=None):
    """
    Upload a file to the specified S3/Minio bucket
    
    Args:
        file_path (str): Path to the file on local filesystem
        bucket_name (str): Name of the bucket
        object_name (str, optional): Object name in the bucket. If not specified, file_path's basename is used
        
    Returns:
        str: URL of the uploaded object
    """
    client = get_minio_client()
    return client.upload_file(file_path, bucket_name, object_name)

def download_file(bucket_name, object_name, file_path):
    """
    Download a file from the specified S3/Minio bucket
    
    Args:
        bucket_name (str): Name of the bucket
        object_name (str): Object name in the bucket
        file_path (str): Path where the file will be saved
        
    Returns:
        bool: True if successful, False otherwise
    """
    client = get_minio_client()
    return client.download_file(bucket_name, object_name, file_path)

def get_file_url(bucket_name, object_name, expires=3600):
    """
    Get a presigned URL for the object
    
    Args:
        bucket_name (str): Name of the bucket
        object_name (str): Object name in the bucket
        expires (int, optional): Expiration time in seconds. Default is 1 hour.
        
    Returns:
        str: Presigned URL
    """
    client = get_minio_client()
    return client.get_presigned_url(bucket_name, object_name, expires)
