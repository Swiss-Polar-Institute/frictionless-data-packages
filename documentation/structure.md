## Structure of a dataset

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

## Description of the data files with Tableschema

Data files are described by the Frictionless Tableschema. Generally within a dataset, there is only one type of data file and therefore only one tablschema description. The tableschema file which describes a particular data file, or set of data files, is identified within the `datapackage.json`.

### Example of identifying the schema which describes a data file

Here we can see that the resource with the name `ace_bromine_monoxide_atmospheric_measurements` is a `tabular-data-resource` that is described by the schema `tableschema.json`:
```
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




 