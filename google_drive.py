import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the scopes required for the application
# SCOPES = ['https://www.googleapis.com/auth/drive.file']
SCOPES = ['https://www.googleapis.com/auth/drive']
root_file_id = '1yQ9Nu3bmT6enyx107bzBfy90ZB8ltOfN'
creds = None
name_fileId_mapping = dict()

def get_folder_hierarchy(service, folder_id, indent=""):
    global name_fileId_mapping
    folder = service.files().get(fileId=folder_id, fields="name").execute()
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    string_to_return = indent + folder['name']  + "\n"
    name_fileId_mapping[folder['name']] = folder_id
    items = results.get('files', [])
    for item in items:
        # print(item['id'])
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            string_to_return += get_folder_hierarchy(service, item['id'], indent + "__")
    return string_to_return

def authenticate():
    # Authenticate and authorize the application
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return creds

def get_heirarchy():
    global creds, root_file_id
    if creds is None:
        creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    return get_folder_hierarchy(service, root_file_id)


def upload_file(file_path, file_name, folder_id):
    global creds
    if creds is None:
        creds = authenticate()
    # Create a service instance using the credentials
    service = build('drive', 'v3', credentials=creds)

    # Upload the file to Google Drive
    file_metadata = {'name': file_name, 'parents':[folder_id]}
    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = service.files().create(body=file_metadata, media_body=media).execute()

    print('File uploaded successfully.')
    # print('File ID:', uploaded_file.get('id'))

def save_to_file(file_name: str, text: str):
    try:
        with open(file_name, 'w') as file:
            file.write(text)
    except FileNotFoundError:
        print(f"File not found: {file_name}")
        return None
    except IOError:
        print(f"Error reading file: {file_name}")
        return None

def upload_file_text(text, file_name, dir_name):
    local_path = "local_" + file_name
    save_to_file(local_path, text)
    if not dir_name in name_fileId_mapping:
        directory_file_id = root_file_id
    else:
        directory_file_id = name_fileId_mapping[dir_name] 
    upload_file(local_path, file_name, directory_file_id)

def upload_file_image(image_path, file_name, dir_name):
    if not dir_name in name_fileId_mapping:
        directory_file_id = root_file_id
    else:
        directory_file_id = name_fileId_mapping[dir_name] 
    upload_file(image_path, file_name, directory_file_id)
