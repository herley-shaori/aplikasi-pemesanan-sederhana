from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as codepipeline_actions
from aws_cdk import aws_codedeploy as codedeploy


def create_codepipeline(scope, id, repo, ec2_instance):
    # Create CodePipeline
    pipeline = codepipeline.Pipeline(scope, id)

    # Source Stage
    source_output = codepipeline.Artifact()
    source_action = codepipeline_actions.CodeCommitSourceAction(
        action_name="CodeCommit",
        repository=repo,
        output=source_output,
        branch="master"
    )
    pipeline.add_stage(
        stage_name="Source",
        actions=[source_action]
    )

    # Create CodeDeploy Application and Deployment Group
    codedeploy_app = codedeploy.ServerApplication(scope, f"{id}-CodeDeployApp")
    deployment_group = codedeploy.ServerDeploymentGroup(
        scope,
        f"{id}-DeploymentGroup",
        application=codedeploy_app,
        ec2_instance_tags=codedeploy.InstanceTagSet(
            {"Project": ["CICD"]}  # Match EC2 instance by tag "Name"
        ),
        deployment_config=codedeploy.ServerDeploymentConfig.ALL_AT_ONCE  # Deployment strategy
    )

    # Deploy Stage
    deploy_action = codepipeline_actions.CodeDeployServerDeployAction(
        action_name="CodeDeploy",
        input=source_output,
        deployment_group=deployment_group
    )

    pipeline.add_stage(
        stage_name="Deploy",
        actions=[deploy_action]
    )