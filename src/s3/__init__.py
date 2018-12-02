from botocore.exceptions import ClientError


def bucket_exists(client, bucket_name):
    try:
        client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError:
        return False


def create_bucket(client, bucket_name, bucket_region):
    try:
        client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': bucket_region
            }
        )
        return True
    except ClientError:
        return False
