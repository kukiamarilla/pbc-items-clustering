from dotenv import load_dotenv
import os

def configure_dvc():
    load_dotenv()
    repo_id = os.getenv("GDRIVE_REPO_ID")
    client_id = os.getenv("GDRIVE_CLIENT_ID")
    client_secret = os.getenv("GDRIVE_CLIENT_SECRET")

    # if env are not set
    if not repo_id or not client_id or not client_secret:
        print("Please set the environment variables GDRIVE_REPO_ID, GDRIVE_CLIENT_ID, GDRIVE_CLIENT_SECRET")
        return
    
    dvc_config = f"""[core]
    remote = storage
    autostage = true
['remote "storage"']
    url = gdrive://{repo_id}
    gdrive_client_id = {client_id}
    gdrive_client_secret = {client_secret}
    """
    with open(".dvc/config", "w") as f:
        f.write(dvc_config)
    
    print("DVC configured successfully")

if __name__ == "__main__":
    configure_dvc()

