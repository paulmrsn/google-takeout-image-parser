import re
import json
import os
from subprocess import call
from datetime import datetime

# Get the datetime from the google json
def get_google_datetime(image_path, metadata):
    generated_json_name = image_path + ".json"

    # Edited google photos share the json with the original photo
    if '-edited' in image_path:
        generated_json_name = image_path.replace('-edited', '') + ".json"

    # if '-COLLAGE' in image_path:
    #     generated_json_name = image_path + ".j.json"

    # Case for duplicate media names x(1).jpg going to x.jpg(1).json
    match = re.match(r".*\((\d+)\)\..*", image_path)
    if match:
        number = match.group(1)
        generated_json_name = image_path.replace(f"({number})", '') + f"({number}).json"

    if generated_json_name in metadata:
        # Read the metadata from the JSON file
        with open(generated_json_name) as f:
            img_meta = json.load(f)

        datetime_raw = img_meta["photoTakenTime"]["timestamp"] or img_meta["creationTime"]["timestamp"]
        return datetime.fromtimestamp(int(datetime_raw)).strftime("%Y:%m:%d %H:%M:%S")
    return None 

# Get the datetime from fallback.json
def get_manual_datetime(image_path):
    # Get parent directory of media file 
    manual_json_name = os.path.dirname(image_path) + "/fallback.json"

    if os.path.exists(manual_json_name):
        # Read the metadata from the JSON file
        with open(manual_json_name) as f:
            img_meta = json.load(f)

        datetime_raw = img_meta["fallbackTime"]
        return datetime.strptime(datetime_raw, "%Y:%m:%d %H:%M:%S").strftime("%Y:%m:%d %H:%M:%S")
    return None

def normalize_exif_date(date_string : str) -> str:
    date =  datetime.strptime(date_string.replace('-', ':'), "%Y:%m:%d %H:%M:%S")
    date_formatted = date.strftime("%m/%d/%Y %H:%M:%S")
    return date_formatted

def update_file_create_time(datetime: str, path: str, dry_run: bool = False):
    create_time_command = f"SetFile -d '{normalize_exif_date(datetime)}' '{path}'"
    if not dry_run:
        call(create_time_command, shell=True)