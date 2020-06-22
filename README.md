master: [![validation](https://github.com/Swiss-Polar-Institute/frictionless-data-packages/workflows/validation/badge.svg?branch=master)](https://github.com/Swiss-Polar-Institute/frictionless-data-packages/actions?query=branch%3Amaster)
dev: [![validation](https://github.com/Swiss-Polar-Institute/frictionless-data-packages/workflows/validation/badge.svg?branch=dev)](https://github.com/Swiss-Polar-Institute/frictionless-data-packages/actions?query=branch%3Adev)
[![License: CC0-1.0](https://img.shields.io/badge/License-CC0--1.0-blue.svg)](https://creativecommons.org/publicdomain/zero/1.0/)

# frictionless-data-packages

This repository describes a dataset (otherwise known as a data package) and tabular data files using the [Frictionless Data](https://frictionlessdata.io/) schemas. 

Table schema: https://specs.frictionlessdata.io/table-schema/

Data package schema: https://specs.frictionlessdata.io/data-package/

Each directory within this repository refers to a published dataset that is named by its Digital Object Identifier (DOI). Note that the "/" from the DOI has been replaced by "_", so the directory 10.5281_zenodo.3634411 refers to the DOI [10.5281/zenodo.3634411](https:doi.org/10.5281/zenodo.3634411).

Each dataset is described by a JSON file, datapackage.json. The tabular data files are described by a separate JSON file, tableschema.json.

Dataset files that are described in each data package, can be found through their DOI or by using the URL in the field "homepage" in the datapackage.json file.

### EMODNet Physics specifics
In order for the data to be ingested into EMODNet Physics, a time column is required (seconds since 1970-01-01 in UTC), in accordance with the [CF standard names](https://cfconventions.org/standard-names.html).

A Python script, `convert_isodatetime_in_file_to_timesince.py` is provided to convert the date_time field (in ISO 8601 format, YYYY-MM-DDT:hh:mm:ss+00:00) to time (secs since 1970-01-01 in UTC) and add a time field to the data file. 

# Validation

Install requirements. For example create a `venv`, activate it and add use pip to install the requirements:
```
python3 -m venv venv
. venv/bin/activate
pip3 install -r requirements.txt
```

To validate the `datapackage` and `tableschema` run the python script `validate_packages_and_resources.py`
```
python3 validate_packages_and_resources.py --dois doi1 doi2 doi3
```
using the directory names for each `datapackage` used in this repository, eg.
```
python3 validate_packages_and_resources.py --dois 10.5281_zenodo.3843376
```

If you need further checks to validate the Frictionless Data schema, then go to a directory and validate the `datapackage` and `tableschema`:
```
datapackage validate datapackage.json
tableschema validate tableschema.json
```

[GoodTables](https://frictionlessdata.io/tooling/goodtables/) can also be used to validate the `datapackage` and `tableschema` but this does not validate the SPI-specific fields: 
```
goodtables validate datapackage
tableschema validate tableschema
```
# Use of DOIs within repository

Each directory within the repository is named using the *parent DOI* of the dataset. Currently (as of June 2020) we are only dealing with datasets here that are published on [Zenodo](https://zenodo.org/communities/spi-ace?page=1&size=200). Within Zenodo, each dataset has a *parent DOI* which will always resolve to the latest version of a dataset. 

For example: [10.5281/zenodo.3367283](https://doi.org/10.5281/zenodo.3367283) is the *parent DOI* of this dataset, which as of June 2020 has two different versions: [1.0](https://doi.org/10.5281/zenodo.3367284) and [1.1](https://doi.org/10.5281/zenodo.3895704).

Within the Frictionless Data Package schema, the *specific version DOIs* are used to avoid confusion in the following fields: 
- ```id```, eg. ```"id": "https://doi.org/10.5281/zenodo.3250980"```
- ```homepage```, eg. ```"homepage": "https://doi.org/10.5281/zenodo.3250980"```
- within the ```citation```, eg. ```"x_spi_citation": "Rickli, Jörg, Janssen, David J., Hassler, Christel, Ellwood, Michael, & Jaccard, Samuel L. (2019). Seawater chromium concentrations and isotope compositions in the Southern Ocean during the austral summer of 2016/2017, on board the Antarctic Circumnavigation Expedition (ACE). (Version 1.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.3250980"```

The ```index.json``` file can be consulted for the latest version of each dataset where they are listed with the *parent DOI* and latest version number. 
