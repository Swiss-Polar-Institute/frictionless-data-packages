#!/usr/bin/env python3

# Very quick and dirty script to validate data packages
# This is part of a pilot - it needs proper re-writing if we keep using this

import argparse
import http.client
import json
import os
import sys
import time

import goodtables
import tabulator
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
        print('----')

    print()
    print('Total number of errors:', len(errors))


def add_error(errors, error, datapackage, resource=None):
    errors.append({'datapackage': datapackage,
                   'error': error,
                   'resource': resource}
                  )


def extra_validation_package(package, errors):
    spi_mandatory_attributes = ['x_spi_platform_code', 'x_spi_type', 'x_spi_platform_name', 'x_spi_citation', 'version',
                                'x_spi_assembly_center', 'x_spi_assembly_center_link', 'x_spi_dataset_owner',
                                'x_spi_schema_url']
    for spi_attribute in spi_mandatory_attributes:
        if spi_attribute not in package.descriptor:
            add_error(errors, f'Missing mandatory SPI package attribute: {spi_attribute}', package.base_path)

    for attribute_name in package.descriptor:
        if attribute_name.startswith('x_spi_') and attribute_name not in spi_mandatory_attributes:
            add_error(errors,
                      f'There is an attribute in a package that stats with x_spi_ ({attribute_name}) but is not one of the SPI attributes',
                      package.base_path)


def extra_validation_table(package, table, errors):
    spi_mandatory_attributes = ['x_spi_netcdf_name']
    spi_attributes = spi_mandatory_attributes + ['x_spi_cf_standard_name', 'x_spi_cf_unit', 'x_spi_cf_attribute',
                                                 'x_spi_emodnet_visualise_variable']

    if table.schema is None:
        return

    for field in table.schema.fields:
        for attribute_name in field.descriptor:
            if attribute_name.startswith('x_spi_') and attribute_name not in spi_attributes:
                add_error(errors,
                          f'There is an attribute in a field starting with x_spi_ ({attribute_name}) but it is not one of the SPI attributes',
                          package.base_path, f'{table.name}-{field.name}')

        for spi_attribute in spi_mandatory_attributes:
            # It makes sure that attribute are there
            if spi_attribute not in field.descriptor:
                add_error(errors, f'Missing mandatory SPI field attribute: {spi_attribute}', package.base_path,
                          f'{table.name}-{field.name}')

            if spi_attribute == 'x_spi_netcdf_name' and spi_attribute in field.descriptor and ' ' in field.descriptor[
                'x_spi_netcdf_name']:
                add_error(errors, f'x_spi_netcdf_name value cannot contain spaces', package.base_path,
                          f'{table.name}-{field.name}')


def doi_from_datapackage_path(datapackage_path):
    return datapackage_path.split('/')[1]


def validate_using_goodtables(datapackage_path, errors):
    try:
        result = goodtables.validate(datapackage_path)
    except http.client.IncompleteRead as e:
        print(e)
        add_error(errors, f'Error reading remote file', datapackage_path)
        return

    if result['valid'] is False:
        add_error(errors,
                  'goodtables.py returned valid=False. Next errors might contain the errors if they are in tables',
                  datapackage_path)

        for table in result['tables']:
            if 'errors' in table:
                for error in table['errors']:
                    add_error(errors, f'goodtables.py returned an error - {error["message"]}', datapackage_path,
                              table['resource-name'])


def validate_table(package, resource, errors):
    try:
        resource.read()
        print(f'Tableschema: {resource.name} is valid!')
        time.sleep(2)  # hope to avoid HTTP 429
    except (exceptions.ValidationError, exceptions.CastError) as exception:
        for error in exception.errors:
            add_error(errors, error, package.base_path, resource.name)
    except tabulator.exceptions.SourceError as exception:
        print(f'--------- Cannot download: {resource.source}')
        print('error is ignored')
        print(exception)

        # add_error(errors, f'Cannot download file: {resource.source}', package, resource.name)


def validate_data_package(datapackage_path, errors):
    print('* DATAPACKAGE', datapackage_path)

    if '10.5281_zenodo.5109385' in datapackage_path:
        print('Skip:', datapackage_path)
        # goodtables is running out of memory for this package
        # we should migrate to the new framework and see if this problem
        # happens as well
        return

    package = Package(datapackage_path)
    print('opened package')

    if package.valid is False:
        add_error(errors, f'Invalid package: {package}', datapackage_path)
        return

    print('will do extra_validation_package')
    extra_validation_package(package, errors)
    print('finished extra validation')

    for resource in package.resources:
        print(f'Resource: {resource.name} ')
        if resource.valid is False:
            error = f'Invalid resource {resource} in {package.base_path}'
            add_error(errors, error, package.base_path)

        if resource.profile.title != 'Tabular Data Resource':
            print(f'Ignoring resource: {resource.name} because it is not "tabular-data-resource" profile')
            continue

        if resource.tabular is False:
            print(f'Ignoring resource: {resource.name} because it is not tabular type')
            continue

        print('Before validate table')
        validate_table(package.base_path, resource, errors)
        print('After validate table')
        extra_validation_table(package, resource, errors)


def calculate_size_of_datapacakge_mb(datapackage_path):
    content = json.load(open(datapackage_path))

    total_size = 0

    for resource in content['resources']:
        total_size += int(resource.get('bytes', 0))

    return total_size / 1024 / 1024


def validate_data_packages(dois):
    errors = []

    for datapackage_path in find_data_packages():
        doi = doi_from_datapackage_path(datapackage_path)
        if dois is not None and doi not in dois:
            print('::warning::Skipping validation of', doi)
            continue

        validate_data_package(datapackage_path, errors)

        size_of_data_package_mb = calculate_size_of_datapacakge_mb(datapackage_path)
        print(f'Calculated size: {size_of_data_package_mb} MB')
        if size_of_data_package_mb > 100:
            print(f'::warning::Skipping validation of {doi} size is too big ({size_of_data_package_mb}')
            continue
        validate_using_goodtables(datapackage_path, errors)

    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dois', nargs='+', help='Check only for this or these DOIs', required=False)

    args = parser.parse_args()

    exitcode = 0
    errors = validate_data_packages(args.dois)

    print_summary_errors(errors)

    if len(errors) > 0:
        exitcode = 1

    sys.exit(exitcode)
