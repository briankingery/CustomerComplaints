# Will run and error out when script reaches last month exported but it ran successfully


import arcpy, time, datetime
from arcpy.sa import *
from arcpy import env

ExecutionStartTime = datetime.datetime.now()
print 'Started: %s\n' % ExecutionStartTime.strftime('%A, %B %d, %Y %I:%M:%S %p')

env.workspace = r"R:\Divisions\Distribution\Shared\TechnicalScvs\ProjectFiles\EngProjects\Customer_Complaints\Customer_Complaints.gdb"
#                                                                                                            \Density.gdb
env.overwriteOutput = True

# Check out the ArcGIS Spatial Analyst extension license if available
if arcpy.CheckExtension("spatial") == "Available":
    arcpy.CheckOutExtension("spatial")

    # Make a layer from the feature class
    featureClass    = "Master_CustomerComplaints"
    fcLayer         = "Master_CustomerComplaints_lyr"
    arcpy.MakeFeatureLayer_management(featureClass, fcLayer)

    month       = 12                    # for starting month - Range of 0-12
    year        = 1996                  # for starting year

    while year < 2017:                  # change to a more future year as time passes if needed to be ran again
        
        YEAR        = str(year)         # for starting year in SQL statement
        yearRange   = 5                 # 5 year snapshot
        yearPlus5   = year + yearRange
        YEARPLUS5   = str(yearPlus5)    # for ending year in SQL statement

        # Create a dictionary for the months
        monthDict   = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
        monthIndex = month
        MONTH = monthDict[monthIndex]   # for month in name variable
        if month == 1:                  # Make this version of text so it is in the correct format for the expression for the SQL statement
            month_text = "01"
        if month == 2:
            month_text = "02"
        if month == 3:
            month_text = "03"
        if month == 4:
            month_text = "04"
        if month == 5:
            month_text = "05"
        if month == 6:
            month_text = "06"
        if month == 7:
            month_text = "07"
        if month == 8:
            month_text = "08"
        if month == 9:
            month_text = "09"
        if month == 10:
            month_text = "10"
        if month == 11:
            month_text = "11"
        if month == 12:
            month_text = "12"

        #expression = "NotifDate >= date '1996-01-01 00:00:00' AND NotifDate <= date '2001-01-01 00:00:00'"
        expression = "NotifDate >= date '"+YEAR+"-"+month_text+"-01 00:00:00' AND NotifDate <= date '"+YEARPLUS5+"-"+month_text+"-01 00:00:00'"

        # Select desired features from Master_CustomerComplaints
        arcpy.SelectLayerByAttribute_management(fcLayer, "NEW_SELECTION", expression)

        # Copy the layer to a new permanent feature class
        name = "Density_"+YEAR+month_text+"_"+YEARPLUS5+month_text
        arcpy.CopyFeatures_management(fcLayer, name)

        ############################################################################

        # Kernel Density
        inFeatures = name
        populationField = "NONE"
        cellSize = 25                   # Make smaller for more refined size 
        searchRadius = 4500     

        # Execute KernelDensity
        outKernelDensity = KernelDensity(inFeatures, populationField, cellSize, searchRadius, "SQUARE_MILES")
        # Save the output 
        outKernelDensity.save("R:/Divisions/Distribution/Shared/TechnicalScvs/ProjectFiles/EngProjects/Customer_Complaints/Density.gdb/" + name)

        print "Complete..." + name

        arcpy.Delete_management(name)

        
        month   += 1
        
        if month == 13:
            month = 1
            year    += 1

    arcpy.CheckInExtension("spatial")
else:
    print "Spatial Analyst license is not available."





ExecutionEndTime = datetime.datetime.now()
ElapsedTime = ExecutionEndTime - ExecutionStartTime

print 'Ended: %s\n' % ExecutionEndTime.strftime('%A, %B %d, %Y %I:%M:%S %p')
print 'Elapsed Time: %s' % str(ElapsedTime).split('.')[0]




##    # Kernel Density for entire Master_CustomerComplaints feature class
##    inFeatures = "R:/Divisions/Distribution/Shared/TechnicalScvs/ProjectFiles/EngProjects/Customer_Complaints/Customer_Complaints.gdb/Master_CustomerComplaints"
##    populationField = "NONE"
##    cellSize = 25           
##    searchRadius = 4500     
##    outKernelDensity = KernelDensity(inFeatures, populationField, cellSize, searchRadius, "SQUARE_MILES"
##    TITLE = "All_20150901"            ########################### Change title to most up to date ###########################
##    outKernelDensity.save("R:/Divisions/Distribution/Shared/TechnicalScvs/ProjectFiles/EngProjects/Customer_Complaints/Density.gdb/" + TITLE)


