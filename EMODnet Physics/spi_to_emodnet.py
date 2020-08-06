#!/usr/bin/env python
# coding: utf-8
import _locale
_locale._gdl_bak = _locale._getdefaultlocale
_locale._getdefaultlocale = (lambda *args: (_locale._gdl_bak()[0], 'utf8'))
from datapackage import Package
from tableschema import Table
import datetime
import os
import urllib.request
import netCDF4
from netCDF4 import Dataset, num2date, date2num, stringtochar
import re
from datetime import datetime, timedelta
import numpy as np
import sys, getopt
import subprocess
import json
import shutil
import fileinput
import lxml.etree as ET
from xml.etree.ElementTree import ElementTree
from shutil import copyfile

mailText=""

### VARIABLE TO  MODIFY OR PASS ARGUMENT TO SCRIPT ###
id=""
basesavepath=""
xmltemplathepath=""
indexjsonpath=""
erddapdatasetpath=""
newerddapdatasetpath=""

def CreateNetCDF(netcdf,package,resourceData):
    #create netcdf
    print("CreateNetCDF")
    mailText+="CreateNetCDF\n"
    #create dimension
    print("create dimension")
    mailText+="create dimension\n"
    row = netcdf.createDimension("row", None) ##unlimited dimension
    #create global attribute
    print("create global attribute")
    mailText+="create global attribute\n"
    netcdf.cdm_data_type="Other"
    netcdf.Conventions="COARDS, CF-1.6, ACDD-1.3"
    netcdf.creator_type = "institution"  
    if 'x_spi_platform_code' in package.descriptor:
        netcdf.platform_code=package.descriptor['x_spi_platform_code']
    if 'x_spi_platform_name' in package.descriptor:
        netcdf.platform_name=package.descriptor['x_spi_platform_name']
    if 'x_spi_type' in package.descriptor:
        netcdf.type=package.descriptor['x_spi_type']
    if 'x_spi_citation' in package.descriptor:
        netcdf.citation=package.descriptor['x_spi_citation']
    if 'keywords' in package.descriptor:
        netcdf.keywords=','.join(package.descriptor['keywords'])
    if 'contributors' in package.descriptor:
        if 'title' in package.descriptor['contributors'][0]:
            netcdf.creator_name = package.descriptor['contributors'][0]['title']
        if 'path' in package.descriptor['contributors'][0]:
            netcdf.creator_url = package.descriptor['contributors'][0]['path']
        if 'organisation' in package.descriptor['contributors'][0]:
            netcdf.institution = package.descriptor['contributors'][0]['organisation']
    if 'homepage' in package.descriptor:
        netcdf.DOI=package.descriptor['homepage']
        netcdf.infoUrl = package.descriptor['homepage']
    if 'licenses' in package.descriptor:    
        if 'name' in package.descriptor['licenses'][0]:    
            netcdf.license = package.descriptor['licenses'][0]['name']
    if 'description' in package.descriptor:
        netcdf.summary = package.descriptor['description']
    if 'contributors' in package.descriptor:
        netcdf.contributors=str(package.descriptor['contributors'])
    if 'title' in package.descriptor:
        netcdf.title=str(package.descriptor['title'])
    
    #create variables
    print("create variables")
    mailText+="create variables\n"
    netcdf_variables={}
    for field in resourceData.schema.fields:        
        fieldName=field.descriptor['x_spi_netcdf_name']
        if (fieldName==""):
            continue        
        fieldtype=""
        fieldsize=""
        if field.type=="string":
            fieldtype="S1"        
            maxFieldSize=0
            for row in resourceData.iter(keyed = True):
                if len(row[field.name])>maxFieldSize:
                    maxFieldSize=len(row[field.name]) 
            fieldsize=str(maxFieldSize)
        elif field.type=="integer":
            fieldtype="i4"
        elif field.type=="time":
            fieldtype="S1"
            fieldsize="4"
        elif field.type=="datetime":  ##is the time variable
            fieldtype="datetime"
            netcdf_variables['time']=field.name
        elif field.type=="number":
            fieldtype="f8"
        elif field.type=="date":
            fieldtype="S1"
            fieldsize=10

        if fieldtype=="datetime":
            netcdf_variables[field.name]=fieldName
            netcdf_variable = netcdf.createVariable(fieldName,"f8",("row",))
            netcdf_variable._CoordinateAxisType = "Time";
            netcdf_variable.axis = "T";
            netcdf_variable.long_name = "Time";
            netcdf_variable.standard_name = "time";
            netcdf_variable.time_origin = "01-JAN-1970 00:00:00";
            netcdf_variable.units = "seconds since 1970-01-01T00:00:00Z"; 
            continue
        if fieldsize=="":
            netcdf_variables[field.name]=fieldName
            netcdf_variable=netcdf.createVariable(fieldName,fieldtype,("row",))
        else:
            netcdf.createDimension(fieldName + "_strlen", int(fieldsize))
            netcdf_variables[field.name]=fieldName
            netcdf_variable=netcdf.createVariable(fieldName,fieldtype,("row",fieldName + "_strlen",))

        netcdf_variable.description=field.descriptor['description']
        if 'unit' in field.descriptor:
            netcdf_variable.units=field.descriptor['unit']
        if 'x_spi_cf_standard_name' in field.descriptor:
            netcdf_variable.standard_name=field.descriptor['x_spi_cf_standard_name']
        if 'x_spi_cf_unit' in field.descriptor:
            netcdf_variable.units=field.descriptor['x_spi_cf_unit']
        if 'x_spi_cf_attribute' in field.descriptor:
            netcdf_variable.attribute=field.descriptor['x_spi_cf_attribute']
        netcdf_variable.spi_original_name=field.name

    print("fill values")
    mailText+="fill values\n"

    values={}
    values['dummy']=[0]
    for row in resourceData.iter(keyed = True):
        for field in resourceData.schema.fields:
            if not field.name in netcdf_variables:
                continue
            try:
                if netcdf.variables[netcdf_variables[field.name]].standard_name=="time":
                    datetime_value=row[field.name]
                    datetime_value_numeric=date2num([datetime_value],units="seconds since 1970-01-01T00:00:00Z",calendar="gregorian")[0]
                    if netcdf_variables[field.name] in values:
                        values[netcdf_variables[field.name]]=np.append(values[netcdf_variables[field.name]],datetime_value_numeric)
                    else:
                        values[netcdf_variables[field.name]]=[datetime_value_numeric]  
                    continue
            except:
                ("")
            if netcdf.variables[netcdf_variables[field.name]].dtype == "S1":
                value=row[field.name]
                if netcdf_variables[field.name] in values:
                    values[netcdf_variables[field.name]]=np.append(values[netcdf_variables[field.name]],value)
                else:
                    values[netcdf_variables[field.name]]=[value]
            else:
                curValue=row[field.name]
                if curValue==None:
                    if netcdf.variables[netcdf_variables[field.name]].dtype=="int32":                        
                        curValue=netCDF4.default_fillvals['i4']
                if netcdf_variables[field.name] in values:
                    values[netcdf_variables[field.name]]=np.append(values[netcdf_variables[field.name]],curValue)
                else:
                    values[netcdf_variables[field.name]]=[curValue]

    print("populate netcdf variables")
    mailText+="populate netcdf variables\n"
    for field in values:
        if field=="dummy":
            continue
        if netcdf.variables[field].dtype == "S1":
            size=str(netcdf.dimensions[field +'_strlen'].size)
            datain=np.array(values[field],dtype='S' + size)
            netcdf.variables[field][:] = stringtochar(datain) 
        else:
            netcdf.variables[field][:]=values[field]
    print("END")

