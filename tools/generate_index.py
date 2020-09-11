#!/usr/bin/env python3

import glob
import json
import os
import git
import time


def get_git_commit_time(path):

    repo = git.Repo(search_parent_directories=True)

    commit_linux_timestamp = next(repo.iter_commits(paths=path)).committed_date
    commit_time = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.gmtime(commit_linux_timestamp))

    return commit_time

def tableschemas_file_names(directory, datapackage):
    tableschemas = []

    for resource in datapackage['resources']:
        if 'profile' in resource and resource['profile'] == 'tabular-data-resource':
            tableschemas.append(os.path.join(directory, resource['schema']))

    return tableschemas

def newest_tableschema_update(tableschema_paths):
    if len(tableschema_paths) == 0:
        return None

    updates = []

    for tableschema_path in tableschema_paths:
        update = get_git_commit_time(tableschema_path)
        updates.append(update)

    updates.sort(reverse=True)

    return updates[0]

def generate_index():
    result = []

    for directory in glob.glob('10.5281_zenodo*'):
        print(directory)
        datapackage_path = os.path.join(directory, 'datapackage.json')
        datapackage = json.load(open(datapackage_path))
        tableschema_paths = tableschemas_file_names(directory, datapackage)
        tableschema_lastupdate = newest_tableschema_update(tableschema_paths)
        version = datapackage['version']
        datapackage_lastupdate = get_git_commit_time(datapackage_path)

        result.append({'directory': directory,
                       'version': version,
                       'x_spi_datapackage_lastupdate': datapackage_lastupdate,
                       'x_spi_tableschema_lastupdate': tableschema_lastupdate
                       })

    json.dump(result, open('index.json', 'w'), sort_keys=True, indent=2)


if __name__ == '__main__':
    generate_index()
