#!/usr/bin/env python3

import glob
import json
import os
import git
import time


def get_git_commit_time(path):

    repo = git.Repo(search_parent_directories=True)
    # headcommit = repo.head.commit
    # commit_time = time.strftime("%a, %d %b %Y %H:%M", time.gmtime(headcommit.committed_date))
    commit_linux_timestamp = next(repo.iter_commits(paths=path)).committed_date
    commit_time = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.gmtime(commit_linux_timestamp))

    return commit_time


def generate_index():
    result = []

    for directory in glob.glob('10.5281_zenodo*'):
        print(directory)
        datapackage_path = os.path.join(directory, 'datapackage.json')
        datapackage = json.load(open(datapackage_path))
        # TODO - amend for if there are no, or more than one tableschema files within the path
        tableschema_path = os.path.join(directory, 'tableschema.json')
        version = datapackage['version']
        datapackage_lastupdate = get_git_commit_time(datapackage_path)
        tableschema_lastupdate = get_git_commit_time(tableschema_path)

        result.append({'directory': directory,
                       'version': version,
                       'x_spi_datapackage_lastupdate': datapackage_lastupdate,
                       'x_spi_tableschema_lastupdate': tableschema_lastupdate
                       })

    json.dump(result, open('index.json', 'w'), sort_keys=True, indent=2)


if __name__ == '__main__':
    generate_index()