def CreateERDDAPDataset(netcdf,datasetID):
    print("CreateERDDAPDataset")
    mailText+="CreateERDDAPDataset\n"
    xml=""
    dataVariable=""
    with open(os.path.join(xmltemplathepath,'xml_template.xml'), 'r') as file:
        xml = file.read().replace("[datasetIDNoDot]",datasetID.replace(".","_")).replace("[datasetID]",datasetID)

    for variablename in netcdf.variables:
        variable=netcdf.variables[variablename]
        xml_template = ("<dataVariable><sourceName>" + variable.name + "</sourceName>" + 
                        "<destinationName>" + variable.name + "</destinationName>" +
                        "<dataType>[dataType]</dataType></dataVariable>")
        if variable.dtype == "S1":
            xml_template=xml_template.replace("[dataType]","String")
        elif variable.dtype == "i4":
            xml_template=xml_template.replace("[dataType]","int")
        elif variable.dtype == "f8":
            xml_template=xml_template.replace("[dataType]","double")
        dataVariable=dataVariable+xml_template
    xml=xml.replace("[dataVariable]",dataVariable)
    xml=xml.replace("[title]",netcdf.title)
    with open(os.path.join(basesavepath,id,'ERDDAPdataset.xml'), 'w') as file:
        file.write(xml)
        file.close()   

    date_time = datetime.now().strftime("%Y%m%d%H%M%S")
    copyfile(erddapdatasetpath, erddapdatasetpath + date_time)
    root=ET.parse(erddapdatasetpath + date_time)
    newdataset = ET.fromstring(xml)
    dataset=root.find("./dataset/[@datasetID='" + datasetID + "']")
    if (dataset!=None):
        root.getroot().remove(dataset)
    root.getroot().append(newdataset)
    root.write(erddapdatasetpath + date_time)

    copyfile(erddapdatasetpath + date_time,erddapdatasetpath)
    os.remove(erddapdatasetpath + date_time)
    print("END")
   
