#-------------------------------------------------------------------------------
# Name:        Single Band Gap Filler For Landsat 7
# Purpose:      To use cloud masks for three seperate scenes to fill gaps in data
#               due to SLC-induced gaps and clouds
# Author:      Quinten Geddes   Quinten.A.Geddes<at>nasa.gov
#               NASA DEVELOP PRogram
# Created:     12/04/2013

#-------------------------------------------------------------------------------

import arcpy
def L7GapFill(SceneList, OutputPath,CloudMaskList=[],Zstretch=True):
    """Uses cloud masks for three seperate scenes to fill gaps in data
    due to SLC-induced gaps and clouds"""

    arcpy.CheckOutExtension("Spatial")
#Registering the scenes of interest
    for i,Scene in enumerate(SceneList):
        exec("Scene{0}=arcpy.Raster(Scene)".format(i+1))
        #establishing gaps in each image

        if len(CloudMaskList)==len(SceneList):
            CloudMask=arcpy.Raster(CloudMaskList[i])
            exec("Mask{0}=(Scene{0}>0)*CloudMask".format(i+1))
            del CloudMask
        else:
            exec("Mask{0}=Scene{0}>0".format(i+1))


    if Zstretch==True or Zstretch=="true":
        print("shifting and streching histograms using z-score")
        arcpy.AddMessage("shifting and streching histograms using z-score")
        #Collecting stats for z score
        if len(SceneList)==3:
            MaskC=Mask1*Mask2*Mask3
        else:
            MaskC=Mask1*Mask2

        print("Calculating statistics for Scene 1")
        arcpy.AddMessage("Calculating statistics for Scene 1")
        Scene1Common=Scene1*MaskC
        arcpy.CalculateStatistics_management(Scene1Common,ignore_values=[0])
        mean1=Scene1Common.mean
        std1 =Scene1Common.standardDeviation

        print("Calculating statistics for Scene 2")
        arcpy.AddMessage("Calculating statistics for Scene 2")
        Scene2Common=Scene2*MaskC
        arcpy.CalculateStatistics_management(Scene2Common,ignore_values=[0])
        mean2=Scene2Common.mean
        std2 =Scene2Common.standardDeviation

        #converting to z score then using the std and mean of the preferred scene to "fit" histogram
        Scene2 = (((Scene2-mean2)/std2)*std1)+mean1

        if len(SceneList)==3:
            print("Calculating statistics for Scene 3")
            arcpy.AddMessage("Calculating statistics for Scene 3")
            Scene3Common=Scene3*MaskC
            arcpy.CalculateStatistics_management(Scene3Common,ignore_values=[0])
            mean3=Scene3Common.mean
            std3 =Scene3Common.standardDeviation


            Scene3 = (((Scene3-mean3)/std3)*std1)+mean1

    print("Filling Gaps")
    arcpy.AddMessage("Filling Gaps")
    #keeping all good pixels for the first scene
    Scene1Fill=Mask1*Scene1

    #keeping good pixels for the 2nd scene where 1st pixels are bad
    Scene2Fill=((Mask1==0)*Mask2)*Scene2

    #keeping good pixels for the 3rd scene where 2nd and 1st pixels are bad
    if len(SceneList)==3:
        Scene3Fill= ((Mask1==0)*(Mask2==0)*Mask3)*Scene3
        FinalImage=Scene1Fill+Scene2Fill+Scene3Fill
    else:
        FinalImage=Scene1Fill+Scene2Fill
    #combining the kept pixels from each scene

    FinalImage.save(OutputPath)
    return OutputPath

