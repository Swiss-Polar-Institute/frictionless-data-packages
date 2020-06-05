#!/usr/bin/env python3

import glob
import json
import os


def generate_index():
    result = {}

    for directory in glob.glob('10.5281_zenodo*'):
        print(directory)
        datapackage_path = os.path.join(directory, 'datapackage.json')
        datapackage = json.load(open(datapackage_path))
        version = datapackage['version']

        result[directory] = {'version': version}

    json.dump(result, open('index.json', 'w'), sort_keys=True, indent=2)


if __name__ == '__main__':
    generate_index()
