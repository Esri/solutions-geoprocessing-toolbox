import arcpy 
import datetime
from dateutil import rrule 
import ast

def createFeatureClass(fcName, spatRef, statsFields):

	arcpy.AddMessage("Creating output feature class...")
	arcpy.CreateFeatureclass_management(arcpy.env.workspace, fcName, "POLYGON", "", "", "", spatRef)

	createFields = {'start_date':'DATE','end_date':'DATE','count':'LONG'}
	for k,v in createFields.items():
		arcpy.AddField_management(fcName, k,v)

	if len(statsFields) > 0 and statsFields[0] != "":
		for field in statsFields:
			for statType in ["_sum", "_mean", "_min", "_max", "_std", "_var"]:
				arcpy.AddField_management(fcName, field + statType, "DOUBLE")

	arcpy.AddMessage("Output feature class complete.")


def pointsOfInterest(points, polygon):

	if arcpy.Exists("points_lyr"):
		arcpy.management.SelectLayerByAttribute("points_lyr", "CLEAR_SELECTION")

	arcpy.management.MakeFeatureLayer(points, "points_lyr")
	arcpy.management.SelectLayerByLocation("points_lyr", "INTERSECT", polygon, "", "NEW_SELECTION")
	arcpy.management.CopyFeatures("points_lyr", 'in_memory\selectedPoints')
	arcpy.management.Delete("points_lyr")

	return 'in_memory\selectedPoints'


def timeRange(timeField, pointsLayer, timeStep, stats, rangeDirections, rangeField, outputFCName):

	fieldNames = [f.name for f in arcpy.ListFields(pointsLayer)]
	timeIndex = fieldNames.index(timeField)

	count = 0
	dateList =[]
	with arcpy.da.SearchCursor(pointsLayer, "*") as searchCursor:
		for row in searchCursor:
			dateList.append(row[timeIndex])
			count += 1

	firstDate = min(dateList).replace(hour=0, minute=0, second=0)   
	lastDate =  max(dateList).replace(hour=23, minute=59, second=59) 
	arcpy.AddMessage('Processing: ' + str((lastDate - firstDate)) + " worth of data...")

	timeRule = {"Year":rrule.YEARLY, "Month":rrule.MONTHLY, "Week":rrule.WEEKLY,"Day":rrule.DAILY, "Hour":rrule.HOURLY, "Minute": rrule.MINUTELY}

	start = 0
	analysisOutputs = []
	arcpy.management.MakeFeatureLayer(pointsLayer, "pointSelection")
	for dateStep in rrule.rrule(timeRule[timeStep], dtstart=firstDate, until=lastDate):
		if start == 0:
			start += 1
			startDate = firstDate
			continue
		arcpy.AddMessage('Processing: ' + str(startDate) + " - " + str(dateStep)) 
		where_clause = fieldNames[timeIndex] + " >= date '" + str(startDate) + "' AND " + fieldNames[timeIndex] + " < date '" + str(dateStep) + "'"
		analysisOutputs.append(polyCounts(where_clause, "pointSelection",[startDate, dateStep], stats, rangeDirections, rangeField, outputFCName))
		startDate = dateStep

	if dateStep < lastDate:
	        arcpy.AddMessage('Processing: ' + str(startDate) + " - " + str(lastDate))
	        where_clause = fieldNames[timeIndex] + " >= date '" + str(startDate) + "' AND " + fieldNames[timeIndex]+ " <= date '" + str(lastDate) + "'"
	        analysisOutputs.append(polyCounts(where_clause, "pointSelection", [startDate, lastDate], stats, rangeDirections, rangeField, outputFCName))

	return analysisOutputs


def polyCounts(whereClause, pointLayer, dates, statsF, inputRanges, inputDirField, outputFC):

	arcpy.management.SelectLayerByAttribute(pointLayer, "NEW_SELECTION", whereClause)
	selected = arcpy.GetCount_management(pointLayer)
	numSelected = int(selected.getOutput(0))
	arcpy.AddMessage("Features selected: " + str(numSelected))
	dates.append(numSelected)
	
	arcpy.management.MakeFeatureLayer(pointLayer, "rangePoints", whereClause)
	degRange = degreesRange("rangePoints", numSelected, inputRanges, inputDirField, outputFC)
	arcpy.management.Delete("rangePoints")

	if len(statsF) > 0 and statsF[0] != "":
		statsResults = calcStatistics(pointLayer, statsF, numSelected)
		for statsR in statsResults:
			dates.append(statsR)
	
	if numSelected > 0: 	
		centroids.append(timeSliceCentroid(pointLayer))
	#else: 
		#centroids.append(timeSliceCentroid("pointWhole"))

	for deg in degRange:
		dates.append(deg)

	return dates


def writeOutput(polygonShape, featureWrite, outputFeatureClass, statsFields, dirRangeFields):

	arcpy.AddMessage('Writing output...')

	fieldList = ['start_date', 'end_date', 'count']

	if len(statsFields) > 0 and statsFields[0] != "":
		for field in statsFields:
			for statType in ["_sum", "_mean", "_min", "_max", "_std", "_var"]:
				fieldList.append(field + statType)

	if len(dirRangeFields) > 0:
		for dirField, trash in dirRangeFields.items():
			fieldList.append(dirField + "_count")
			fieldList.append(dirField + "_percent")

	fieldList.append('SHAPE@')

	for features in featureWrite:
		features.append(polygonShape)
		with arcpy.da.InsertCursor(outputFeatureClass, fieldList) as insertCursor:
			insertCursor.insertRow((features))


