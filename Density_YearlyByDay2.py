
import arcpy, time, datetime
from arcpy.sa import *
from arcpy import env

ExecutionStartTime = datetime.datetime.now()
print 'Started: %s\n' % ExecutionStartTime.strftime('%A, %B %d, %Y %I:%M:%S %p')



### Check out the ArcGIS Spatial Analyst extension license if available
if arcpy.CheckExtension("spatial") == "Available":
    arcpy.CheckOutExtension("spatial")

    env.workspace = "R:/Divisions/Distribution/Shared/TechnicalScvs/ProjectFiles/EngProjects/Customer_Complaints/Customer_Complaints.gdb"
    #                                                                                                           /Density_YearlyByDay.gdb
    env.overwriteOutput = True

    # Make a layer from the feature class
    featureClass    = "Master_CustomerComplaints"
    fcLayer         = "Master_CustomerComplaints_lyr"
    arcpy.MakeFeatureLayer_management(featureClass, fcLayer)


    day         = 1                     # for starting day   - Range of 1-28 (Not paying attention to 29, 30, or 31 for differing months)
    month       = 12                    # for starting month - Range of 0-12
    year        = 1996                  # for starting year
    
    while year < 2017:                  # change to a more future year as time passes if needed to be ran again
        
        CURRENTYEAR         = str(year) # for starting year in SQL statement
        NEXTYEAR            = str(int(year+1))
        
        if day < 29:
            if day < 10:
                DAY = "0" + str(day)
            else:
                DAY = str(day)
        
        if month == 1:                  # Make this version of text so it is in the correct format for the expression for the SQL statement
            CURRENTMONTH    = "01"
            NEXTMONTH       = "0" + str(int(month+1))
        if month == 2:
            CURRENTMONTH    = "02"
            NEXTMONTH       = "0" + str(int(month+1))
        if month == 3:
            CURRENTMONTH    = "03"
            NEXTMONTH       = "0" + str(int(month+1))      
        if month == 4:
            CURRENTMONTH    = "04"
            NEXTMONTH       = "0" + str(int(month+1))          
        if month == 5:
            CURRENTMONTH    = "05"
            NEXTMONTH       = "0" + str(int(month+1))          
        if month == 6:
            CURRENTMONTH    = "06"
            NEXTMONTH       = "0" + str(int(month+1))           
        if month == 7:
            CURRENTMONTH    = "07"
            NEXTMONTH       = "0" + str(int(month+1))          
        if month == 8:
            CURRENTMONTH    = "08"
            NEXTMONTH       = "0" + str(int(month+1))          
        if month == 9:
            CURRENTMONTH    = "09"
            NEXTMONTH       = str(int(month+1))         
        if month == 10:
            CURRENTMONTH    = "10"
            NEXTMONTH       = str(int(month+1))           
        if month == 11:
            CURRENTMONTH    = "11"
            NEXTMONTH       = str(int(month+1))          
        if month == 12:
            CURRENTMONTH    = "12"
            if CURRENTMONTH == "12":
                NEXTMONTH   = "01"
                
        #expression = "NotifDate >= date '1996-01-01 00:00:00' AND NotifDate <= date '2001-01-01 00:00:00'"
        expression = "NotifDate >= date '"+CURRENTYEAR+"-"+CURRENTMONTH+"-"+DAY+" 00:00:00' AND NotifDate <= date '"+NEXTYEAR+"-"+CURRENTMONTH+"-"+DAY+" 00:00:00'"

 
        # Select desired features from Master_CustomerComplaints
        arcpy.SelectLayerByAttribute_management(fcLayer, "NEW_SELECTION", expression)

        # Copy the layer to a new permanent feature class
        name = "Density_"+CURRENTYEAR+CURRENTMONTH+DAY+"_"+NEXTYEAR+CURRENTMONTH+DAY
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
        outKernelDensity.save("R:/Divisions/Distribution/Shared/TechnicalScvs/ProjectFiles/EngProjects/Customer_Complaints/Density_YearlyByDay.gdb/" + name)

        print "Completed Raster... " + name

        arcpy.Delete_management(name)

