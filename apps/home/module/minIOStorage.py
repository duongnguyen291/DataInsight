import boto3
s3 = boto3.client(
    's3',
    endpoint_url='http://127.0.0.1:9000',
    aws_access_key_id='YruQp7n8MAjxMyS02cud',
    aws_secret_access_key='yLpZvIj7TTOTHJbQWK606IXhYWjxSw5XnnNEq7c'
)

def upload_to_minio(file, bucket_name, key):
    s3.upload_fileobj(file, bucket_name, key)
def generate_presigned_url(bucket_name, key, expiration=3600):
    return s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': key},
        ExpiresIn=expiration
    )
def get_file_from_minio(file_key):
    response = s3.get_object(Bucket="datainsight", Key=file_key)
    return response['Body'].read()
