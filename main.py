import os
import re
import traceback

from utils.colors import Colors
from utils.datetime import update_file_create_time, get_google_datetime, get_manual_datetime 
from utils.filesystem import get_file_extension, copy_media
from utils.exif import update_file_exif_date_time, get_exif_tag 
from config import *

def update_media_with_exif(output_path: str, image: str, date_time: str, dry_run: bool = False):
    copy_media(output_path, image, dry_run)
    update_file_exif_date_time(date_time, output_path, dry_run, verbose)
    update_file_create_time(date_time, output_path, dry_run)

def update_media(output_path: str, image: str, date_time: str, dry_run: bool = False):
    copy_media(output_path, image, dry_run)
    update_file_create_time(date_time, output_path, dry_run)

images = []
metadata = []

# Walk the files and determine which are supported images and the google json files.
for root, dirs, files in os.walk(input_path):
    for file in files:
        file_path = os.path.join(root, file)
        if re.search(".*.json", file_path):
            metadata.append(file_path)
        else:
            extension = get_file_extension(file_path)
            if extension in supportedMediaFileTypes:
                images.append(file_path)
            else:
                print("Unsupported extension", file_path)

print('Found ', len(images), ' media files. ')
print('Found', len(metadata), ' metadata files. ')

# Walk through the images/media files and process them
for image_path in images:
    try:
        if verbose:
            print("")
            print(Colors.UNDERLINE, image_path, Colors.END_C)
        if supportedMediaFileTypes[get_file_extension(image_path)]['supportsExif']:
            # Read image
            tag = get_exif_tag(image_path, 'DateTimeOriginal', verbose) or \
                  get_exif_tag(image_path, 'DateTime', verbose) or \
                  get_exif_tag(image_path, 'DateTimeDigitized', verbose)
            # If the image has exif data, update it using that
            if tag:
                update_media_with_exif(os.path.join(output_path, image_path), image_path, tag, dry_run)
            else:
                if verbose:
                    print(Colors.WARNING, "Image has no EXIF datetime information, using the one provided from Google.", Colors.END_C)
                datetime_meta = get_google_datetime(image_path, metadata) 
                # If it has google metadata, update it using that
                if datetime_meta:
                    if verbose:
                        print("Saving image with google datetime as create date.")
                    update_media(os.path.join(output_path, image_path), image_path, datetime_meta, dry_run)
                # If the folder has manual metadata, update it using that
                else:
                    datetime_meta = get_manual_datetime(image_path)
                    if(datetime_meta):
                        print(Colors.WARNING, "Using manual root yaml to update date time, ", image_path, Colors.END_C)
                        update_media(os.path.join(output_path, image_path), image_path, datetime_meta, dry_run)
                    # Copy the file as is, no metadata was found anywhere
                    else:
                        print(Colors.FAIL, "No metadata found for image, copying as is...", image_path, Colors.END_C)
                        copy_media(os.path.join(output_path, image_path), image_path, dry_run)
        # Similar to the above, but does not use/update exif data
        else:
            if verbose:
                print("Unsupported exif media file, updating created time only.")
            datetime_meta = get_google_datetime(image_path, metadata) 
            if datetime_meta:
                if verbose:
                    print("Saving media file with Google datetime as create date.")
                update_media(os.path.join(output_path, image_path), image_path, datetime_meta, dry_run)
            else:
                datetime_meta = get_manual_datetime(image_path)
                if(datetime_meta):
                    print(Colors.WARNING, "Using manual root yaml to update date time, ", image_path, Colors.END_C)
                    update_media(os.path.join(output_path, image_path), image_path, datetime_meta, dry_run)
                else:
                    print(Colors.FAIL, "No metadata found for image, copying as is...", image_path, Colors.END_C)
                    copy_media(os.path.join(output_path, image_path), image_path, dry_run)
    # Global exception handler 
    except:
        print("Something went wrong for: ", image_path)
        traceback.print_exc() 
        break