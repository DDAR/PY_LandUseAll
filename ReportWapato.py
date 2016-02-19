#-------------------------------------------------------------------------------
# Name:         ReportWapato.py
# Purpose:      Calculate statistics for different zones and adding
#               up total vacant and occupied acreages.
#
#Version:       ArcGIS 10.2 and Python 2.7.5
#
# Author:      Donna Arnett
#
# Created:     08/5/2015
# Copyright:   (c) donnaa 2015
# Licence:     <your licence>
# Add to git hub 02/09/2016
#-------------------------------------------------------------------------------
import arcpy
import os
import sys
import traceback
import numpy
import time

#Calculates Median Statistics
# env settings

arcpy.env.overwriteOutput = True
arcpy.env.qualifiedFieldNames = False

# Figure out the median value of a dataset
def GetMedian(in_list):
    medianValue = numpy.median(in_list)
    return medianValue

# Figure the Average value of a dataset
def GetAverage(in_list):
    avgValue = numpy.average(in_list)
    return avgValue

# Calculate the Median values for a dataset
def GetMedianValues(source_fc, value_field):
    use_vals = []
    with arcpy.da.SearchCursor(source_fc, [value_field]) as rows:
        for row in rows:
            if row[0] != None:
                use_vals.append(row[0])
    if len(use_vals) > 0:
        median = GetMedian(use_vals)
        avg = GetAverage(use_vals)


    return (str("%.2f" % median), str("%.2f" % avg))

# Get all values and stats for a data field
def GetAllList(source_fc, value_field):
    use_vals = []
    with arcpy.da.SearchCursor(source_fc, [value_field]) as rows:
        for row in rows:
            if row[0] != None:
                use_vals.append(row[0])
    if len(use_vals) > 0:
        count = len(use_vals)
        median = GetMedian(use_vals)
        avg = GetAverage(use_vals)
        total = sum(use_vals)

    return (str("%.2f" % median), str("%.2f" % avg), str("%.0f" % count), str("%.2f" % total))

# Add up the values
def findTotals(source_fc, value_field, whereclause):
    use_value = []
    with arcpy.da.SearchCursor(source_fc, [value_field], whereclause) as rows:
        for row in rows:
            if row[0] != None:
                use_value.append(row[0])
        if len(use_value) > 0:
            total = sum(use_value)
        else:
            total = 0
    return total

# Write the stats to a file
def writeToFile(lyrfile, finFile2):
    matchcount = int(arcpy.GetCount_management('parc_lyr').getOutput(0))
    if matchcount == 0:
        print('No feautures matched spatial and attribute criteria')
    else:
        if arcpy.Exists(finFile2):
            arcpy.Delete_management(finFile2)
    arcpy.CopyFeatures_management('parc_lyr', finFile2)

if __name__ == '__main__':


    # Script tool params

    SummaryLayer = r'R:\disk_5\projects\county\planning\uga_analysis\wapato\Analysis_2015\AnalysisData.gdb\UGAWapato_020416'
    baseFileLocation = r'R:\disk_5\projects\county\planning\uga_analysis\wapato\Analysis_2015'
    fileGeoLocation = r'R:\disk_5\projects\county\planning\uga_analysis\wapato\Analysis_2015\AnalysisData.gdb'
    reportFile = os.path.join(baseFileLocation, "WapatoReport_020416.txt")
    print reportFile
    value_field = 'ACRES'
    value_vacant = 'ACRES_VAC'
    value_occupied = 'ACRES_OCC'
    value_city = 'CITY'
    value_zonegroup = 'ZoneGroup'
    value_vacantSym = 'VACANT'

    if os.path.exists(reportFile):
        os.remove(reportFile)
    f = open(reportFile, 'w')
    line = 'Wapato Report - UGA Analysis'
    f.write(line + '\n' + '\n')
    line = time.strftime("%m/%d/%Y")
    f.write(line + '\n')
    line = time.strftime("%I:%M:%S")
    f.write(line + '\n' + '\n')

    #Find the Total acres
    totalAcres = GetAllList(SummaryLayer, value_field)
    line = "Total Acres: " + str(totalAcres[3])
    f.write(line + '\n' + '\n')

    #find the Total acres within city
    whereClause = '"CITY" = ' + '1'
    total = findTotals(SummaryLayer, value_field, whereClause)
    line = "Total Acres Within City: " + str("%.2f" % total)
    f.write(line + '\n')

    #find the Total acres within the UGA
    whereClause = '"CITY" = ' + '0'
    total = findTotals(SummaryLayer, value_field, whereClause)
    line = "Total Acres Outside City Limits Within UGA: " + str("%.2f" % total)
    f.write(line + '\n' + '\n')

    #find the Total of acres that are Developed
    whereClause = '"Vacant" = ' + '0'
    total = findTotals(SummaryLayer, value_field, whereClause)
    line = "Total of acres that are Developed: " + str("%.2f" % total)
    f.write(line + '\n')

    #find the Total of acres that are Vacant
    whereClause = '"Vacant" = ' + '1'
    total = findTotals(SummaryLayer, value_field, whereClause)
    line = "Total of acres that are Vacant: " + str("%.2f" % total)
    f.write(line + '\n')

    #find the Total of acres that are Partially Developed
    whereClause = '"Vacant" = ' + '2'
    total = findTotals(SummaryLayer, value_field, whereClause)
    totalVac = findTotals(SummaryLayer, value_vacant, whereClause)
    totalOcc = findTotals(SummaryLayer, value_occupied, whereClause)
    line = "Total of acres that are Partially Vacant: " + str("%.2f" % total)
    f.write(line + '\n')
    line = "        Vacant Acres: " + str("%.2f" % totalVac)
    f.write(line + '\n')
    line = "        Developed Acres: " + str("%.2f" % totalOcc)
    f.write(line + '\n')

