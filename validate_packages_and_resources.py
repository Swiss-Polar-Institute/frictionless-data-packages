from datapackage import Package
from datapackage import validate, exceptions


package = Package('/home/jen/projects/spi_data_management/git/frictionless-data-packages/10.5281_zenodo.3250980/datapackage.json')
package.get_resource('ace_chromium_isotope_concentration').read()

descriptor = package.descriptor

try:
    valid = validate(descriptor)
except exceptions.ValidationError as exception:
   for error in exception.errors:
      print(error)


