import argparse
import hashlib
import json
import os

import magic


def get_lower_extension(file_path):
    file_name, extension = os.path.splitext(file_path)

    return extension.lower()


def calculate_md5(file_path):
    file = open(file_path, 'rb')

    hash = hashlib.md5()
    hash.update(file.read())
    return hash.hexdigest()


def get_mediatype(file_path):
    extension = get_lower_extension(file_path)

    if extension == '.csv':
        return 'text/csv'

    detected = magic.detect_from_filename(file_path)
    return detected.mime_type


def get_encoding(file_path):
    detected = magic.detect_from_filename(file_path)
    return detected.encoding


def get_profile(file_path):
    extension = get_lower_extension(file_path)

    if extension in ('.csv', '.dat'):
        return 'tabular-data-resource'
    else:
        return 'data-resource'


def get_format(file_path):
    extension = get_lower_extension(file_path)

    return extension[1:]


def generate_frictionless_resource(data_directory, file_path):
    frictionless_file = {}

    frictionless_file['name'] = os.path.basename(file_path).lower().replace('.', '_')
    frictionless_file['path'] = file_path[len(data_directory) + 1:]
    frictionless_file['format'] = get_format(file_path)
    frictionless_file['mediatype'] = get_mediatype(file_path)
    frictionless_file['encoding'] = get_encoding(file_path)
    frictionless_file['bytes'] = os.stat(file_path).st_size
    frictionless_file['hash'] = calculate_md5(file_path)
    frictionless_file['profile'] = get_profile(file_path)

    if frictionless_file['profile'] == 'tabular-data-resource':
        frictionless_file['schema'] = 'tableschema.json'

    return frictionless_file


def generate_resources(data_directory, destination_file):
    resources = []

    for root, directories, files in os.walk(data_directory):
        for file in files:
            resources.append(generate_frictionless_resource(data_directory, os.path.join(root, file)))

    datapackage = {}
    datapackage['resources'] = resources

    output_file = open(destination_file, 'w')

    json.dump(datapackage, output_file, indent=2)

    output_file.close()


if __name__ == '__main__':
    main_parser = argparse.ArgumentParser()

    main_parser.add_argument('data_directory')
    main_parser.add_argument('destination_file')

    args = main_parser.parse_args()

    generate_resources(args.data_directory, args.destination_file)
