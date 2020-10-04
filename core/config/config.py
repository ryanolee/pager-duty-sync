from dotenv import load_dotenv
import os

from core.logging import get_logger

"""
Load env var into file context if one is given
"""
def in_dot_env_context(orig_func):
    def load_dotenv_then_proxy_orig(*args, **kwargs):
        logger = get_logger()
        logger.info("Looking for .env file")

        env_dir = os.path.abspath(__file__ + "/../../../")
        env_file_path = env_dir + "/.env"
        
        if os.path.exists(env_file_path):
            logger.info("Found .env file loading vars")
            load_dotenv(env_file_path)
        else:
            logger.info("No .env file found skipping" + env_file_path)
        return orig_func(*args, **kwargs)
    return load_dotenv_then_proxy_orig

