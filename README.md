# frictionless-data-packages

This repository describes a dataset (otherwise known as a data package) and tabular data files using the [Frictionless Data](https://frictionlessdata.io/) schemas. 

Table schema: https://specs.frictionlessdata.io/table-schema/


Data package schema: https://specs.frictionlessdata.io/data-package/

Each directory within this repository refers to a published dataset that is named by its Digital Object Identifier (DOI). Note that the "/" from the DOI has been replaced by "_", so the directory 10.5281_zenodo.3634411 refers to the DOI [10.5281/zenodo.3634411](https:doi.org/10.5281/zenodo.3634411).

Each dataset is described by a JSON file, datapackage.json. The tabular data files are described by a separate JSON file, tableschema.json.

Dataset files that are described in each data package, can be found through their DOI or by using the URL in the field "homepage" in the datapackage.json file.

### EMODNet specifics
In order for the data to be ingested into EMODNet, a time column is required (seconds since 1970-01-01 in UTC), in accordance with the [CF standard names](http://cfconventions.org/standard-names.html).

A Python script, `convert_isodatetime_in_file_to_timesince.py` is provided to convert the date_time field (in ISO 8601 format, YYYY-MM-DDT:hh:mm:ss+00:00) to time (secs since 1970-01-01 in UTC) and add a time field to the data file. 
