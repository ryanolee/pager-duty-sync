from dotenv import load_dotenv
import os

"""
Load env var into file context if one is given
"""
def in_dot_env_context(orig_func):
    def load_dotenv_then_proxy_orig(*args, **kwargs):
        env_dir = os.path.abspath(__file__ + "/../")
        env_file_path = env_dir + ".env"
        
        if os.path.exists(env_file_path):
            load_dotenv(env_file_path)

        return orig_func(*args, **kwargs)
    return load_dotenv_then_proxy_orig