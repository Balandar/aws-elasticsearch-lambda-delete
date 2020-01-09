# Summary

This AWS lambda function will delete old indicies from the AWS Elastic Search Service.

# Req:

Python 3.6.

- Run ./install.sh (or skip install and use function_clean.zip in the steps below)
- Create a python 3.6 function in lambda.
- Upload function.zip to your lambda python function. 
- Edit the lambda_function.py values as needed.

# Permissions:

Add the following permissions to your function
```
    {
      "Effect": "Allow",
      "Action": [
        "es:ESHttpPost",
        "es:ESHttpGet",
        "es:ESHttpPut",
        "es:ESHttpDelete"
      ],
      "Resource": "arn:aws:es:us-west-1:123456789012:domain/my-domain/*"
    }
```
# Basic Settings

Index Deletion	128 MB	10 seconds

# Trigger

Index Deletion	CloudWatch Events	Schedule expression	rate(1 day)

# Refs:

- https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html
- https://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/curator.html
- https://blog.mapbox.com/aws-lambda-python-magic-e0f6a407ffc6
- https://gist.github.com/egonbraun/b8a63cdd6f5410d549f2cce2233c4c8e