def CreateEMODnetPlatform(netcdf,datasetid):
    print("CreateEMODnetPlatform")
    mailText+="CreateEMODnetPlatform\n"
    netcdfvariableskeys=netcdf.variables.keys()
    platformtemplate=json.load(open(os.path.join(xmltemplathepath,'platformtemplate.json')))
    parameters_list=[]    
    for variablename in netcdf.variables:
        variable=netcdf.variables[variablename]        
        if (variable.dtype == "i4" or variable.dtype == "f8") and variable.name!="time" and variable.name!="latitude" and variable.name!="longitude":
            parameters_list.append(variablename)
    parameters=';'.join(parameters_list)         
    
    platformtemplate["PlatformCode"]=getattr(netcdf, "platform_code")
    platformtemplate["PlatformCode_MAP"]=getattr(netcdf, "platform_code")
    platformtemplate["PlatformName"]=getattr(netcdf, "platform_name")                
    platformtemplate["PlatformType"]=getattr(netcdf, "type")
    platformtemplate["URLDWONLOADERDDAP"]="https://erddap.emodnet-physics.eu/erddap/tabledap/" + datasetid + ".csv0?time%2Clatitude%2Clongitude%2C" + parameters.replace(";","%2C") + "&latitude!=NaN&longitude!=NaN&orderByClosest(%22time%2C1%20hour%22)"
    platformtemplate["URLPREVIEWERDDAP"]="https://erddap.emodnet-physics.eu/erddap/tabledap/" + datasetid + ".csv0?time%2Clatitude%2Clongitude%2C" + parameters.replace(";","%2C")
    platformtemplate["ERDDAPM2M"]="https://erddap.emodnet-physics.eu/erddap/tabledap/" + datasetid + ".html"
    #platformtemplate["INFO"]=getattr(netcdf, "")
    platformtemplate["DOCUMENTATIONVALUE"]=documentationvalue

    platformtemplate["DOIs"]=[getattr(netcdf, "DOI")]
    platformtemplate["provider"]="Swiss Polar Institute"
    platformtemplate["piname"]=getattr(netcdf, "creator_name")
    platformtemplate["DataOwnerCode"]="Swiss Polar Institute"
    platformtemplate["WMOPlatformCode"]=""
    platformtemplate["DataAssemblyCenter"]=""
    platformtemplate["Contact"]=""
    platformtemplate["InstitutionReferences"]=""
    platformtemplate["EDMO"]=""
    platformtemplate["InstitutionEDMOCode"]=""
    platformtemplate["Stato"]="T"
    platformtemplate["DataAgeCode"]=""
    platformtemplate["DataOwner"]="Swiss Polar Institute"
    platformtemplate["ProjectCodes"]=[ "SPI" ]

    platformtemplate["Parameters"]=parameters.split(";")
    
    if "depth" in netcdfvariableskeys:
        absolute_difference_function = lambda list_value : abs(list_value - value)
        depths_set=set([])
        depths_steps =[ 0, 5, 10, 20, 30, 40, 50, 100, 250, 500, 1000, 1500, 2000, 2500, 3000 ];
        depths=netcdf.variables["depth"][:]
        for depth in depths:
            value=depth
            closest_value = min(depths_steps, key=absolute_difference_function)
            depths_set.add(closest_value)
        depths_list=list(depths_set) 
        platformtemplate["Depths"]=';'.join([str(i).replace(".0","") for i in depths_list])

    if "latitude" in netcdfvariableskeys:
        platformtemplate["latitude"]=netcdf.variables["latitude"][:][-1]
    if "longitude" in netcdfvariableskeys:
        platformtemplate["longitude"]=netcdf.variables["longitude"][:][-1]

    YearDataMeasureds=set([])
    YearMonthDataMeasureds=set([])
    times_numeric=netcdf.get_variables_by_attributes(axis="T")[0][:]    
    times_datetime=np.array(num2date(times_numeric, units="seconds since 1970-01-01T00:00:00Z",only_use_cftime_datetimes=False))
    platformtemplate["LastDataMeasured"]=times_datetime[-1].strftime("%Y-%m-%d %H:%M:%S")
    YearDataMeasureds_set=set([])
    YearMonthDataMeasureds_set=set([])
    for value in times_datetime:        
        YearDataMeasureds_set.add(str(value.year) )
        YearMonthDataMeasureds_set.add('{:02d}'.format(value.month) + "-" + str(value.year) )
    YearDataMeasureds=list(YearDataMeasureds_set)
    YearDataMeasureds.sort()
    YearMonthDataMeasureds=list(YearMonthDataMeasureds_set)
    YearMonthDataMeasureds.sort()    
    platformtemplate["YearDataMeasureds"]=';'.join(YearDataMeasureds)
    platformtemplate["YearMonthDataMeasureds"]=';'.join(YearMonthDataMeasureds)
    
    #platformtemplate["SeaRegionIDs"]=

    with open(os.path.join(xmltemplathepath,"platforms", datasetid + '.json'), 'w') as outfile:
        json.dump(platformtemplate, outfile)     

    return "0"    

