# AWS Glue Lambda CloudWatch Utility Script

Instead of using CloudFormation to generate the necessary stack configurations, the scripts in this repo can help perform the following tasks:

- create GlueStartCrawler IAM policy
- create AWSGlueServiceRole for the glue crawler to access s3 content
- create S3ACCESS IAM policy for source and target s3 bucket

- create Glue Crawl Database 
- create GlueCrawler

- create GlueStartCrawlerRole for lambda to start glue crawler
- create Lambda Function to start crawler and upload the code
- create S3 bucket notification event rule to trigger lambda when content is available in S3 bucket
- add permission for s3 to invoke lambda function

- create GlueStartJobRun IAM policy
- create GlueStartJobRunRole for lambda to start ETL job run
- create Lambda Function to start job run and upload the code
- create CloudWatch event rule to trigger lambda when glue crawler state is SUCCEEDED
- add permission for events to invoke Lambda Function


For now, ETL job needs to be created manually in the AWS console
