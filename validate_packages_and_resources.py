import os

from datapackage import Package

from datapackage import exceptions


def find_data_packages():
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file == 'datapackage.json':
                yield os.path.join(root, file)


def validate_data_packages():
    for datapackage_path in find_data_packages():
        package = Package(datapackage_path)

        for resource in package.resources:
            if resource.valid is False:
                print(f'Invalid resource {resource} in {datapackage_path}')
                continue

            if resource.tabular is False:
                continue

            try:
                resource.read()
            except exceptions.ValidationError as exception:
                for error in exception.errors:
                    print(error)
            except exceptions.CastError as exception:
                for error in exception.errors:
                    print(error)

if __name__ == '__main__':
    validate_data_packages()


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