def findVersion(json_object, directory):
    for dict in json_object:
        if dict['directory'] == directory:
            return dict['version']
    return "-1"

###MAIN###
try:
    opts, args = getopt.getopt(sys.argv[1:],"p:x:",["path=","xmlpath="])
    for opt, arg in opts:
        if opt in ("-p", "--path"):
            basesavepath=arg
        if opt in ("-x", "--xmlpath"):
            xmltemplathepath=arg
except getopt.GetoptError:
    print ("no parameters")

indexjson_link="https://raw.githubusercontent.com/Swiss-Polar-Institute/frictionless-data-packages/master/index.json"
savepath_indexjson=os.path.join(indexjsonpath, "index.json")
urllib.request.urlretrieve(indexjson_link, savepath_indexjson)
storedjson=[]
newjson=[]
if os.path.exists(os.path.join(indexjsonpath, "index_stored.json")):
    with open(os.path.join(indexjsonpath, "index_stored.json"), 'r') as file:
        storedjson=json.load(file) 
with open(savepath_indexjson, 'r') as file:
    newjson= json.load(file)

#download documentation
documentation_link="https://raw.githubusercontent.com/Swiss-Polar-Institute/frictionless-data-packages/master/documentation/platform_page_about_spiace_text.html"
savepath_documentation=os.path.join(indexjsonpath, "documentation.txt")
urllib.request.urlretrieve(documentation_link, savepath_documentation)
documentationvalue=""
with open(savepath_documentation, 'r') as file:
    documentationvalue = file.read()

