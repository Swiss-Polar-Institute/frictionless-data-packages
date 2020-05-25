import os
import sys

from datapackage import Package
from datapackage import exceptions
import argparse

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


def extra_validation(package, errors):
    for spi_attribute in ['x_spi_platform_code', 'x_spi_type', 'x_spi_platform_name', 'x_spi_citation']:
        if spi_attribute not in package.attributes:
            add_error(errors, f'Missing mandatory SPI attribute: {spi_attribute}', package.base_path)


def validate_data_packages(dois):
    errors = []
    for datapackage_path in find_data_packages():
        doi = datapackage_path.split('/')[1]
        if dois is not None and doi not in dois:
            print('Skipping', doi)
            continue

        print('* DATAPACKAGE', datapackage_path)
        package = Package(datapackage_path)

        if package.valid is False:
            add_error(errors, f'Invalid package: {package}', datapackage_path)
            continue

        extra_validation(package, errors)

        for resource in package.resources:
            print(f'Resource: {resource.name} ')
            if resource.valid is False:
                error = f'Invalid resource {resource} in {package.base_path}'
                add_error(errors, error, package.base_path)

            if resource.tabular is False:
                print(f'Ignoring resource: {resource.name} because it is not tabular type')
                continue

            try:
                resource.read()
                print(f'Tableschema: {resource.name} is valid!')
            except (exceptions.ValidationError, exceptions.CastError) as exception:
                for error in exception.errors:
                    add_error(errors, error, package.base_path, resource.name)

    print_summary_errors(errors)
    return len(errors)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dois', nargs='+', help='Check only for this or these DOIs', required=False)

    args = parser.parse_args()

    exitcode = 0
    errors_count = validate_data_packages(args.dois)
    if errors_count > 0:
        exitcode = 1

    sys.exit(exitcode)

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
