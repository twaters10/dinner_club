import pandas as pd
import boto3
import logging
from io import StringIO


def load_processed_data_to_s3(df: pd.DataFrame, bucket_name: str, csvfilename: str) -> None:
    """Loads the processed data to S3 bucket.

    Args:
        df (pd.DataFrame): Processed data frame to be uploaded.
        bucket_name (str): Name of the S3 bucket.
        csvfilename (str): Name of the CSV file to be created in S3.
        
    Raises:
        e: error in uploading processed data to S3.
    """
    try:
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        s3_client = boto3.client('s3')
        bucket_name = bucket_name
        object_key = csvfilename
        s3_client.put_object(Bucket=bucket_name, Key=object_key, Body=csv_buffer.getvalue())
        logging.info(f"Processed data saved to S3 bucket {bucket_name} at key {object_key}.")
    except Exception as e:
        logging.error(f"Error uploading processed data to S3: {e}")
        raise e