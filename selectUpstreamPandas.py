import arcpy, sys, os.path
import numpy as np
import pandas as pd

zoneTopologyFile = arcpy.GetParameterAsText(0)
zoneSelectField = arcpy.GetParameterAsText(1)

# zoneTopologyFile = "C:/Users/ruesca/Documents/GIS/24kAttribution/Spatial24k03142013.gdb/watersheds"
# zoneSelectField = "SELECTUP"


def traceAttribution(zoneTopologyFile, zoneSelectField):
	arcpy.AddMessage("Reading zone topology table...")
	rows = arcpy.SearchCursor(zoneTopologyFile)
	hydroids = []
	tohydroids = []
	selectVals = []
	for row in rows:
		hydroid = row.getValue("CATCHID")
		tohydroid = row.getValue("TOCATCHID")
		selectVal = row.getValue(zoneSelectField)
		hydroids.append(hydroid)
		tohydroids.append(tohydroid)
		selectVals.append(selectVal)
	del row, rows, hydroid, tohydroid, selectVal
	hydroids = map(int, hydroids)
	hydroids = map(str, hydroids)
	tohydroids = map(int, tohydroids)
	tohydroids = map(str, tohydroids)
	topologyTable = pd.DataFrame({"TOHYDROID": tohydroids, 'SELECTUP': selectVals}, index=hydroids)
	selectid = topologyTable.index[topologyTable["SELECTUP"]==1]
	arcpy.AddMessage("Finding upstream zones...")
	tos = pd.Series(selectid)
	end = False
	i = 0
	while end == False:
		i += 1
		froms = topologyTable.index[topologyTable['TOHYDROID'].isin(tos)]
		if len(froms) > 0:
			# upstrIds = upstrIds.append(pd.Series(froms))
			topologyTable.ix[topologyTable.index.isin(froms), 'SELECTUP'] = 1
		else:
			end = True
		# step up one tier on network hierarchy
		tos = froms
		if i > 1000:
			break
	del tos, end, froms
	rows = arcpy.UpdateCursor(zoneTopologyFile, "", "", zoneSelectField)
	j = -1
	for row in rows:
		j += 1
		if topologyTable.SELECTUP[j] == 1:
			row.setValue(zoneSelectField, 1)
		else:
			row.setValue(zoneSelectField, 0)
		rows.updateRow(row)
	del row, rows

if __name__ == "__main__":
	traceAttribution(zoneTopologyFile, zoneSelectField)