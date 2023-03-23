import re
from subprocess import check_output, CalledProcessError, STDOUT

from utils.colors import Colors

def update_file_exif_date_time(datetime: str, path: str, dry_run: bool = False, verbose: bool = False):
    command = ["exiftool", f"-DateTimeOriginal='{datetime}'", path, '-overwrite_original']
    if not dry_run:
        try:
            output = check_output(command, stderr=STDOUT)
            if verbose:
                print(output.decode())
        except CalledProcessError as e:
            # In my case, a lot of the pictures had the wrong file extension. This code block uses the error from 'exiftool' to correct that
            pattern = r"Not a valid (\w+) \(looks more like a (\w+)\)"
            match = re.search(pattern, e.output.decode())
            if match:
                incompatible_extension = match.group(1)
                correct_extension = match.group(2)
                new_path = re.sub(pattern=f"({incompatible_extension})", repl=correct_extension.lower(), string=path, flags=re.IGNORECASE)
                if verbose:
                    print("Wrong extensions, replacing: ", incompatible_extension, " with ", correct_extension, Colors.END_C)
                update_file_exif_date_time(datetime, new_path, dry_run)

def get_exif_tag(image_path: str, tag: str, verbose: bool = False) -> str:
    output =  check_output(["exiftool", f"-{tag}", image_path])
    decoded_output = output.decode()
    if decoded_output:
        date = decoded_output.strip().split(": ")[1]
        if verbose:
            print("Found data for: ", tag, ", date: ", date)
        return date
    return None