# polly-recorder

A chalice based recording interface for converting text-to-speech using
AWS polly.

See: https://sookocheff.com/post/aws/learning-a-language-with-amazon-polly/

## Setup

### CloudFormation Resources

A CloudFormation template is included to deploy an S3 bucket for storing
recordings and a DynamoDB table for indexing the stored recordings.

Create the CloudFormation stack using the AWS CLI setting any parameters
correctly.

```bash
aws cloudformation create-stack \
    --stack-name polly-recorder \
    --template-body file://cloudformation.yaml \
    --parameters ParameterKey=S3BucketName,ParameterValue=<s3-bucket-name> \
                 ParameterKey=DynamoDBTableName,ParameterValue=<dynamo-table>
```

### Chalice Application

Update `.chalice/config.json` with environment variables for your
application.

* DYNAMO_DB_TABLE: The table used to index recordings.
* S3_BUCKET: The bucket used to store recordings.

Example:

```json
{
  "version": "2.0",
  "app_name": "polly-recorder",
  "stages": {
    "dev": {
      "api_gateway_stage": "dev",
      "environment_variables": {
        "DYNAMO_DB_TABLE": "<your-table-name>",
        "S3_BUCKET": "<your-bucket-name>"
      }
    }
  }
}
```

Deploy your application:

```
$ chalice deploy
```

### Update IAM Policies

The Lambda function deployed by Chalice will need to have access to the S3
bucket, the DynamoDB table, and to Amazon Polly. Set the policy on the
Lambda function as appropriate.

### Create an API Key

Create an API key for API Gateway endpoint to be used by the user
interface for (somewhat) secure access.

### Web Interface

The web interface (`index.html`) needs to now which API endpoint and API
key to use. Set these in `script.js`.

## Usage

Open `index.html` to start recording input text.
