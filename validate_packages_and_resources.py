import os
import sys

from datapackage import Package
from datapackage import exceptions


def find_data_packages():
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file == 'datapackage.json':
                yield os.path.join(root, file)


def print_summary_errors(errors):
    print()
    print('SUMMARY OF ERRORS')
    print('=================')

    for error in errors:
        print(f'Datapackage: {error["datapackage"]}')
        if error['resource']:
            print(f'Resource: {error["resource"]}')
        print(f'Error: {error["error"]}')

    print()
    print('Total number of errors:', len(errors))


def add_error(errors, error, datapackage, resource=None):
    errors.append({'datapackage': datapackage,
                   'error': error,
                   'resource': resource}
                  )


def validate_data_packages():
    errors = []
    for datapackage_path in find_data_packages():
        print('* DATAPACKAGE', datapackage_path)
        package = Package(datapackage_path)

        for resource in package.resources:
            print(f'Resource: {resource.name} ')
            if resource.valid is False:
                error = f'Invalid resource {resource} in {datapackage_path}'
                add_error(errors, error, datapackage_path)

            if resource.tabular is False:
                print(f'Ignoring resource: {resource.name} because it is not tabular type')
                continue

            try:
                resource.read()
                print('Tableschema: {resource.name} is valid!')
            except (exceptions.ValidationError, exceptions.CastError) as exception:
                for error in exception.errors:
                    add_error(errors, error, datapackage_path, resource.name)

    print_summary_errors(errors)
    return len(errors) == 0


if __name__ == '__main__':
    sys.exit(validate_data_packages())

# package = Package('/home/jen/projects/spi_data_management/git/frictionless-data-packages/10.5281_zenodo.3250980/datapackage.json')
# package.get_resource('ace_chromium_isotope_concentration').read()
#
# descriptor = package.descriptor
#
# try:
#     valid = validate(descriptor)
# except exceptions.ValidationError as exception:
#    for error in exception.errors:
#       print(error)
#
#