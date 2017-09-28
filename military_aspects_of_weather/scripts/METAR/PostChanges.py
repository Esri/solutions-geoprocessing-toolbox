import arcpy

# Modify the following variables
# URL to your service, where clause, fields and token if applicable
baseURL= httpsampleserver6.arcgisonline.comarcgisrestservicesPoolPermitsFeatureServer1query
where = '1=1'
fields ='apn, address, pool_permit'
token = ''

#The above variables construct the query
query = where={}&outFields={}&returnGeometry=true&f=json&token={}.format(where, fields, token)
# See httpservices1.arcgis.comhelpindex.htmlfsQuery.html for more info on FS-Query
fsURL = baseURL + query

fs = arcpy.FeatureSet()
fs.load(fsURL)

arcpy.CopyFeatures_management(fs, rclocaldata.gdbpermits)