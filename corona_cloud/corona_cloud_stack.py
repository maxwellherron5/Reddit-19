import os

from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
)
from constructs import Construct
from dotenv import load_dotenv

load_dotenv()

class CoronaCloudStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        reddit_parser_layer = _lambda.LayerVersion(
            self, "RedditParserLayer",
            code=_lambda.AssetCode('lambda/layer/'),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_7],
            description="External dependencies used for parsing Reddit",
            layer_version_name="CoronaCloud-RedditParserLayer",
        )

        reddit_parser_lambda = _lambda.Function(
            self, "RedditParserLambda",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset("lambda"),
            handler="reddit_parser.handler",
            timeout=Duration.seconds(300),
            environment={
                "BOT_USERNAME": os.getenv("BOT_USERNAME"),
                "BOT_PASSWORD": os.getenv("BOT_PASSWORD"),
                "CLIENT_ID": os.getenv("CLIENT_ID"),
                "CLIENT_SECRET": os.getenv("CLIENT_SECRET"),
            },
            layers=[reddit_parser_layer]
        ) 
