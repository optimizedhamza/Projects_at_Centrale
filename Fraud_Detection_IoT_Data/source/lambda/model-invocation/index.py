import json 
import os  
import logging

import boto3  

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Retrieve environment variables for the stream name and solution prefix
STREAM_NAME = os.environ['StreamName']
SOLUTION_PREFIX = os.environ['SolutionPrefix']

# Main handler function for the AWS Lambda
def lambda_handler(event, context):
    logger.info(event)  # Log the incoming event for debugging
    
    # Validate and retrieve metadata from the event
    metadata = event.get('metadata', None)
    assert metadata, "Request did not include metadata!"
    
    # Validate and retrieve the data payload from the event
    data_payload = event.get('data', None)
    assert data_payload, "Payload did not include a data field!"
    
    # Optional: Retrieve and validate the model choice from the event
    model_choice = event.get('model', None)
    valid_models = {'anomaly_detector', 'fraud_classifier'}
    if model_choice:
        assert model_choice in valid_models, "The requested model, {}, was not a valid model name {}".format(model_choice, valid_models)
    models = {model_choice} if model_choice else valid_models  # Determine which models to use based on the event

    output = {}  # Initialize the output dictionary
    # Call fraud classifier model if requested or by default
    if 'fraud_classifier' in models:
        output["fraud_classifier"] = get_fraud_prediction(data_payload)

    store_data_prediction(output, metadata)  # Log the predictions and metadata
    return output  # Return the predictions

# Function to get fraud prediction from a SageMaker endpoint
def get_fraud_prediction(data, threshold=0.5):
    sagemaker_endpoint_name = "{}-xgb".format(SOLUTION_PREFIX)
    sagemaker_runtime = boto3.client('sagemaker-runtime')
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=sagemaker_endpoint_name, ContentType='text/csv',Body=data)
    pred_proba = json.loads(response['Body'].read().decode())
    prediction = 0 if pred_proba < threshold else 1

    logger.info("classification pred_proba: {}, prediction: {}".format(pred_proba, prediction))

    return {"pred_proba": pred_proba, "prediction": prediction} 

# Function to store predictions and metadata in Kinesis Firehose
def store_data_prediction(output_dict, metadata):
    firehose_delivery_stream = STREAM_NAME  # The Firehose delivery stream name
    firehose = boto3.client('firehose', region_name=os.environ['AWS_REGION'])  # Firehose client

    # Extract predictions if available
    anomaly_score = output_dict["anomaly_detector"]["score"] if 'anomaly_detector' in output_dict else ""

    # Format the record to be logged
    record = ','.join(metadata + [ str(anomaly_score)]) + '\n'

    # Log the record to Kinesis Firehose
    success = firehose.put_record(
        DeliveryStreamName=firehose_delivery_stream, Record={'Data': record})
    if success:
        logger.info("Record logged: {}".format(record))  # Log success
    else:
        logger.warning("Record delivery failed for record: {}".format(record))  # Log failure
