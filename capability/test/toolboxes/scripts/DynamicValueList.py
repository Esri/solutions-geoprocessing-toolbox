# Import system modules
import arcpy

# Set the parameters
InputFeatureClass = arcpy.GetParameterAsText(0)
InputField = arcpy.GetParameterAsText(1)
InputValue = arcpy.GetParameterAsText(2)

arcpy.SetParameter(3, InputValue)