def outputToCSV(fcToWrite, pathToCSV):

	fieldNames = [f.name for f in arcpy.ListFields(fcToWrite)]
	fieldNames.remove('Shape')
	arcpy.stats.ExportXYv(fcToWrite, fieldNames,'COMMA', pathToCSV,'ADD_FIELD_NAMES')

	arcpy.AddMessage("Data Written to CSV Successfully.")


def calcStatistics(pointsStats, statsFields, numSelected):

	arr = arcpy.da.TableToNumPyArray(pointsStats, (statsFields))
	
	statsList = []
	testList = []
	for stats in statsFields:
		if numSelected > 0:
			statsList.extend((arr[stats].sum(), arr[stats].mean(), arr[stats].min(), arr[stats].max(), arr[stats].std(), arr[stats].var()))
		else:
			statsList.extend((0,0,0,0,0,0))

	return statsList


def timeSliceCentroid(slicedPoints):

	arcpy.management.MinimumBoundingGeometry(slicedPoints, 'in_memory/sliced_convex', "CONVEX_HULL", "", "", "NO_MBG_FIELDS")

	with arcpy.da.SearchCursor('in_memory/sliced_convex', "SHAPE@XY") as centroidCursor:
		for centroid in centroidCursor:
			return centroid[0]

			
# def centroidsToLines(centroidGeoms, outputName, spatialRef):
# 	features = [arcpy.Polyline(arcpy.Array([arcpy.Point(geoms[0], geoms[1]) for geoms in centroidGeoms]), spatialRef, False, False)]
# 	arcpy.CopyFeatures_management(features, outputName)


def degreesRange(layer, totalSel, cardinalRanges, cardinalField, featureClass):

	degreeRangeList = []

	for k,v in cardinalRanges.items():
		arcpy.AddField_management(featureClass, k + "_count", "DOUBLE")
		arcpy.AddField_management(featureClass, k + "_percent", "DOUBLE")
		if v[0] > v[1]:
			where = """(({0} > {1} AND {0} <= 360) OR ({0} >= 0 AND {0} <= {2}))""".format(cardinalField, v[0], v[1])
			arcpy.management.SelectLayerByAttribute(layer, "NEW_SELECTION", where)
			sel = arcpy.GetCount_management(layer)
			numSel = int(sel.getOutput(0))
			degreeRangeList.append(numSel)
		else:
			where = """{0} > {1} AND {0} <= {2}""".format(cardinalField, v[0], v[1])
			arcpy.management.SelectLayerByAttribute(layer, "NEW_SELECTION", where)
			sel = arcpy.GetCount_management(layer)
			numSel = int(sel.getOutput(0))
			degreeRangeList.append(numSel)

		if totalSel > 0:
			degreeRangeList.append((numSel/totalSel)*100)
			percent = "{0:.2f}".format((numSel/totalSel)*100) + "%"
		else:
			degreeRangeList.append(0)
			percent = "0%"

		arcpy.AddMessage(k + ": " + str(numSel) + " - " + percent)

	arcpy.AddMessage("*" * 50)

	return degreeRangeList

def main(poly, inputs):

	inputPoints = inputs[0]
	timeFieldName = inputs[1]
	timeStepInterval = inputs[2]
	outFCName = inputs[3] + "_" + str(poly[0])
	createCSV = inputs[4]
	csvPath = inputs[5]
	statsFields = inputs[6].split(';')
	convertPoints = inputs[7]
	directionField = inputs[8] 
	directionRanges = ast.literal_eval(inputs[9]) 
		
	arcpy.AddMessage("Output feature class names will have object ID of input polygon appended to the name.\
	This is to insure a unique ID for each output feature class.  Eveything is running as expected.")

	arcpy.AddMessage("Starting....")

	createFeatureClass(outFCName, arcpy.Describe(inputPoints).spatialReference, statsFields)
	
	selectedPoints = pointsOfInterest(inputPoints, poly[1])
	
	newFeatues = timeRange(timeFieldName, selectedPoints, timeStepInterval, statsFields, directionRanges, directionField, outFCName)

	writeOutput(poly[1], newFeatues, outFCName, statsFields, directionRanges)

	if bool(createCSV) == True:
		outputToCSV(outFCName, csvPath + '\\' + outFCName + '.csv')

	if bool(convertPoints) == True:
		arcpy.management.FeatureToPoint(outFCName, outFCName + "_Points", "INSIDE")

	#arcpy.AddMessage("Creating centroid line....")
	#centroidsToLines(centroids, outFCName + "_Line", arcpy.Describe(inputPoints).spatialReference)

	arcpy.AddMessage("Cleaning up.")

	arcpy.management.Delete("points_lyr")
	arcpy.management.Delete("in_memory\selectedPoints")
	arcpy.management.Delete("pointSelection")
	arcpy.management.Delete('in_memory/sliced_convex')

	arcpy.AddMessage("Processing Complete.")


if __name__ == '__main__':

	arcpy.env.overwriteOutput = True

	argv = tuple(arcpy.GetParameterAsText(i) for i in range(arcpy.GetArgumentCount()))

	arcpy.env.workspace = argv[0]
	inputPolygon = argv[1]
	variables = argv[2:]

	with arcpy.da.SearchCursor(inputPolygon, ['OID@','SHAPE@']) as polyCursor:
		for polygon in polyCursor:
			global centroids
			centroids = []
			main(polygon, variables)



