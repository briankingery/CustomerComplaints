
import arcpy
from arcpy.sa import *
from arcpy import env

env.workspace = r"R:\Divisions\Distribution\Shared\TechnicalScvs\ProjectFiles\EngProjects\Customer_Complaints\Customer_Complaints.gdb"
env.overwriteOutput = True

# Check out the ArcGIS Spatial Analyst extension license if available
if arcpy.CheckExtension("spatial") == "Available":
    arcpy.CheckOutExtension("spatial")

    # Create a dictionary for the months
    monthDict   = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
    month       = arcpy.GetParameter(0)     #1                 # GetUserInput for starting month - Range of 0-12

    year        = arcpy.GetParameter(1)     #2001              # GetUserInput for starting year
    YEAR        = str(year)
    yearRange   = arcpy.GetParameter(2)     #5                 # GetUserInput for how many years to cover, the Default is a 5 year snapshot


    enddate    = year + yearRange
    ENDDATE    = str(enddate)

    monthIndex = month
    MONTH = monthDict[monthIndex]
    if month == 1:
        month = "01"
    if month == 2:
        month = "02"
    if month == 3:
        month = "03"
    if month == 4:
        month = "04"
    if month == 5:
        month = "05"
    if month == 6:
        month = "06"
    if month == 7:
        month = "07"
    if month == 8:
        month = "08"
    if month == 9:
        month = "09"
    if month == 10:
        month = "10"
    if month == 11:
        month = "11"
    if month == 12:
        month = "12"

    # Make a layer from the feature class
    featureClass    = "Master_CustomerComplaints"
    fcLayer         = "Master_CustomerComplaints_lyr"
    arcpy.MakeFeatureLayer_management(featureClass, fcLayer)
    #expression = "NotifDate >= date '1996-01-01 00:00:00' AND NotifDate <= date '2001-01-01 00:00:00'"
    expression = "NotifDate >= date '"+YEAR+"-"+month+"-01 00:00:00' AND NotifDate <= date '"+ENDDATE+"-"+month+"-01 00:00:00'"

    # Select desired features from Master_CustomerComplaints
    arcpy.SelectLayerByAttribute_management(fcLayer, "NEW_SELECTION", expression)

    # Copy the layer to a new permanent feature class
    name = MONTH+YEAR+"_"+MONTH+ENDDATE+"_"+str(yearRange)+"yearSnapshot"
    arcpy.CopyFeatures_management(fcLayer, name)

    ############################################################################

    # Kernel Density
    inFeatures = name
    populationField = "NONE"
    cellSize = 25           
    searchRadius = 4500     

    # Execute KernelDensity
    outKernelDensity = KernelDensity(inFeatures, populationField, cellSize, searchRadius, "SQUARE_MILES")
    # Save the output 
    outKernelDensity.save("KD_"+name)
    arcpy.Delete_management(name)



    arcpy.CheckInExtension("spatial")
else:
    print "Spatial Analyst license is not available."















