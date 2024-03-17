from boto3.session import Session
from config import settings
from botocore.exceptions import ClientError

session = Session(
    aws_secret_access_key=settings.AWS_SECRET_ACCES_KEY,
    aws_access_key_id=settings.AWS_ACCES_KEY_ID,
    region_name=settings.REGION_NAME
)

s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net'
)

def bucket():
    if settings.MODE == "TEST":
        return settings.TEST_BUCKET_NAME
    return settings.BUCKET_NAME

def create_bucket_if_not_exists(bucket_name):
    try:
        s3.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            s3.create_bucket(Bucket=bucket_name)
    else:
        pass
        #сюда нужно прикрутить лог

# create_bucket_if_not_exists('pastes',