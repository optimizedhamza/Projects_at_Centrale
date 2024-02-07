import os
import time
import logging

import boto3
import papermill as pm
import watchtower

from package import config, utils

# Main entry point of the script
if __name__ == "__main__":

    # Determine whether to run the notebook based on the presence of an S3 bucket in the configuration
    run_on_start = False if config.TEST_OUTPUTS_S3_BUCKET == "" else True

    # Exit the script if it is not configured to run on start
    if not run_on_start:
        exit()

    # Create a CloudFormation client using boto3 with the specified AWS region from the config
    cfn_client = boto3.client('cloudformation', region_name=config.AWS_REGION)

    # Set up logging configuration and create a logger instance
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    log_group = "/aws/sagemaker/NotebookInstances"
    stream_name = "{}/run-notebook.log".format(utils.get_notebook_name())
    # Add Watchtower as a handler to send logs to AWS CloudWatch under the specified log group and stream
    logger.addHandler(
        watchtower.CloudWatchLogHandler(log_group=log_group, stream_name=stream_name))
    # Configure another logger for Papermill to also send its logs to CloudWatch
    pm_logger = logging.getLogger('papermill')
    pm_logger.addHandler(
        watchtower.CloudWatchLogHandler(log_group=log_group, stream_name=stream_name))

    # Inform that the script is waiting for a CloudFormation stack to finish launching
    logger.info("Waiting for stack to finish launching...")
    waiter = cfn_client.get_waiter('stack_create_complete')
    waiter.wait(StackName=config.STACK_NAME)  # Wait for the CloudFormation stack creation to complete

    logger.info("Starting notebook execution through papermill")

    # Define variables for the notebook execution
    bucket = config.TEST_OUTPUTS_S3_BUCKET  # S3 bucket to store outputs
    prefix = 'integration-test'  # Prefix for organizing outputs in the S3 bucket
    output_notebook = "output.ipynb"  # Name of the output notebook file

    start_time = time.time()  # Record the start time of the notebook execution
    test_prefix = "/home/ec2-user/SageMaker/test/"  # Base directory for test outputs
    # Open files for capturing standard output and error
    with open(os.path.join(test_prefix, "output_stdout.txt"), 'w') as stdoutfile, open(os.path.join(test_prefix, "output_stderr.txt"), 'w') as stderrfile:
        try:
            # Execute the specified notebook with Papermill, capturing output and errors
            nb = pm.execute_notebook(
                '/home/ec2-user/SageMaker/notebooks/aws_fraud_detection_credit_card_data.ipynb',
                os.path.join(test_prefix, output_notebook),
                cwd='/home/ec2-user/SageMaker/notebooks/',
                kernel_name='python3',
                stdout_file=stdoutfile, stderr_file=stderrfile, log_output=True
            )
        except pm.PapermillExecutionError as err:
            # Log any errors encountered during notebook execution
            logger.warn("Notebook encountered execution error: {}".format(err))
        finally:
            # Calculate and log the execution time of the notebook
            end_time = time.time()
            logger.info("Notebook execution time: {} sec.".format(end_time - start_time))
            s3 = boto3.resource('s3')
            # Upload the output notebook and log files to the specified S3 bucket
            s3.meta.client.upload_file(
                os.path.join(test_prefix, output_notebook), bucket, os.path.join(prefix, output_notebook))
            s3.meta.client.upload_file(
                os.path.join(test_prefix, "output_stdout.txt"), bucket, os.path.join(prefix, "output_stdout.txt"))
            s3.meta.client.upload_file(
                os.path.join(test_prefix, "output_stderr.txt"), bucket, os.path.join(prefix, "output_stderr.txt"))
