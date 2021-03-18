# Structure of a dataset

On Github, each directory is named in the format `10.5281_zenodo.maindoi`
where the `maindoi` is the primary DOI which refers to dataset, rather than a particular version. In Zenodo, this will automatically take a user to the latest version. 

Within these directories, the JSON files describing the Frictionless data package and table schemas can be found. A standard case would contain one of each of these files.

These JSON files are then published alongside the data files in the Zenodo dataset publication. Often, the JSON files are put inside a folder within a Zip file named `fricitonless_data_schema.zip` (this was originally because there was no way within the JSON files or the dataset itself to describe where these schemas originated from; more recently we have included a separate field, `x_spi_schema_url` which provides a URL directly to the schema). 

### Standard example

**Github**: https://github.com/Swiss-Polar-Institute/frictionless-data-packages/tree/master/10.5281_zenodo.3843262

```
|-- 10.5281_zenodo.3843263
|   |-- datapackage.JSON
|   |-- tableschema.JSON
```

**Zenodo** dataset publication: https://doi.org/10.5281/zenodo.3843263
```
|-- https://doi.org/10.5281/zenodo.3843263
|   |-- ace_bromine_monoxide_atmospheric_measurements.csv
|   |-- data_file_header.txt
|   |-- fricitonless_data_schema.zip
|   |   |-- fricitonless_data_schema
|   |   |   |-- datapackage.JSON
|   |   |   |-- tableschema.JSON
|   |-- README.pdf
|   |-- README.txt
``` 

## Use of structure to access the data files

The JSON files within `fricitonless_data_schema.zip` are not used as part of the transfer of data to EMODnet Physics. These files are provided for a user that downloads the data from Zenodo. 

JSON files on Github are used by EMODnet Physics to get metadata (within both of the JSON files) and the data files (using the `path` field within `datapackage.json`). Hence, the contents of `path` differ between the JSON files on Github and Zenodo. 

**Github**: the URL goes directly to the file download
```
"path": "https://zenodo.org/record/3843263/files/ace_bromine_monoxide_atmospheric_measurements.csv?download=1"
```

**Zenodo**: the path to the file is relative (although this doesn't generally take into account the Zip file containing the Frictionless JSON schemas)
```
"path": "ace_bromine_monoxide_atmospheric_measurements.csv",
```

## Description of the data files with a tableschema

Data files are described by the Frictionless tableschema. Generally within a dataset, there is only one type of data file and therefore only one tableschema description. The tableschema file which describes a particular data file, or set of data files, is identified within the `datapackage.json`. A dataset can contain multiple data files that are described by the same `tableschema.json`.

**Example of identifying the schema which describes a data file**

Here we can see that the resource with the name `ace_bromine_monoxide_atmospheric_measurements` is a `tabular-data-resource` that is described by the schema `tableschema.json`:
```json
"resources": [
    {
      "name": "ace_bromine_monoxide_atmospheric_measurements",
      "path": "https://zenodo.org/record/3843263/files/ace_bromine_monoxide_atmospheric_measurements.csv?download=1",
      "title": "ACE bromine monoxide (BrO) atmospheric measurements",
      "description": "Data file containing atmospheric bromine monoxide (BrO) measurements from ACE",
      "format": "csv",
      "mediatype": "text/csv",
      "encoding": "ASCII",
      "bytes": 4727,
      "hash": "bf91ff3bca39d5e330e627a9a32256b9",
      "profile": "tabular-data-resource",
      "schema": "tableschema.json"
    },
``` 

# Structure of a dataset with multiple tableschemas

### Multiple tableschemas within a dataset

Some datasets contain data files that differ in their format, and therefore are described by different `tableschema.json` files. These JSON files are still contained within the dataset but are named differently in order to distinguish between them. As with the datasets where only one `tableschema.json` file exists, the particular file is identified within the `datapackage.json`. 

For now, no examples of datasets like this have been pushed to the master branch. There are examples that can be found in other branches though, such as `dev-wip-1494924`: https://github.com/Swiss-Polar-Institute/frictionless-data-packages/tree/dev-wip-1494924
```
|-- 10.5281_zenodo.1494923
|   |-- datapackage.json
|   |-- tableschema_csv_other.json
|   |-- tableschema_uw.json
```
In this case there are a number of resources that are described by one of these tableschemas: 
```json
"resources": [
    {
      "name": "ace_18_data_salinity_ctd",
      "path": "ace_18_data_salinity_ctd_20200820.csv",
      "title": "Seawater sample salinity CTD",
      "description": "Salinity measurements of seawater samples collected from the Niskin bottles mounted on the CTD rosette",
      "format": "csv",
      "mediatype": "text/csv",
      "encoding": "utf-8",
      "bytes": 59718,
      "hash": "fa8b1bdc73cb109013c38e29ef5b7901",
      "profile": "tabular-data-resource",
      "schema": "tableschema_csv_other.json"
    },
    {
      "name": "ace_18_data_salinity_other",
      "path": "ace_18_data_salinity_other_20200820.csv",
      "title": "Seawater sample salinity other source",
      "description": "Salinity measurements of miscellaneous samples: Duplicate seawater samples; seawater bucket sample from Cumberland Bay, South Georgia; seawater samples from Niskin bottles mounted on the trace-metal rosette",
      "format": "csv",
      "mediatype": "text/csv",
      "encoding": "utf-8",
      "bytes": 12007,
      "hash": "1999e3796418d32b32cbc03acd5eb74c",
      "profile": "tabular-data-resource",
      "schema": "tableschema_csv_other.json"
    },
    {
      "name": "ace_18_data_salinity_uw",
      "path": "ace_18_data_salinity_uw_20200820.csv",
      "title": "Seawater sample salinity underway",
      "description": "Seawater salinity data from underway samples collected during ACE",
      "format": "csv",
      "mediatype": "text/csv",
      "encoding": "utf-8",
      "bytes": 57943,
      "hash": "45b7f6f4c60b98f221d1d98166ef537c",
      "profile": "tabular-data-resource",
      "schema": "tableschema_uw.json"
    },
```

 ### No data in zip file

The structure of these datasets is similar to those that only use one tableschema to describe them. 

**Github**:
```
|-- 10.5281_zenodo.1494923
|   |-- datapackage.json
|   |-- tableschema_csv_other.json
|   |-- tableschema_uw.json
```

**Zenodo**:
All JSON files are packaged in a zip file and the files are available to download individually from Zenodo.
```
|-- https://doi.org/10.5281/zenodo.1494924
|   |-- ace_18_data_salinity_ctd_20200820.csv
|   |-- ace_18_data_salinity_other_20200820.csv
|   |-- ace_18_data_salinity_uw_20200820.csv
|   |-- data_file_header.txt
|   |-- figure1.pdf
|   |-- figure2.pdf
|   |-- figure3.pdf
|   |-- figure4.pdf
|   |-- figure5.pdf
|   |-- figure6.pdf
|   |-- frictionless_data_schema.zip
|   |   |-- datapackage.json
|   |   |-- tableschema_csv_other.json
|   |   |-- tableschema_uw.json
|   |-- README.txt
```

 ### Data in zip file