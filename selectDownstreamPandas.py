import arcpy, sys, os.path
import numpy as np
import pandas as pd

zoneTopologyFile = arcpy.GetParameterAsText(0)
fromField = arcpy.GetParameterAsText(1)
toField = arcpy.GetParameterAsText(2)
zoneSelectField = arcpy.GetParameterAsText(3)

def traceAttribution(zoneTopologyFile, zoneSelectField, toField, fromField):
	arcpy.AddMessage("Reading zone topology table...")
	rows = arcpy.SearchCursor(zoneTopologyFile)
	hydroids = []
	tohydroids = []
	selectVals = []
	for row in rows:
		hydroid = row.getValue(fromField)
		tohydroid = row.getValue(toField)
		selectVal = row.getValue(zoneSelectField)
		hydroids.append(hydroid)
		tohydroids.append(tohydroid)
		selectVals.append(selectVal)
	del row, rows, hydroid, tohydroid, selectVal
	hydroids = map(int, hydroids)
	hydroids = map(str, hydroids)
	tohydroids = map(int, tohydroids)
	tohydroids = map(str, tohydroids)
	topologyTable = pd.DataFrame({"TOHYDROID": tohydroids, 'SELECTDOWN': selectVals}, index=hydroids)
	selectid = topologyTable.index[topologyTable['SELECTDOWN']==1]
	arcpy.AddMessage("Finding downstream zones...")
	froms = pd.Series(selectid)
	end = False
	i = 0
	while end == False:
		i += 1
		tos = topologyTable.ix[topologyTable.index.isin(froms), 'TOHYDROID']
		if len(froms) > 0:
			topologyTable.ix[topologyTable.index.isin(tos), 'SELECTDOWN'] = 1
		else:
			end = True
		# step down one tier on network hierarchy
		froms = tos
		if i > 1000:
			break
	del tos, end, froms
	rows = arcpy.UpdateCursor(zoneTopologyFile, "", "", zoneSelectField)
	j = -1
	for row in rows:
		j += 1
		if topologyTable.SELECTDOWN[j] == 1:
			row.setValue(zoneSelectField, 1)
		else:
			row.setValue(zoneSelectField, 0)
		rows.updateRow(row)
	del row, rows

if __name__ == "__main__":
	traceAttribution(zoneTopologyFile, zoneSelectField, toField, fromField)