#######
## Add code from DensityMXD_JPGExport_Daily Here
#######

        del env.workspace
        env.workspace = r"R:\Divisions\Distribution\Shared\TechnicalScvs\ProjectFiles\EngProjects\Customer_Complaints\Density_YearlyByDay.gdb"
        env.overwriteOutput = True

        mxd = arcpy.mapping.MapDocument("R:/Divisions/Distribution/Shared/TechnicalScvs/ProjectFiles/EngProjects/Customer_Complaints/Density_YearlyByDay.mxd")
        df  = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
        for df in arcpy.mapping.ListDataFrames(mxd):
            targetGroupLayer = arcpy.mapping.ListLayers(mxd, "DensityGroupLayer", df)[0]
            
            # Add Raster Layer to Density Group Layer
            for raster in arcpy.ListRasters("D*"):              # List all rasters that start with a 'D'
                rasterLayerName = raster+"_lyr"
                result          = arcpy.MakeRasterLayer_management(raster, rasterLayerName)
                layer           = result.getOutput(0)
                arcpy.mapping.AddLayerToGroup(df, targetGroupLayer, layer, "AUTO_ARRANGE")

                arcpy.RefreshTOC()                              # REFRESH
                arcpy.RefreshActiveView()

                for target in targetGroupLayer:
                    # Add Symbology to Raster Layer in Density Group Layer
                    inputLayer      = target                    # Layer to apply symbology to
                    sourceLayer     = "R:/Divisions/Distribution/Shared/TechnicalScvs/ProjectFiles/EngProjects/Customer_Complaints/Stretched_8STD_YearlyByDay.lyr"
                    symbologyLayer  = arcpy.mapping.Layer(sourceLayer)
                    #arcpy.ApplySymbologyFromLayer_management(inputLayer, symbologyLayer)
                    arcpy.mapping.UpdateLayer(df, inputLayer, symbologyLayer, True)

                    # Raster name example = Density_19990303_20000303

                    dateRange = raster[8:]                      # Cuts of 'Density_'
                    d1 = dateRange[6:8]
                    d2 = dateRange[15:]
                    y1 = dateRange[0:4]                         # Example - 'From 12 1996 to 12 2001'
                    y2 = dateRange[9:13]
                    m = dateRange[4:6]                         # Changes dynamic text in mxd to match new dataframe name
                    if dateRange[4] == "0":
                        m = int(dateRange[5])
                    if dateRange[4] == "10":
                        m = int(dateRange[5])
                    if dateRange[4:6] == "11":
                        m = int(dateRange[4:6])
                    if dateRange[4:6] == "12":
                        m = int(dateRange[4:6])
                    # Create a dictionary for the months
                    monthDict   = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
                    monthIndex = m
                    MONTH = monthDict[monthIndex]

                    rasterName = "From " + MONTH +" "+ y1 +" - "+ y2

                    df.name = rasterName                        # Change dataframe name to the date
                    
                    arcpy.RefreshTOC()                          # REFRESH
                    arcpy.RefreshActiveView()

                    # Export the map to a .jpg
                    jpg = "R:/Divisions/Distribution/Shared/TechnicalScvs/ProjectFiles/EngProjects/Customer_Complaints/Density_JPGs_YearlyByDay/" + raster + ".jpg"
                    arcpy.mapping.ExportToJPEG(mxd, jpg)
                    print "Completed Jpeg... " + raster

                    df.name = "Layers"                          # Change dataframe name back to Layers
                    
                    # Remove Layer from Density Group Layer
                    arcpy.mapping.RemoveLayer(df, target)
           
                    arcpy.RefreshTOC()                          # REFRESH
                    arcpy.RefreshActiveView()

                    arcpy.Delete_management(raster)
        del mxd

        day         += 1
        if day == 29:
            day     = 1
            month   += 1
        if month == 13 or month == 14:
            month   = 1
            year    += 1

    arcpy.CheckInExtension("spatial")
else:
    print "Spatial Analyst license is not available."

ExecutionEndTime = datetime.datetime.now()
ElapsedTime = ExecutionEndTime - ExecutionStartTime

print 'Ended: %s\n' % ExecutionEndTime.strftime('%A, %B %d, %Y %I:%M:%S %p')
print 'Elapsed Time: %s' % str(ElapsedTime).split('.')[0]




























### Create a dictionary for the months
##monthDict   = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
##monthIndex = month
##MONTH = monthDict[monthIndex]   # for month in name variable



##    # Kernel Density for entire Master_CustomerComplaints feature class
##    inFeatures = "R:/Divisions/Distribution/Shared/TechnicalScvs/ProjectFiles/EngProjects/Customer_Complaints/Customer_Complaints.gdb/Master_CustomerComplaints"
##    populationField = "NONE"
##    cellSize = 25           
##    searchRadius = 4500     
##    outKernelDensity = KernelDensity(inFeatures, populationField, cellSize, searchRadius, "SQUARE_MILES"
##    TITLE = "All_20150901"            ########################### Change title to most up to date ###########################
##    outKernelDensity.save("R:/Divisions/Distribution/Shared/TechnicalScvs/ProjectFiles/EngProjects/Customer_Complaints/Density.gdb/" + TITLE)


