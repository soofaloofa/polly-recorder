import os
import uuid
import random
import time
import datetime
from contextlib import closing

import boto3
from boto3.dynamodb.conditions import Key

from chalice import Chalice, IAMAuthorizer

app = Chalice(app_name='recorder')
app.debug = True

authorizer = IAMAuthorizer()

DYNAMO_DB_TABLE = os.environ['DYNAMO_DB_TABLE']
S3_BUCKET = os.environ['S3_BUCKET']

VOICES = ['Celine', 'Mathieu', 'Chantal']


dynamodb = boto3.resource('dynamodb')
polly = boto3.client('polly')
s3 = boto3.client('s3')


def synthesize_speech(record_id, text, voice):
    """
    Synthesizes the text, writing the result to Lambda's temp filesystem.
    """
    response = polly.synthesize_speech(
        OutputFormat='mp3',
        Text=text,
        VoiceId=voice
    )

    output = os.path.join("/tmp/", record_id)

    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            with open(output, "a") as file:
                file.write(stream.read())


def upload_to_s3(record_id, s3_bucket):
    """
    Upload the tmp file to S3.

    Returns the S3 URL of the uploaded result.
    """
    s3.upload_file('/tmp/' + record_id,
                   s3_bucket,
                   record_id + ".mp3")

    s3.put_object_acl(ACL='public-read',
                      Bucket=s3_bucket,
                      Key=record_id + ".mp3")

    location = s3.get_bucket_location(Bucket=s3_bucket)
    region = location['LocationConstraint']

    if region is None:
        url_begining = "https://s3.amazonaws.com/"
    else:
        url_begining = "https://s3-" + str(region) + ".amazonaws.com/" \

    url = url_begining + s3_bucket + "/" + record_id + ".mp3"

    return url


def delete_from_s3(record_id, s3_bucket):
    """
    Delete a file from S3.
    """
    bucket = s3.Bucket(s3_bucket)
    bucket.delete_key(record_id + ".mp3")


def index_in_dynamodb(record_id, text, voice, url, table_name):
    """
    Index the record in DynamoDB.

    Returns the Item.
    """
    table = dynamodb.Table(table_name)
    posix_day = 86400
    expire_time = long(time.time()) + 90*posix_day

    item = {
        'id': record_id,
        'text': text,
        'voice': voice,
        'url': url,
        'created': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'expires': expire_time,
    }

    table.put_item(Item=item)
    return item


@app.route('/recordings',
           methods=['POST'],
           cors=True,
           api_key_required=True)
def create_recording():
    """
    Create a new recording.
    """
    request = app.current_request
    body = request.json_body
    record_id = str(uuid.uuid4())
    text = body.get("text")
    voice = random.choice(VOICES)

    synthesize_speech(record_id, text, voice)

    url = upload_to_s3(record_id, S3_BUCKET)

    try:
        item = index_in_dynamodb(record_id, text, voice, url, DYNAMO_DB_TABLE)

        return [item]
    except Exception:
        delete_from_s3(record_id, S3_BUCKET)
        raise


@app.route('/recordings/{record_id}',
           cors=True,
           api_key_required=True)
def get_recording(record_id):
    """
    Get existing recordings.
    """
    if record_id == "*":
        # List all recordings
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(DYNAMO_DB_TABLE)
        items = table.scan()

        return items["Items"]
    else:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(DYNAMO_DB_TABLE)

        items = table.query(
            KeyConditionExpression=Key('id').eq(record_id)
        )

        return items["Items"]
