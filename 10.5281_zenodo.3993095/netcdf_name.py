#!/usr/bin/python3
import json

with open('tableschema_uw.json') as table_schema:
    j = json.load(table_schema)

    for field in j['fields']:
        name = field['name']
        field['x_spi_netcdf_name'] += name

    output = open('tableschema_uw_enhanced.json', 'w')
    json.dump(j, output, indent=2)
    output.close()
