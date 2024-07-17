
import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    keys = event["s3_keys"]
    bucket = event["s3_bucket"]
    
    image_data_list = []

    for key in keys:
        s3.download_file(bucket, key, "/tmp/image.png")
        with open("/tmp/image.png", "rb") as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        image_data_list.append({"s3_key": key, "image_data": image_data})

    return {
        'statusCode': 200,
        'body': {
            "image_data_list": image_data_list,
            "s3_bucket": bucket,
            "inferences": []
        }
    }



import json
import boto3
import base64
from sagemaker.predictor import Predictor
from sagemaker.serializers import IdentitySerializer

ENDPOINT = "your-endpoint-name"

def lambda_handler(event, context):
    image_data_list = event['body']['image_data_list']
    inferences = []

    predictor = Predictor(endpoint_name=ENDPOINT)
    predictor.serializer = IdentitySerializer("image/png")

    for image_data_item in image_data_list:
        image_data = base64.b64decode(image_data_item['image_data'])
        prediction = predictor.predict(image_data).decode('utf-8')
        inferences.append({"s3_key": image_data_item["s3_key"], "inference": prediction})

    event["inferences"] = inferences
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }



import json

THRESHOLD = .93

def lambda_handler(event, context):
    inferences = json.loads(event['body']['inferences'])
    filtered_inferences = []

    for inference in inferences:
        inference_values = json.loads(inference["inference"])
        if max(inference_values) >= THRESHOLD:
            filtered_inferences.append(inference)

    if not filtered_inferences:
        raise Exception("THRESHOLD_CONFIDENCE_NOT_MET")

    event["filtered_inferences"] = filtered_inferences
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
