#!/usr/bin/env python3

import glob
import json
import os


def generate_index():
    result = []

    for directory in glob.glob('10.5281_zenodo*'):
        print(directory)
        datapackage_path = os.path.join(directory, 'datapackage.json')
        datapackage = json.load(open(datapackage_path))
        version = datapackage['version']
        x_spi_datapackage_lastupdate = '2020-08-05 10:00:00'
        x_spi_tableschema_lastupdate = '2020-08-05 11:00:00'

        result.append({'directory': directory,
                       'version': version,
                       'x_spi_datapackage_lastupdate': x_spi_datapackage_lastupdate,
                       'x_spi_tableschema_lastupdate': x_spi_tableschema_lastupdate
                       })

    json.dump(result, open('index.json', 'w'), sort_keys=True, indent=2)


if __name__ == '__main__':
    generate_index()
