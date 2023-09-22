from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import os, json

DEBUG = True
KEYFILE = "/Users/errol/Downloads/sakey.json"

if "BACKUP_CLIENT_ID" in os.environ:
    credentials_dict = {
        'type': 'service_account',
        'client_id': os.environ['BACKUP_CLIENT_ID'],
        'client_email': os.environ['BACKUP_CLIENT_EMAIL'],
        'private_key_id': os.environ['BACKUP_PRIVATE_KEY_ID'],
        'private_key': os.environ['BACKUP_PRIVATE_KEY'],
    }
elif os.path.exists(KEYFILE):
    with open(KEYFILE) as jsonFile:
        credentials_dict = json.load(jsonFile)
else:
    print("do something")
    exit(199)
# print(credentials_dict)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    credentials_dict
)
client = storage.Client(credentials=credentials, project='theresastrecker')
bucket = client.get_bucket('errol-test-bucket')


def uploadFile(file, filename):
    if DEBUG: print(f'Starting Upload of: {filename}')
    blob = bucket.blob(filename)
    print(blob)
    try:
        print(file)
        blob.upload_from_filename(file)
    except:
        print("Upload Failed")

