import json, os, time, boto3

runtime = boto3.client("sagemaker-runtime")
dynamo = boto3.resource("dynamodb").Table(os.environ["LOG_TABLE"])
ENDPOINT = os.environ["SAGEMAKER_ENDPOINT"]

def lambda_handler(event, context):
    print(f"Event: {event}")
    # body = json.loads(event.get("body", event))
    body = event
    print(f"Body: {body}")
    # body = event
    text = body.get("inputs", "")
    print(f"Text : {text}")

    resp = runtime.invoke_endpoint(
        EndpointName=ENDPOINT,
        ContentType="application/json",
        Body=json.dumps({"inputs": text})
    )

    result = json.loads(resp["Body"].read().decode())
    print(f"Model result: {result['generated_text']}")

    log_item = {
        "id": f"{int(time.time()*1000)}#{context.aws_request_id}",
        "prompt": text,
        "response": result['generated_text'],
        "timestamp": int(time.time())
    }
    dynamo.put_item(Item=log_item)

    return {
        "statusCode": 200,
        "body": json.dumps({"result": result['generated_text']})
    }