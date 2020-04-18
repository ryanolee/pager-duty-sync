import json

class S3Client():
    def __init__(self, client, bucket_name):
        self.client = client
        self.bucket_name = bucket_name
    
    def write_on_call_entity(self, entity):
        self.client.put_object(
            Bucket=self.bucket_name,
            Body=json.dumps(entity.to_dict()).encode(),
            Key=entity.get_entity_file_name()
        )