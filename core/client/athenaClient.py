import boto3
import os
from pyathena import connect
from core.entitiy import OnCallShift

"""
Table schema
@todo move this into cloud formation
Move this into cloud formation code:
    id: string
    name: string
    start_date: timestamp
    end_date: timestamp
    is_chargeable: boolean
"""
class AthenaClient():
    def __init__(self, aws_secret_id, aws_secret_access_key, database, bucket, region, table):
        self.cursor = connect(aws_access_key_id=aws_secret_id,
                 aws_secret_access_key=aws_secret_access_key,
                 s3_staging_dir='s3://{0}/'.format(bucket),
                 region_name=region
            ).cursor()
        self.database = database
        self.table = table
    
    def get_chargeable_on_call_data(self, since, until):
        query = self.cursor.execute("SELECT * FROM {database}.{table} WHERE start_date > DATE(%(start)s) AND end_date < DATE(%(until)s) AND is_chargeable = true".format(
            database= self.database,
            table = self.table
        ), {
            "start": since,
            "until": until
        })
    
        results = self.cursor.fetchall()
        return [OnCallShift.from_athena_row(row) for row in results]

def get_athena_client():
    return AthenaClient(
        os.getenv("ATHENA_USER_ID"),
        os.getenv("ATHENA_USER_SECRET"),
        os.getenv("ATHENA_DB_NAME"),
        os.getenv("ATHENA_BUCKET_NAME"),
        os.getenv("ATHENA_REGION"),
        os.getenv("ATHENA_DB_TABLE")
    )