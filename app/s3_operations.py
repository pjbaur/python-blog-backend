"""
S3/Minio operations for handling file uploads and retrievals
"""
from minio import Minio as MinioClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for testing mode
TESTING = os.getenv("TESTING", "false").lower() == "true"

# Example configuration for MinioClient
MINIO_CONFIG = {
    "endpoint": os.getenv("MINIO_ENDPOINT", "localhost:9000"),
    "access_key": os.getenv("ACCESS_KEY", "miniouser"),
    "secret_key": os.getenv("SECRET_KEY", "pa55word"),
    "secure": os.getenv("MINIO_SECURE", "false").lower() == "true"
}

# Mock MinioClient for testing
class MockMinioClient:
    """A mock MinioClient that doesn't make real connections during tests"""
    
    def __init__(self, *args, **kwargs):
        self.uploaded_files = {}
        
    def bucket_exists(self, bucket_name):
        """Always return True in test mode"""
        return True
        
    def make_bucket(self, bucket_name, *args, **kwargs):
        """Mock bucket creation"""
        return True
        
    def put_object(self, bucket_name, object_name, data, length, content_type):
        """Mock object upload"""
        self.uploaded_files[(bucket_name, object_name)] = {
            "data_length": length,
            "content_type": content_type
        }
        return True
        
    def presigned_get_object(self, bucket_name, object_name, expires):
        """Return a mock URL for testing"""
        return f"http://test-minio-server/{bucket_name}/{object_name}"

def get_minio_client():
    """
    Create and return a configured MinioClient instance
    In test mode, returns a MockMinioClient
    """
    if TESTING:
        return MockMinioClient()
    
    return MinioClient(
        endpoint=MINIO_CONFIG["endpoint"],
        access_key=MINIO_CONFIG["access_key"],
        secret_key=MINIO_CONFIG["secret_key"],
        secure=MINIO_CONFIG["secure"]
    )

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