##    #find the Total of acres that are not classified
##    whereClause = '"Vacant" = ' + '9'
##    total = findTotals(SummaryLayer, value_field, whereClause)
##    line = "Total of acres that are not classified as vacant or developed: " + str("%.2f" % total)
##    f.write(line + '\n' + '\n')

    # Group
    line = '\n' + '    Acreage by Zone Groupings' + '\n' + '\n'
    f.write(line)

    # Residential
    line = 'RESIDENTIAL' + '\n'
    f.write(line)
    #Total Residential
    whereClause = '"ZoneGroup" = ' + "'RES'"
    total = findTotals(SummaryLayer, value_vacant, whereClause)
    total2 = findTotals(SummaryLayer, value_occupied, whereClause)
    grandtotal = total + total2
    line = 'Total Residential: ' + str("%.2f" % grandtotal) + '\n'
    f.write(line)
    #Total Residential City
    whereClause = '"ZoneGroup" = ' + "'RES'" + "AND" + '"CITY" = ' + '1'
    totalResVacCity = findTotals(SummaryLayer, value_vacant, whereClause)
    totalResOccCity = findTotals(SummaryLayer, value_occupied, whereClause)
    totalResCity = totalResOccCity + totalResVacCity
    line = "Total Residential Within the City: " + str("%.2f" % totalResCity) + '\n'
    f.write(line)
    #Total Residential UGA
    whereClause = '"ZoneGroup" = ' + "'RES'" + "AND" + '"CITY" = ' + '0'
    totalResOccUGA = findTotals(SummaryLayer, value_occupied, whereClause)
    totalResVacUGA = findTotals(SummaryLayer, value_vacant, whereClause)
    totalResUGA = totalResOccUGA + totalResVacUGA
    line = "Total Residential Outside City Limits: " + str("%.2f" % totalResUGA) + '\n' + '\n'
    f.write(line)
    #Total Vacant
    line = "     Total Vacant: " + str("%.2f" % total) + '\n'
    f.write(line)
    #Total Vacant within City Limits
    line = '     Total Vacant Within City Limits: ' + str("%.2f" % totalResVacCity) + '\n'
    f.write(line)
    #Total Vacant Outside City Limits
    line = '     Total Vacant Outside City Limits: ' + str("%.2f" % totalResVacUGA) + '\n' + '\n'
    f.write(line)
    #Total Developed
    line = "     Total Developed: " + str("%.2f" % total2) + '\n'
    f.write(line)
    #Total Developed within City Limits
    line = '     Total Developed Within the City Limits: ' + str("%.2f" % totalResOccCity) + '\n'
    f.write(line)
    #Total Developed Outside City Limits
    line = '     Total Developed Outside City Limits: ' + str("%.2f" % totalResOccUGA) + '\n' + '\n'
    f.write(line)

    #Commercial
    line = 'Commercial' + '\n'
    f.write(line)
    #Total Commercial
    whereClause = '"ZoneGroup" = ' + "'COM'"
    total = findTotals(SummaryLayer, value_vacant, whereClause)
    total2 = findTotals(SummaryLayer, value_occupied, whereClause)
    grandtotal = total + total2
    line = 'Total Commercial: ' + str("%.2f" % grandtotal) + '\n'
    f.write(line)
    #Total Commercial City
    whereClause = '"ZoneGroup" = ' + "'COM'" + "AND" + '"CITY" = ' + '1'
    totalResVacCity = findTotals(SummaryLayer, value_vacant, whereClause)
    totalResOccCity = findTotals(SummaryLayer, value_occupied, whereClause)
    totalResCity = totalResOccCity + totalResVacCity
    line = "Total Commercial Within the City: " + str("%.2f" % totalResCity) + '\n'
    f.write(line)
    #Total Commercial UGA
    whereClause = '"ZoneGroup" = ' + "'COM'" + "AND" + '"CITY" = ' + '0'
    totalResOccUGA = findTotals(SummaryLayer, value_occupied, whereClause)
    totalResVacUGA = findTotals(SummaryLayer, value_vacant, whereClause)
    totalResUGA = totalResOccUGA + totalResVacUGA
    line = "Total Commercial Outside City Limits: " + str("%.2f" % totalResUGA) + '\n' + '\n'
    f.write(line)
    #Total Vacant
    line = "     Total Vacant: " + str("%.2f" % total) + '\n'
    f.write(line)
    #Total Vacant within City Limits
    line = '     Total Vacant Within City Limits: ' + str("%.2f" % totalResVacCity) + '\n'
    f.write(line)
    #Total Vacant Outside City Limits
    line = '     Total Vacant Outside City Limits: ' + str("%.2f" % totalResVacUGA) + '\n' + '\n'
    f.write(line)
    #Total Developed
    line = "     Total Developed: " + str("%.2f" % total2) + '\n'
    f.write(line)
    #Total Developed within City Limits
    line = '     Total Developed Within the City Limits: ' + str("%.2f" % totalResOccCity) + '\n'
    f.write(line)
    #Total Developed Outside City Limits
    line = '     Total Developed Outside City Limits: ' + str("%.2f" % totalResOccUGA) + '\n' + '\n'
    f.write(line)

    #Industrial
    line = 'Industrial' + '\n'
    f.write(line)
    #Total Industrial
    whereClause = '"ZoneGroup" = ' + "'IND'"
    total = findTotals(SummaryLayer, value_vacant, whereClause)
    total2 = findTotals(SummaryLayer, value_occupied, whereClause)
    grandtotal = total + total2
    line = 'Total Industrial: ' + str("%.2f" % grandtotal) + '\n'
    f.write(line)
    #Total Industrial City
    whereClause = '"ZoneGroup" = ' + "'IND'" + "AND" + '"CITY" = ' + '1'
    totalResVacCity = findTotals(SummaryLayer, value_vacant, whereClause)
    totalResOccCity = findTotals(SummaryLayer, value_occupied, whereClause)
    totalResCity = totalResOccCity + totalResVacCity
    line = "Total Industrial Within the City: " + str("%.2f" % totalResCity) + '\n'
    f.write(line)
    #Total Industrial UGA
    whereClause = '"ZoneGroup" = ' + "'IND'" + "AND" + '"CITY" = ' + '0'
    totalResOccUGA = findTotals(SummaryLayer, value_occupied, whereClause)
    totalResVacUGA = findTotals(SummaryLayer, value_vacant, whereClause)
    totalResUGA = totalResOccUGA + totalResVacUGA
    line = "Total Industrial Outside City Limits: " + str("%.2f" % totalResUGA) + '\n' + '\n'
    f.write(line)
    #Total Vacant
    line = "     Total Vacant: " + str("%.2f" % total) + '\n'
    f.write(line)
    #Total Vacant within City Limits
    line = '     Total Vacant Within City Limits: ' + str("%.2f" % totalResVacCity) + '\n'
    f.write(line)
    #Total Vacant Outside City Limits
    line = '     Total Vacant Outside City Limits: ' + str("%.2f" % totalResVacUGA) + '\n' + '\n'
    f.write(line)
    #Total Developed
    line = "     Total Developed: " + str("%.2f" % total2) + '\n'
    f.write(line)
    #Total Developed within City Limits
    line = '     Total Developed Within the City Limits: ' + str("%.2f" % totalResOccCity) + '\n'
    f.write(line)
    #Total Developed Outside City Limits
    line = '     Total Developed Outside City Limits: ' + str("%.2f" % totalResOccUGA) + '\n' + '\n'
    f.write(line)

