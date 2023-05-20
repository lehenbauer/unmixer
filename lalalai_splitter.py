
# Copyright (c) 2021 LALAL.AI
# Copyright (c) 2023 Karl Lehenbauer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import json
import os
import re
import sys
import time
from argparse import ArgumentParser
from urllib.parse import quote, unquote, urlencode
from urllib.request import urlopen, Request


CURRENT_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
URL_API = "https://www.lalal.ai/api/"

stem_types = [
    "vocals",
    "drum",
    "bass",
    "piano",
    "electric_guitar",
    "acoustic_guitar",
    "synthesizer",
    "voice",
    "strings",
    "wind",
]



def validate_stems(stems):
    """
    Validates the list of stems and returns the name of any stem that is
    not recognized, else None if all stems are valid.
    """
    for stem in stems:
        if stem not in stem_types:
            return stem
    return None


def make_content_disposition(filename, disposition="attachment"):
    """
    Generates a Content-Disposition header for a given filename, with
    the specified disposition type.
    """
    try:
        filename.encode("ascii")
        file_expr = f'filename="{filename}"'
    except UnicodeEncodeError:
        quoted = quote(filename)
        file_expr = f"filename*=utf-8''{quoted}"
    return f"{disposition}; {file_expr}"


def upload_file(file_path, license):
    """
    Uploads a file to the Lalal.ai API and returns the file ID on success.
    Raises a `RuntimeError` with the API error message on failure.
    """
    url_for_upload = URL_API + "upload/"
    _, filename = os.path.split(file_path)
    headers = {
        "Content-Disposition": make_content_disposition(filename),
        "Authorization": f"license {license}",
    }
    with open(file_path, "rb") as f:
        request = Request(url_for_upload, f, headers)
        with urlopen(request) as response:
            upload_result = json.load(response)
            if upload_result["status"] == "success":
                return upload_result["id"]
            else:
                raise RuntimeError(upload_result["error"])


def split_file(file_id, license, stem, filter_type, splitter):
    """
    Submits a file with the specified `file_id` to the Lalal.ai API for stem
    separation.  The `stem` parameter specifies the stem to extract, and the
    `filter_type` parameter specifies the strength of the filtering to apply.
    The `splitter` parameter specifies the type of neural network to use
    for the separation.

    Raises a `RuntimeError` with the API error message on failure.
    """
    url_for_split = URL_API + "split/"
    headers = {
        "Authorization": f"license {license}",
    }
    query_args = {
        "id": file_id,
        "stem": stem,
        "filter": filter_type,
        "splitter": splitter,
    }
    encoded_args = urlencode(query_args).encode("utf-8")
    request = Request(url_for_split, encoded_args, headers=headers)
    with urlopen(request) as response:
        split_result = json.load(response)
        if split_result["status"] == "error":
            print(f'%split_result_error {split_result}')
            raise RuntimeError(split_result["error"])


def check_file(stem, file_id):
    """
    Checks the status of a file submitted for stem separation by the
    Lalal.ai API.  Polls the API for updates until processing is complete,
    periodically printing progress.

    Returns URLs for extracted stem and backing tracks (if any) on success.
    Raises a `RuntimeError` with API error message on processing error.
    """
    url_for_check = URL_API + "check/?"
    query_args = {"id": file_id}
    encoded_args = urlencode(query_args)

    while True:
        with urlopen(url_for_check + encoded_args) as response:
            check_result = json.load(response)

        if check_result["status"] == "error":
            raise RuntimeError(check_result["error"])

        task_state = check_result["task"]["state"]

        if task_state == "error":
            raise RuntimeError(check_result["task"]["error"])

        if task_state == "progress":
            progress = int(check_result["task"]["progress"])
            if progress == 0:
                print(f"%split_waiting {stem}")
            else:
                print(f"%split_progress {stem} {progress}%")

        if task_state == "success":
            print(f"%split_progress {stem} 100%")
            stem_track_url = check_result["split"]["stem_track"]
            back_track_url = check_result["split"]["back_track"]
            return stem_track_url, back_track_url

        time.sleep(10)


def get_filename_from_content_disposition(header):
    """
    Extracts the filename from a Content-Disposition header.
    """
    match = re.search(r'filename[^;=\n]*=[\'"]?([^;\'"\n]*)[\'"]?', header)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid header Content-Disposition")


def download_file(url_for_download, output_path):
    with urlopen(url_for_download) as response:
        filename = get_filename_from_content_disposition(
            response.headers["Content-Disposition"]
        )
        filename = filename.replace("_split_by_lalalai", "")
        filename = filename.replace("_no_", "_all_but_", 1)
        filename = filename.replace(".aiff", ".aif", 1)
        file_path = os.path.join(output_path, filename)
        with open(file_path, "wb") as f:
            while chunk := response.read(8196):
                f.write(chunk)
    return file_path


def batch_process_multiple_stems(
    license, input_path, output_path, stems, backing_tracks, filter_type, splitter
):
    """
    Processes an audio file specified by `input_path` and splits it into
    multiple stems using the Lalal.ai API.  The stems to be extracted are
    specified by the `stems` list, and any backing tracks (a version of the
    song that contains everything but the stem)) are specified by the
    `backing_tracks` list. The API splits the audio using the neural network
    specified by `splitter`, and applies a filter of mild, normal, or
    aggressive strength as specified by `filter_type`.

    The resulting stem tracks and backing tracks (if specified) are
    downloaded to the `output_path` directory.
    """
    # Validate stems and backing_tracks
    invalid_stem = validate_stems(stems)
    if invalid_stem:
        raise ValueError(f"Unrecognized stem: {invalid_stem}")

    invalid_track = validate_stems(backing_tracks)
    if invalid_track:
        raise ValueError(f"Unrecognized backing track: {invalid_track}")

    # Upload the file
    print(f'%uploading "{input_path}"')
    file_id = upload_file(file_path=input_path, license=license)
    #print(f"The file has been successfully uploaded (file id: {file_id})")
    print(f'%uploaded {file_id}')

    # Split the file for each stem
    for i in range(len(stems)):
        stem = stems[i]
        #print(f'Processing the file for stem "{stem}"...')
        print(f'%split_start {stem}')
        if i == 0:
            split_file(file_id, license, stem, filter_type, splitter)

        stem_track_url, back_track_url = check_file(stem, file_id)

        if i + 1 < len(stems):
            next_stem = stems[i + 1]
            #print(f'Early start processing of next stem extraction "{next_stem}"...')
            print(f'%split_start {next_stem}')
            split_file(file_id, license, next_stem, filter_type, splitter)

        #print(f'Downloading stem {stem} "{stem_track_url}"')
        print(f'%download_start stem {stem}')
        downloaded_file = download_file(stem_track_url, output_path)
        print(f'%download_complete stem {stem}')


        if stem in backing_tracks:
            #print(f'Downloading backing track {stem} "{back_track_url}"')
            print(f'%download_start back_track {stem}')
            downloaded_file = download_file(back_track_url, output_path)
            print(f'%download_complete back_track {stem}')

        #print(f'The file has been successfully split for stem "{stem}"')
        print(f'%split_complete {stem}')
    print(f'%unmixing_complete')


