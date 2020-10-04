import boto3
import os
from pyathena import connect
from core.logging import get_logger
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

"""
Stub athena client as there are no offline versions of the service
"""
class StubAthenaClient():
    def __init__(self):
        pass

    def get_chargeable_on_call_data(self, *args):
        logger = get_logger()
        logger.info(f'StubAthenaClient: called with {", ".join(args)}')
        rows = [
            {"id": "Q0CHJ6OQQ8QAY5", "name": "Another person", "start_date": "2020-09-06 18:30:00", "end_date": "2020-09-07 06:30:00", "is_chargeable": True},
            {"id": "Q0E3Z39EHASCZ5", "name": "Another person", "start_date": "2020-09-18 06:30:00", "end_date": "2020-09-19 06:30:00", "is_chargeable": True},
            {"id": "Q0IN9S6WH644IM", "name": "A person", "start_date": "2020-09-20 18:30:00", "end_date": "2020-09-21 06:30:00", "is_chargeable": True},
            {"id": "Q0KR6RW1PBSDXV", "name": "Another person", "start_date": "2020-09-26 18:30:00", "end_date": "2020-09-27 06:30:00", "is_chargeable": True},
            {"id": "Q0MV3QIVI6EP91", "name": "A person", "start_date": "2020-10-02 18:30:00", "end_date": "2020-10-03 18:30:00", "is_chargeable": True}
        ]

        return [OnCallShift.from_athena_row(row.values()) for row in rows]

def get_athena_client():
    if os.getenv('ENV') == 'local':
        logger = get_logger()
        logger.warn("Stubbing out athena client with StubAthenaClient")
        return StubAthenaClient()

    return AthenaClient(
        os.getenv("ATHENA_USER_ID"),
        os.getenv("ATHENA_USER_SECRET"),
        os.getenv("ATHENA_DB_NAME"),
        os.getenv("ATHENA_BUCKET_NAME"),
        os.getenv("ATHENA_REGION"),
        os.getenv("ATHENA_DB_TABLE")
    )