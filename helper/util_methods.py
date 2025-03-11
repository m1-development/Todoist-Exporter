import json
import os
import time

import requests

from helper import logger
from model.internal_classes import ExporterConfiguration


class ConfigException(Exception):
    pass


def read_exporter_configuration() -> ExporterConfiguration:
    todoist_token = None
    export_directory = "export"
    download_attachments = True

    config_file = "exporter_configuration.json"
    try:
        with open(config_file, 'r') as file:
            json_configuration = json.load(file)

            if "todoist_token" not in json_configuration:
                raise ConfigException("No access token for TodoIst found in '{config_file}' -> See Readme.md.")

            todoist_token = json_configuration["todoist_token"]
            if "export_directory" in json_configuration:
                export_directory = json_configuration["export_directory"]
            if "download_attachments" in json_configuration:
                download_attachments = json_configuration["download_attachments"]

    except FileNotFoundError:
        raise ConfigException(f"There is no configuration file '{config_file}' -> See Readme.md.")

    return ExporterConfiguration(todoist_token,
                                 export_directory,
                                 download_attachments)


def call_api_with_retries(api_func, **kwargs):
    delay = 2
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return api_func(**kwargs)

        except Exception as e:
            logger.log_error(f"Versuch {attempt + 1} fehlgeschlagen: {e}")
            if attempt < max_retries - 1:
                logger.log_info(f"Warte {delay} Sekunde(n) vor dem nächsten Versuch...")
                time.sleep(delay)
            else:
                logger.log_error(f"Maximale Anzahl an Versuchen erreicht. Abbruch.")
                return None


def download_attachment(token, comment_id, file_url, export_directory, path_divider):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    filename_from_url = file_url.split("/")[-1]
    local_file_name = "comment_" + comment_id + "_attachment_" + filename_from_url
    file_path = export_directory + path_divider + local_file_name
    if not os.path.isfile(file_path):
        response = requests.get(file_url, headers=headers, stream=True)

        if response.status_code == 200:
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            logger.log_info(f"Datei '{file_path}' wurde erfolgreich heruntergeladen.")
        else:
            logger.log_error(f"Fehler beim Herunterladen: {response.status_code} - {response.text}")

    return local_file_name


def format_newline_text_to_multiline_list(newline_text):
    separated_lines = newline_text.split("\n")
    return list(filter(None, separated_lines))


def remove_empty_fields(data):
    if isinstance(data, dict):
        return {k: remove_empty_fields(v) for k, v in data.items() if v not in [None, [], {}, ""]}
    elif isinstance(data, list):
        return [remove_empty_fields(item) for item in data if item not in [None, [], {}, ""]]
    else:
        return data