##    #Planned Development
##    line = 'Planned Development' + '\n'
##    f.write(line)
##    whereClause = '"ZoneGroup" = ' + "'PD'"
##    total = findTotals(SummaryLayer, value_vacant, whereClause)
##    total2 = findTotals(SummaryLayer, value_occupied, whereClause)
##    grandtotal = total + total2
##    line = 'Total Planned Development: ' + str("%.2f" % grandtotal) + '\n'
##    f.write(line)
##    #Total Planned Development City
##    whereClause = '"ZoneGroup" = ' + "'PD'" + "AND" + '"CITY" = ' + '1'
##    totalResVacCity = findTotals(SummaryLayer, value_vacant, whereClause)
##    totalResOccCity = findTotals(SummaryLayer, value_occupied, whereClause)
##    totalResCity = totalResOccCity + totalResVacCity
##    line = "Total Planned Development Within the City: " + str("%.2f" % totalResCity) + '\n'
##    f.write(line)
##    #Total Planned Development UGA
##    whereClause = '"ZoneGroup" = ' + "'PD'" + "AND" + '"CITY" = ' + '0'
##    totalResOccUGA = findTotals(SummaryLayer, value_occupied, whereClause)
##    totalResVacUGA = findTotals(SummaryLayer, value_vacant, whereClause)
##    totalResUGA = totalResOccUGA + totalResVacUGA
##    line = "Total Planned Development Outside City Limits: " + str("%.2f" % totalResUGA) + '\n' + '\n'
##    f.write(line)
##    #Total Vacant
##    line = "     Total Vacant: " + str("%.2f" % total) + '\n'
##    f.write(line)
##    #Total Vacant within City Limits
##    line = '     Total Vacant Within City Limits: ' + str("%.2f" % totalResVacCity) + '\n'
##    f.write(line)
##    #Total Vacant Outside City Limits
##    line = '     Total Vacant Outside City Limits: ' + str("%.2f" % totalResVacUGA) + '\n' + '\n'
##    f.write(line)
##    #Total Developed
##    line = "     Total Developed: " + str("%.2f" % total2) + '\n'
##    f.write(line)
##    #Total Developed within City Limits
##    line = '     Total Developed Within the City Limits: ' + str("%.2f" % totalResOccCity) + '\n'
##    f.write(line)
##    #Total Developed Outside City Limits
##    line = '     Total Developed Outside City Limits: ' + str("%.2f" % totalResOccUGA) + '\n' + '\n'
##    f.write(line)

    #Public\Community
    line = 'Community Facilities' + '\n'
    f.write(line)
    whereClause = '"ZoneGroup" = ' + "'PC'"
    total = findTotals(SummaryLayer, value_vacant, whereClause)
    total2 = findTotals(SummaryLayer, value_occupied, whereClause)
    grandtotal = total + total2
    line = 'Total Community Facilities: ' + str("%.2f" % grandtotal) + '\n'
    f.write(line)
    #Total Public\Community City
    whereClause = '"ZoneGroup" = ' + "'PC'" + "AND" + '"CITY" = ' + '1'
    totalResVacCity = findTotals(SummaryLayer, value_vacant, whereClause)
    totalResOccCity = findTotals(SummaryLayer, value_occupied, whereClause)
    totalResCity = totalResOccCity + totalResVacCity
    line = "Total Community Facilities Within the City: " + str("%.2f" % totalResCity) + '\n'
    f.write(line)
    #Total Public\Community UGA
    whereClause = '"ZoneGroup" = ' + "'PC'" + "AND" + '"CITY" = ' + '0'
    totalResOccUGA = findTotals(SummaryLayer, value_occupied, whereClause)
    totalResVacUGA = findTotals(SummaryLayer, value_vacant, whereClause)
    totalResUGA = totalResOccUGA + totalResVacUGA
    line = "Total Community Facilities Outside City Limits: " + str("%.2f" % totalResUGA) + '\n' + '\n'
    f.write(line)
    #Total Vacant
    line = "     Total Vacant: " + str("%.2f" % total) + '\n'
    f.write(line)
    #Total Vacant within City Limits
    line = '     Total Vacant Within City Limits: ' + str("%.2f" % totalResVacCity) + '\n'
    f.write(line)
    #Total Vacant Outside City Limits
    line = '     Total Vacant Outside City Limits: ' + str("%.2f" % totalResVacUGA) + '\n' + '\n'
    f.write(line)
    #Total Developed
    line = "     Total Developed: " + str("%.2f" % total2) + '\n'
    f.write(line)
    #Total Developed within City Limits
    line = '     Total Developed Within the City Limits: ' + str("%.2f" % totalResOccCity) + '\n'
    f.write(line)
    #Total Developed Outside City Limits
    line = '     Total Developed Outside City Limits: ' + str("%.2f" % totalResOccUGA) + '\n' + '\n'
    f.write(line)

    #Environmentally Constrained
    line = 'Environmentally Constrained' + '\n'
    f.write(line)
    whereClause = '"ZoneGroup" = ' + "'EC'"
    total = findTotals(SummaryLayer, value_vacant, whereClause)
    total2 = findTotals(SummaryLayer, value_occupied, whereClause)
    grandtotal = total + total2
    line = 'Total Environmentally Constrained: ' + str("%.2f" % grandtotal) + '\n'
    f.write(line)
    #Total EC\Community City
    whereClause = '"ZoneGroup" = ' + "'EC'" + "AND" + '"CITY" = ' + '1'
    totalResVacCity = findTotals(SummaryLayer, value_vacant, whereClause)
    totalResOccCity = findTotals(SummaryLayer, value_occupied, whereClause)
    totalResCity = totalResOccCity + totalResVacCity
    line = "Total Environmentally Constrained Within the City: " + str("%.2f" % totalResCity) + '\n'
    f.write(line)
    #Total EC\Community UGA
    whereClause = '"ZoneGroup" = ' + "'EC'" + "AND" + '"CITY" = ' + '0'
    totalResOccUGA = findTotals(SummaryLayer, value_occupied, whereClause)
    totalResVacUGA = findTotals(SummaryLayer, value_vacant, whereClause)
    totalResUGA = totalResOccUGA + totalResVacUGA
    line = "Total Environmentally Constrained Outside City Limits: " + str("%.2f" % totalResUGA) + '\n' + '\n'
    f.write(line)
    #Total Vacant
    line = "     Total Vacant: " + str("%.2f" % total) + '\n'
    f.write(line)
    #Total Vacant within City Limits
    line = '     Total Vacant Within City Limits: ' + str("%.2f" % totalResVacCity) + '\n'
    f.write(line)
    #Total Vacant Outside City Limits
    line = '     Total Vacant Outside City Limits: ' + str("%.2f" % totalResVacUGA) + '\n' + '\n'
    f.write(line)
    #Total Developed
    line = "     Total Developed: " + str("%.2f" % total2) + '\n'
    f.write(line)
    #Total Developed within City Limits
    line = '     Total Developed Within the City Limits: ' + str("%.2f" % totalResOccCity) + '\n'
    f.write(line)
    #Total Developed Outside City Limits
    line = '     Total Developed Outside City Limits: ' + str("%.2f" % totalResOccUGA) + '\n' + '\n'
    f.write(line)

    #Yakama Nation Lands
    line = 'Yakama Nation Lands' + '\n'
    f.write(line)
    whereClause = '"ZoneGroup" = ' + "'YN'"
    total = findTotals(SummaryLayer, value_vacant, whereClause)
    total2 = findTotals(SummaryLayer, value_occupied, whereClause)
    grandtotal = total + total2
    line = 'Total Yakama Nation Lands: ' + str("%.2f" % grandtotal) + '\n'
    f.write(line)
    #Total YN\Community City
    whereClause = '"ZoneGroup" = ' + "'YN'" + "AND" + '"CITY" = ' + '1'
    totalResVacCity = findTotals(SummaryLayer, value_vacant, whereClause)
    totalResOccCity = findTotals(SummaryLayer, value_occupied, whereClause)
    totalResCity = totalResOccCity + totalResVacCity
    line = "Total Yakama Nation Lands Within the City: " + str("%.2f" % totalResCity) + '\n'
    f.write(line)
    #Total YN\Community UGA
    whereClause = '"ZoneGroup" = ' + "'YN'" + "AND" + '"CITY" = ' + '0'
    totalResOccUGA = findTotals(SummaryLayer, value_occupied, whereClause)
    totalResVacUGA = findTotals(SummaryLayer, value_vacant, whereClause)
    totalResUGA = totalResOccUGA + totalResVacUGA
    line = "Total Yakama Nation Lands Outside City Limits: " + str("%.2f" % totalResUGA) + '\n' + '\n'
    f.write(line)
    #Total Vacant
    line = "     Total Vacant: " + str("%.2f" % total) + '\n'
    f.write(line)
    #Total Vacant within City Limits
    line = '     Total Vacant Within City Limits: ' + str("%.2f" % totalResVacCity) + '\n'
    f.write(line)
    #Total Vacant Outside City Limits
    line = '     Total Vacant Outside City Limits: ' + str("%.2f" % totalResVacUGA) + '\n' + '\n'
    f.write(line)
    #Total Developed
    line = "     Total Developed: " + str("%.2f" % total2) + '\n'
    f.write(line)
    #Total Developed within City Limits
    line = '     Total Developed Within the City Limits: ' + str("%.2f" % totalResOccCity) + '\n'
    f.write(line)
    #Total Developed Outside City Limits
    line = '     Total Developed Outside City Limits: ' + str("%.2f" % totalResOccUGA) + '\n' + '\n'
    f.write(line)

    f.close()