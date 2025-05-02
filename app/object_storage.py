import os
import logging
from logging.handlers import RotatingFileHandler
from minio import Minio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for testing mode
TESTING = os.getenv("TESTING", "false").lower() == "true"

# MinIO configuration from environment
MINIO_CONFIG = {
    "endpoint": os.getenv("MINIO_ENDPOINT", "localhost:9000"),
    "access_key": os.getenv("ACCESS_KEY", "miniouser"),
    "secret_key": os.getenv("SECRET_KEY", "pa55word"),
    "secure": os.getenv("MINIO_SECURE", "false").lower() == "true"
}

class MockMinioClient:
    """A mock MinioClient that doesn't make real connections during tests"""
    def __init__(self, *args, **kwargs):
        self.uploaded_files = {}
    def bucket_exists(self, bucket_name):
        return True
    def make_bucket(self, bucket_name, *args, **kwargs):
        return True
    def put_object(self, bucket_name, object_name, data, length, content_type):
        self.uploaded_files[(bucket_name, object_name)] = {
            "data_length": length,
            "content_type": content_type
        }
        return True
    def presigned_get_object(self, bucket_name, object_name, expires):
        return f"http://test-minio-server/{bucket_name}/{object_name}"
    # Add any other mock methods as needed for tests

def get_minio_client():
    """
    Create and return a configured MinioClient instance
    In test mode, returns a MockMinioClient
    """
    if TESTING:
        return MockMinioClient()
    return Minio(
        endpoint=MINIO_CONFIG["endpoint"],
        access_key=MINIO_CONFIG["access_key"],
        secret_key=MINIO_CONFIG["secret_key"],
        secure=MINIO_CONFIG["secure"]
    )

