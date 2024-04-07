from .base_repository import AbstractRepository
from app.core.cloud import s3


class CloudRepository(AbstractRepository):

    def __init__(self, bucket: str):
        self.bucket: str = bucket

    def create(self, key: str, data):
        s3.put_object(Bucket=self.bucket, Key=key, Body=data)
    
    def get_single(self, key: str):
        try:
            return s3.get_object(Bucket=self.bucket, Key=key)
        except:
            return None
        
    def delete(self, key: str):
        s3.delete_object(Bucket=self.bucket, Key=key)

    def get_all(self, key: str):
        return s3.list_objects(Bucket=self.bucket, Prefix=key)
    
    def update(self, key: str, data):
        s3.put_object(Bucket=self.bucket, Key=key, Body=data)