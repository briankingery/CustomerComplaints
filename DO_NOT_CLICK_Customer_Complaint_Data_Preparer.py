
import arcpy
from arcpy import env

env.workspace = r"R:\Divisions\Distribution\Shared\TechnicalScvs\ProjectFiles\EngProjects\Customer_Complaints\Customer_Complaints.gdb"
env.overwriteOutput = True

## Copy Meters from Conway_sdeVector_sdeViewer.sde
#meter_original = "Database Connections\Conway_sdeVector_sdeViewer.sde\SDEVECTOR.SDEDATAOWNER.V_WSERVICELOCATION_EAM"
meter_original = r"R:\Divisions\Distribution\Shared\TechnicalScvs\ProjectFiles\EngProjects\Customer_Complaints\Script\Conway_sdeVector_sdeViewer.sde\SDEVECTOR.SDEDATAOWNER.V_WSERVICELOCATION_EAM"
meter_copy = "Meter"
arcpy.FeatureClassToFeatureClass_conversion(meter_original, env.workspace, meter_copy)
meter_layer = "V_WSERVICELOCATION_EAM_lyr"
arcpy.MakeFeatureLayer_management(meter_copy, meter_layer)

## Export XLS to Table in geodatabase
xls = arcpy.GetParameterAsText(0)
# xls file must start with 'cc' EXAMPLE cc201508.xls
xls_file = str(xls)
cc = xls_file.find("cc")
dot_notation = xls_file.find(".xlsx", cc)
if dot_notation == -1:      # Catches and fixes the error when searching for '.xlsx' if filetype is '.xls'
    dot_notation = xls_file.find(".xls", cc)
table_name = xls_file[cc : dot_notation]

if arcpy.Exists(table_name):
    arcpy.Delete_management(table_name)
arcpy.ExcelToTable_conversion(xls, "_"+table_name, "Sheet1")

## Join the Table to the Meter layer
meter_layer = meter_layer
meter_field = "ServiceLocationID"
join_table = "_"+table_name
join_field = "Functional_loc_"
expression = join_table + ".Functional_loc_ IS NOT NULL"
meter_join = "Meter_Join"
# Join the feature layer to a table
arcpy.AddJoin_management(meter_layer, meter_field, join_table, join_field)
# Select desired features from veg_layer
arcpy.SelectLayerByAttribute_management(meter_layer, "NEW_SELECTION", expression)
# Copy the layer to a new permanent feature class
arcpy.CopyFeatures_management(meter_layer, meter_join)

## Make Table Query
table_list = "_"+table_name, meter_join
out_table = "QueryTable"
field_list = "_"+table_name+".Coding_code_txt #;"+"_"+table_name+".Functional_loc_ #;"+"_"+table_name+".Notif_date #;"+"_"+table_name+".Description #;"+meter_join+".Shape #"
whereClause = meter_join+".Meter_ServiceLocationID LIKE " + "_"+table_name+".Functional_loc_"
# Make Query Table...
arcpy.MakeQueryTable_management(table_list, out_table, "NO_KEY_FIELD", "#", field_list, whereClause)
# Create Feature Class from query table
query_table = out_table
query_table_copy = table_name
arcpy.FeatureClassToFeatureClass_conversion(query_table, env.workspace, query_table_copy)

## Delete intermediate Meter_Join FC and table
arcpy.Delete_management(meter_join)
arcpy.Delete_management("_"+table_name)

## Field Modifications
fieldName1 = "_"+table_name + "_Coding_code_txt"
fieldName2 = "_"+table_name + "_Functional_loc_"
fieldName3 = "_"+table_name + "_Notif_date"
fieldName4 = "_"+table_name + "_Description"

fieldName1a = "CodingCode"
fieldName2a = "FunctiLocation"
fieldName3a = "NotifDate"
fieldName4a = "Description"
fieldName5 = "Combo"
fieldName6 = "DeleteOnes"

fieldTypeText = "TEXT"
fieldTypeDate = "DATE"

arcpy.AddField_management(query_table_copy, fieldName1a, fieldTypeText, "", "", 25)
arcpy.AddField_management(query_table_copy, fieldName2a, fieldTypeText, "", "", 10)
arcpy.AddField_management(query_table_copy, fieldName3a, fieldTypeDate, "", "", 8)
arcpy.AddField_management(query_table_copy, fieldName4a, fieldTypeText, "", "", 50)
arcpy.AddField_management(query_table_copy, fieldName5, fieldTypeText, "", "", 50)
arcpy.AddField_management(query_table_copy, fieldName6, fieldTypeText, "", "", 5)

expression1 = "{0}".format('!' + fieldName1 + '!')
expression2 = "{0}".format('!' + fieldName2 + '!')
expression3 = "{0}".format('!' + fieldName3 + '!')
expression4 = "{0}".format('!' + fieldName4 + '!')
expression5 = "{0}".format('str(!FunctiLocation!) + str( !NotifDate!) + str(!CodingCode!)')

arcpy.CalculateField_management(query_table_copy, fieldName1a, expression1, "PYTHON_9.3")
arcpy.CalculateField_management(query_table_copy, fieldName2a, expression2, "PYTHON_9.3")
arcpy.CalculateField_management(query_table_copy, fieldName3a, expression3, "PYTHON_9.3")
arcpy.CalculateField_management(query_table_copy, fieldName4a, expression4, "PYTHON_9.3")
arcpy.CalculateField_management(query_table_copy, fieldName5, expression5, "PYTHON_9.3")

arcpy.DeleteField_management(query_table_copy, fieldName1)
arcpy.DeleteField_management(query_table_copy, fieldName2)
arcpy.DeleteField_management(query_table_copy, fieldName3)
arcpy.DeleteField_management(query_table_copy, fieldName4)

