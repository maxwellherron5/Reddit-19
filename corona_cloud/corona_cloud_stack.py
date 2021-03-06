import os

from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
)
from constructs import Construct
from dotenv import load_dotenv

load_dotenv()


class CoronaCloudStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        reddit_parser_role = iam.Role(
            self,
            "reddit_parser_role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonDynamoDBFullAccess"
                ),
            ],
        )

        reddit_parser_layer = _lambda.LayerVersion(
            self,
            "RedditParserLayer",
            code=_lambda.AssetCode("lambda/layer/"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_7],
            description="External dependencies used for parsing Reddit",
            layer_version_name="CoronaCloud-RedditParserLayer",
        )

        reddit_parser_lambda = _lambda.Function(
            self,
            "RedditParserLambda",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset("lambda"),
            handler="reddit_parser.handler",
            timeout=Duration.seconds(300),
            role=reddit_parser_role,
            environment={
                "BOT_USERNAME": os.getenv("BOT_USERNAME"),
                "BOT_PASSWORD": os.getenv("BOT_PASSWORD"),
                "CLIENT_ID": os.getenv("CLIENT_ID"),
                "CLIENT_SECRET": os.getenv("CLIENT_SECRET"),
            },
            layers=[reddit_parser_layer],
        )

        rule = events.Rule(
            self,
            "Rule",
            schedule=events.Schedule.cron(
                minute="0", hour="0", day="*", month="*", year="*"
            ),
        )
        rule.add_target(targets.LambdaFunction(reddit_parser_lambda))

        dynamodbTable = dynamodb.Table(
            self,
            id="KeywordCounts",
            table_name="KeywordCounts",
            partition_key=dynamodb.Attribute(
                name="timestamp", type=dynamodb.AttributeType.STRING
            ),
        )
