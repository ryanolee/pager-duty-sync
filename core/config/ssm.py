import boto3
import os
from core.logging import get_logger
from functools import wraps

"""
Loads env vars given by name 
"""
def enrich_env(env_vars):
    logging = get_logger()
    
    if os.getenv("ENV", "prod") == "local":
        logging.info("Skipping SSM enrichment. ENV loaded from dev")
        return

    client = boto3.client('ssm')
    results = client.get_parameters(
        Names=env_vars,
        WithDecryption=True
    )

    if 'InvalidParameters' in results and results['InvalidParameters'] != []:

        logging.warn("Failed to load env vars from SSM: [{vars}].".format(vars=results['InvalidParameters'].join(', ')))

    values_to_export = {value["Name"]:value["Value"] for value in results["Parameters"]}
    
    # Export to env
    os.environ = {**os.environ, **values_to_export}

    logging.info("Successfully loaded [{keys}] from SSM".format(keys=", ".join(values_to_export.keys())))

"""Create a wrapper that can accept an array of vars to pull in from ssm then proxy the orig func"""
def enrich_env_with_ssm_secrets(vars_to_import):
    def wrapper_to_return(func):
        def wrapped_func(*inner_args, **inner_kw_args):
            enrich_env(vars_to_import)
            return func(*inner_args, **inner_kw_args)
        return wrapped_func
    return wrapper_to_return