for item in newjson:
    version=findVersion(storedjson,item['directory'])
    if version=="-1" or version!=item['version']:
        id=item['directory']
        print(id)
        mailText+="new version: " + id + "\n"
        datapackage_link="https://raw.githubusercontent.com/Swiss-Polar-Institute/frictionless-data-packages/dev/" + id + "/datapackage.json"
        tableschema_link="https://raw.githubusercontent.com/Swiss-Polar-Institute/frictionless-data-packages/dev/" + id + "/tableschema.json"
        netcdf_name=id +".nc"
        savepath=os.path.join(basesavepath, id)
        savepath_datapackage=os.path.join(savepath, "datapackage.json")
        savepath_tableschema=os.path.join(savepath, "tableschema.json")
        savepath_NetCDF=os.path.join(savepath, netcdf_name)
        if not os.path.exists(savepath):
            os.mkdir(savepath)
        if os.path.exists(savepath_datapackage):
            os.remove(savepath_datapackage) 
        urllib.request.urlretrieve(datapackage_link, savepath_datapackage)
        if os.path.exists(savepath_tableschema):
            os.remove(savepath_tableschema)
        urllib.request.urlretrieve(tableschema_link, savepath_tableschema)
        if os.path.exists(savepath_NetCDF):
            os.remove(savepath_NetCDF)
        package = Package(savepath_datapackage)
        print (package.descriptor['name'])
        dataIsValid=False
        for resource in package.resources:
            print(f'Resource: {resource.name} ')
            if resource.tabular is False:               
                continue
            if resource.valid is False:
                print(f'Tableschema: {resource.name} is NOT valid!')
                print(resource.errors)
                continue
            if (resource.schema==None):
                print(f'Tableschema: {resource.name} NO SCHEMA!')
                continue
            resource.read()
            dataIsValid=True
            print(f'Tableschema: {resource.name} is valid!')
            resourceData=package.get_resource(resource.name) 
            print("create netcdf for " + resource.name)

            netcdf = Dataset(savepath_NetCDF, "w", format="NETCDF4")
            try:
                CreateNetCDF(netcdf,package,resourceData)
            except:
                netcdf.close() 
                break
            finally:
                netcdf.close()

            netcdf = Dataset(savepath_NetCDF, "r", format="NETCDF4")
            try:
                CreateERDDAPDataset(netcdf,id)
            except:
                netcdf.close() 
                break
            finally:
                netcdf.close()

            
            netcdf = Dataset(savepath_NetCDF, "r", format="NETCDF4")
            CreateEMODnetPlatform(netcdf,id)
            netcdf.close()

if os.path.exists(os.path.join(indexjsonpath, "index_stored.json")):
    os.remove(os.path.join(indexjsonpath, "index_stored.json"))
if os.path.exists(savepath_indexjson):
    shutil.move(savepath_indexjson,os.path.join(indexjsonpath, "index_stored.json"))

copyfile(erddapdatasetpath,newerddapdatasetpath)

mailText+="END EXECUTION"

import smtplib
with smtplib.SMTP(host='', port=25) as s:
    s.starttls()
    s.login("", "")
    message = """\
    Subject: SPI to EMODnet
    
    """ +mailText
    s.sendmail("", "", message)
print(message)

    
    


