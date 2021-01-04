import argparse
import hashlib
import importlib
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


def generate_frictionless_resource(data_directory, file_path, extra_module):
    resource = {}

    resource['name'] = os.path.basename(file_path).lower().replace('.', '_')
    resource['path'] = file_path[len(data_directory) + 1:]
    resource['title'] = None
    resource['description'] = None
    resource['format'] = get_format(file_path)
    resource['mediatype'] = get_mediatype(file_path)
    resource['encoding'] = get_encoding(file_path)
    resource['bytes'] = os.stat(file_path).st_size
    resource['hash'] = calculate_md5(file_path)
    resource['profile'] = get_profile(file_path)

    if resource['profile'] == 'tabular-data-resource':
        resource['schema'] = 'tableschema.json'

    for function, field in extra_functions().items():
        value = getattr(extra_module, function, lambda r: None)(resource)

        if value:
            resource[field] = value
        else:
            del resource[field]

    return resource


def extra_functions():
    return {'get_title': 'title',
            'get_description': 'description'
            }


def generate_resources(data_directory, destination_file, extra_module_path):
    resources = []

    extra_module = None

    if extra_module_path:
        extra_module_path = extra_module_path.replace('.py', '')
        extra_module = importlib.import_module(extra_module_path, package='extra')

    for root, directories, files in os.walk(data_directory):
        for file in files:
            resources.append(generate_frictionless_resource(data_directory, os.path.join(root, file), extra_module))

    datapackage = {}
    datapackage['resources'] = resources

    output_file = open(destination_file, 'w')

    json.dump(datapackage, output_file, indent=2)

    output_file.close()


if __name__ == '__main__':
    main_parser = argparse.ArgumentParser()

    main_parser.add_argument('data_directory')
    main_parser.add_argument('destination_file')
    main_parser.add_argument('--import_module')

    args = main_parser.parse_args()

    generate_resources(args.data_directory, args.destination_file, args.import_module)
