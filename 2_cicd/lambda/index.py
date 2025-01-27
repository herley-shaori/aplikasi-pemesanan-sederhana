import boto3
import os

codecommit = boto3.client('codecommit')
s3 = boto3.client('s3')


def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # Download file from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        file_content = response['Body'].read()

        # Update CodeCommit repository
        repo_name = os.environ['REPO_NAME']
        file_path = key.replace('codecommit/', '')

        try:
            codecommit.put_file(
                repositoryName=repo_name,
                branchName='master',
                fileContent=file_content,
                filePath=file_path,
                commitMessage=f'Update {file_path} from S3'
            )
            print(f"Successfully updated {file_path} in CodeCommit repository {repo_name}")
        except Exception as e:
            print(f"Error updating CodeCommit repository: {str(e)}")