class MinioStorage:
    def __init__(self, client=None):
        self.logger = self._setup_logger()
        self.client = client or get_minio_client()
        self.logger.info(f"MinioStorage initialized with endpoint: {MINIO_CONFIG['endpoint']}")

    def _setup_logger(self) -> logging.Logger:
        log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        log_file = os.getenv("LOG_FILE", "minio_operations.log")
        log_format = os.getenv("LOG_FORMAT", "%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s - %(message)s")
        log_date_format = os.getenv("LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")
        log_max_bytes = int(os.getenv("LOG_MAX_BYTES", 10485760))
        log_backup_count = int(os.getenv("LOG_BACKUP_COUNT", 5))
        log_level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        log_level = log_level_map.get(log_level_str, logging.INFO)
        logger = logging.getLogger("minio_storage")
        logger.setLevel(log_level)
        if logger.hasHandlers():
            logger.handlers.clear()
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=log_max_bytes,
            backupCount=log_backup_count
        )
        file_handler.setLevel(log_level)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter(log_format, log_date_format)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.debug(f"Logger initialized with level: {log_level_str}, file: {log_file}")
        return logger

    # ...existing code from MinioClient methods, adapted to use self.client...
    def store_file(self, bucket_name: str, source_file: str, destination_file: str) -> object:
        self.logger.info(f"Attempting to store file '{source_file}' as '{destination_file}' in bucket '{bucket_name}'")
        if not self.client.bucket_exists(bucket_name):
            error_msg = f"Bucket '{bucket_name}' does not exist."
            self.logger.error(error_msg)
            raise Exception(error_msg)
        try:
            result = self.client.fput_object(bucket_name, destination_file, source_file)
            self.logger.info(f"File '{source_file}' successfully uploaded as '{destination_file}' in bucket '{bucket_name}'")
            self.logger.debug(f"Upload details - Object name: {result.object_name}, ETag: {result.etag}")
            return (result.object_name, result.etag)
        except Exception as e:
            self.logger.error(f"Failed to upload file '{source_file}': {str(e)}", exc_info=True)
            return None
    def create_bucket(self, bucket_name: str) -> None:
        self.logger.info(f"Attempting to create bucket '{bucket_name}'")
        if self.client.bucket_exists(bucket_name):
            self.logger.info(f"Bucket '{bucket_name}' already exists")
            return
        try:
            self.client.make_bucket(bucket_name)
            self.logger.info(f"Bucket '{bucket_name}' created successfully")
        except Exception as e:
            self.logger.error(f"Failed to create bucket '{bucket_name}': {str(e)}", exc_info=True)
    def get_bucket_names(self) -> list:
        self.logger.info("Retrieving list of all buckets")
        try:
            buckets = self.client.list_buckets()
            bucket_names = [bucket.name for bucket in buckets]
            self.logger.debug(f"Retrieved {len(bucket_names)} buckets: {', '.join(bucket_names)}")
            return bucket_names
        except Exception as e:
            self.logger.error(f"Failed to retrieve bucket list: {str(e)}", exc_info=True)
            return []
    def delete_bucket(self, bucket_name: str) -> None:
        self.logger.info(f"Attempting to delete bucket '{bucket_name}'")
        try:
            self.client.remove_bucket(bucket_name)
            self.logger.info(f"Bucket '{bucket_name}' deleted successfully")
        except Exception as e:
            self.logger.error(f"Failed to delete bucket '{bucket_name}': {str(e)}", exc_info=True)
    def download_object(self, bucket_name: str, object_name: str, destination_file: str) -> None:
        self.logger.info(f"Attempting to download object '{object_name}' from bucket '{bucket_name}' to '{destination_file}'")
        try:
            self.client.fget_object(bucket_name, object_name, destination_file)
            self.logger.info(f"File '{object_name}' successfully downloaded as '{destination_file}'")
        except Exception as e:
            self.logger.error(f"Failed to download object '{object_name}': {str(e)}", exc_info=True)
    def get_object(self, bucket_name: str, object_name: str) -> object:
        self.logger.info(f"Getting object '{object_name}' from bucket '{bucket_name}'")
        try:
            obj = self.client.get_object(bucket_name, object_name)
            self.logger.debug(f"Retrieved object '{object_name}' successfully")
            return obj
        except Exception as e:
            self.logger.error(f"Failed to get object '{object_name}': {str(e)}", exc_info=True)
            return None
    def delete_file(self, bucket_name: str, object_name: str) -> None:
        self.logger.info(f"Attempting to delete object '{object_name}' from bucket '{bucket_name}'")
        try:
            self.client.remove_object(bucket_name, object_name)
            self.logger.info(f"Object '{object_name}' deleted successfully from bucket '{bucket_name}'")
        except Exception as e:
            self.logger.error(f"Failed to delete object '{object_name}': {str(e)}", exc_info=True)
    def get_file_names(self, bucket_name: str) -> list:
        self.logger.info(f"Listing all objects in bucket '{bucket_name}'")
        try:
            file_names = []
            objects = self.client.list_objects(bucket_name)
            for obj in objects:
                file_names.append(obj.object_name)
            self.logger.debug(f"Retrieved {len(file_names)} objects from bucket '{bucket_name}'")
            return file_names
        except Exception as e:
            self.logger.error(f"Failed to list objects in bucket '{bucket_name}': {str(e)}", exc_info=True)
            return None
    def get_file_info(self, bucket_name: str, object_name: str) -> dict:
        self.logger.info(f"Getting info for object '{object_name}' in bucket '{bucket_name}'")
        try:
            stat = self.client.stat_object(bucket_name, object_name)
            info = {
                'size': stat.size,
                'last_modified': stat.last_modified
            }
            self.logger.debug(f"Retrieved info for '{object_name}': size={stat.size} bytes, last_modified={stat.last_modified}")
            return info
        except Exception as e:
            self.logger.error(f"Failed to get info for object '{object_name}': {str(e)}", exc_info=True)
            return {}
    def get_file_url(self, bucket_name: str, object_name: str, expires=3600) -> str:
        self.logger.info(f"Generating presigned URL for object '{object_name}' in bucket '{bucket_name}'")
        try:
            url = self.client.presigned_get_object(bucket_name, object_name, expires)
            self.logger.debug(f"Generated presigned URL for '{object_name}'")
            return url
        except Exception as e:
            self.logger.error(f"Failed to generate presigned URL for '{object_name}': {str(e)}", exc_info=True)
            return ""
    def get_file_metadata(self, bucket_name: str, object_name: str) -> dict:
        self.logger.info(f"Getting metadata for object '{object_name}' in bucket '{bucket_name}'")
        try:
            stat = self.client.stat_object(bucket_name, object_name)
            metadata = {
                'size': stat.size,
                'last_modified': stat.last_modified,
                'etag': stat.etag,
                'content_type': stat.content_type,
                'metadata': stat.metadata
            }
            self.logger.debug(f"Retrieved metadata for '{object_name}'")
            return metadata
        except Exception as e:
            self.logger.error(f"Failed to get metadata for object '{object_name}': {str(e)}", exc_info=True)
            return {}
    def get_file_tags(self, bucket_name: str, object_name: str) -> dict:
        self.logger.info(f"Getting tags for object '{object_name}' in bucket '{bucket_name}'")
        try:
            tags = self.client.get_object_tags(bucket_name, object_name)
            self.logger.debug(f"Retrieved tags for '{object_name}': {tags}")
            return tags
        except Exception as e:
            self.logger.error(f"Failed to get tags for object '{object_name}': {str(e)}", exc_info=True)
            return {}
    def set_file_tags(self, bucket_name: str, object_name: str, tags: dict) -> None:
        self.logger.info(f"Setting tags for object '{object_name}' in bucket '{bucket_name}'")
        try:
            self.client.set_object_tags(bucket_name, object_name, tags)
            self.logger.debug(f"Tags set for '{object_name}': {tags}")
        except Exception as e:
            self.logger.error(f"Failed to set tags for object '{object_name}': {str(e)}", exc_info=True)

# Utility function for direct URL access (for compatibility)
def get_file_url(bucket_name, object_name, expires=3600):
    client = get_minio_client()
    return client.presigned_get_object(bucket_name, object_name, expires)
