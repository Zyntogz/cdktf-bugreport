#!/usr/bin/env python

import time

start = time.time()
from constructs import Construct
print(time.time() - start)
start = time.time()
from cdktf_cdktf_provider_aws.provider import AwsProvider
print(time.time() - start)
start = time.time()
from cdktf_cdktf_provider_aws.s3_bucket import S3Bucket
print(time.time() - start)
start = time.time()
from cdktf import App, TerraformStack, S3Backend
print(time.time() - start)

class TestStack(TerraformStack):
    def __init__(self, scope: Construct, id: str, environment: str):
        super().__init__(scope, id)

        AwsProvider(self, "AWS", region="eu-central-1")

        S3Backend(self,
            bucket = f"sample-bucket-{environment}-cdktf-backend",
            key = f"{environment}/teststack/terraform.tfstate",
            region = "eu-central-1",
            dynamodb_table = None
        )
        
        my_bucket = S3Bucket(
            self,
            "my_bucket",
            bucket=f"sample-bucket-{environment}-cdktf"
        )

app = App()
TestStack(app, "TestStack", "test")

app.synth()
