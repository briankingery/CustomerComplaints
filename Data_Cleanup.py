print "Loading Application..."

import arcpy, time
from arcpy import env

env.workspace = r"R:\Divisions\Distribution\Shared\TechnicalScvs\ProjectFiles\EngProjects\Customer_Complaints\Customer_Complaints.gdb"
env.overwriteOutput = True

fc = raw_input('\nEnter feature class name: ')
fc = str(fc)

while arcpy.Exists(fc) == False:
  print '\n' + fc +' does not exist. Please try again.\n'
  fc = raw_input('Enter feature class name: ')
while arcpy.Exists(fc):
  fieldName5 = "Combo"
  fieldName6 = "DeleteOnes"

  uniqueList = []
  def isDuplicate(inValue):
    if inValue in uniqueList:
      return 1
    else:
      uniqueList.append(inValue)
      return 0

  expression6 = "{0}".format('isDuplicate(str(!' + fieldName5 + '!))')

  ## Field Calculate the 'DeletOnes' field to get 0s and 1s where the 1s represent duplicates
  ## leaving the first of the duplicate with a 0 along with non-duplicates
  arcpy.CalculateField_management(fc, fieldName6, expression6, "PYTHON_9.3")

  ## Delete the 1s - duplicates
  with arcpy.da.UpdateCursor(fc, [fieldName6]) as cursor:
    for row in cursor:
      if row[0] == str(1):
        cursor.deleteRow()
  del cursor

  ## Delete Fields
  arcpy.DeleteField_management(fc, fieldName5)
  arcpy.DeleteField_management(fc, fieldName6)

  ## Append fc to custCmplt
  arcpy.Append_management(fc,"Master_CustomerComplaints","TEST","#","#")

  
  print "\nData appended to Master_CustomerComplaints\nApplication will close in 10 seconds."
  time.sleep(10)
  break
