from aws_cdk import aws_codecommit as codecommit

def create_codecommit_repo(scope, id):
    return codecommit.Repository(scope, "CodeCommitRepo",
        repository_name="simple-ordering-app",
        description="CodeCommit repository created with CDK.",
        code=codecommit.Code.from_directory(
            "../1_monolitik/streamlit_app",
            branch="master",
        ),
    )
