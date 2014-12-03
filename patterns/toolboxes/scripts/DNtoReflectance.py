#-------------------------------------------------------------------------------
# Name:        Landsat Digital Numbers to Radiance/Reflectance
# Purpose:      To convert landsat 4,5, or 7 pixel values from digital numbers
#               to Radiance, Reflectance, or Temperature
# Author:      Quinten Geddes     Quinten.A.Geddes@nasa.gov
#               NASA DEVELOP Program
# Created:     19/10/2012

#-------------------------------------------------------------------------------
import arcpy
import math

##L7Reflectance C:\Users\qgeddes\Downloads\Landsat\tooltest\LE71720832011270ASN00_B1.TIF C:\Users\qgeddes\Downloads\Landsat\tooltest\LE71720832011270ASN00_MTL.txt Reflectance/Temperature C:\Users\qgeddes\Downloads\Landsat\tooltest\Refl

arcpy.CheckOutExtension("Spatial")
def DNtoReflectance(Lbands,MetaData,OutputType="Reflectance/Temperature",Save=False,OutputFolder=""):
    """This function is used to convert Landsat 4,5, or 7 pixel values from
    digital numbers to Radiance, Reflectance, or Temperature (if using Band 6)

    -----Inputs------
    Lbands: GeoTIFF files containing individual bands of Landsat imagery. These
    must have the original names as downloaded and must be from a single scene.

    MetaData: The metadata text file that is downloaded with the Landsat Bands themselves.
    This may be either the old or new MTL.txt file.

    OutputType: Choose whether the output should be:
                "Radiance"
                "Reflectance/Temperature" - Calculates Reflectance for spectral bands
                                            and Temperature in Kelvin for Thermal bands

    Save: Boolean value that indicates whether the output rasters will be saved permanantly
            Each band will be saved as an individual GeoTIFF file and be named
            accoriding to the original filename and the output pixel unit

            *if this is true, then the OutputFolder variable must also be set

    OutputFolder: Folder in which to save the output rasters

    -----Outputs-----

    A list of arcpy raster objects in a sequence that mirrors that of the input Lbands

    """
    OutList=[]
    
    #These lists will be used to parse the meta data text file and locate relevant information
    #metadata format was changed August 29, 2012. This tool can process either the new or old format
    newMeta=['LANDSAT_SCENE_ID = "','DATE_ACQUIRED = ',"SUN_ELEVATION = ",
            "RADIANCE_MAXIMUM_BAND_{0} = ","RADIANCE_MINIMUM_BAND_{0} = ",
            "QUANTIZE_CAL_MAX_BAND_{0} = ","QUANTIZE_CAL_MIN_BAND_{0} = "]

    oldMeta=['BAND1_FILE_NAME = "',"ACQUISITION_DATE = ","SUN_ELEVATION = ",
            "LMAX_BAND{0} = ","LMIN_BAND{0} = ",
            "QCALMAX_BAND{0} = ","QCALMIN_BAND{0} = "]
    f=open(MetaData)
    MText=f.read()

    #the presence of a PRODUCT_CREATION_TIME category is used to identify old metadata
    #if this is not present, the meta data is considered new.
    #Band6length refers to the length of the Band 6 name string. In the new metadata this string is longer
    if "PRODUCT_CREATION_TIME" in MText:
        Meta=oldMeta
        Band6length=2
    else:
        Meta=newMeta
        Band6length=8

    #The tilename is located using the newMeta/oldMeta indixes and the date of capture is recorded
    if Meta==newMeta:
        TileName=MText.split(Meta[0])[1].split('"')[0]
        year=TileName[9:13]
        jday=TileName[13:16]
    elif Meta==oldMeta:
        TileName=MText.split(Meta[0])[1].split('"')[0]
        year=TileName[13:17]
        jday=TileName[17:20]

    date=MText.split(Meta[1])[1].split('\n')[0]


    #the spacecraft from which the imagery was capture is identified
    #this info determines the solar exoatmospheric irradiance (ESun) for each band
    spacecraft=MText.split('SPACECRAFT_ID = "')[1].split('"')[0]
    if   "7" in spacecraft: ESun=(1969.0,1840.0,1551.0,1044.0,255.700,0.,82.07,1368.00)
    elif "5" in spacecraft: ESun=(1957.0,1826.0,1554.0,1036.0,215.0  ,0.,80.67)
    elif "4" in spacecraft: ESun=(1957.0,1825.0,1557.0,1033.0,214.9  ,0.,80.72)
    else:
        arcpy.AddError("This tool only works for Landsat 4, 5, or 7")
        raise arcpy.ExecuteError()

    #determing if year is leap year and setting the Days in year accordingly
    if float(year) % 4 ==0: DIY=366.
    else:DIY=365.

    #using the date to determing the distance from the sun
    theta =2*math.pi*float(jday)/DIY

    dSun2 = (1.00011 + 0.034221*math.cos(theta) + 0.001280*math.sin(theta) +
             0.000719*math.cos(2*theta)+ 0.000077*math.sin(2*theta) )

    SZA=90.-float(MText.split(Meta[2])[1].split("\n")[0])


    #Calculating values for each band
    for pathname in Lbands:
        try:BandNum=pathname.split("\\")[-1].split("B")[1][0]
        except:
            msg="Error reading Band {0}. Bands must have original names as downloaded.".format(str(inputbandnum))
            arcpy.AddError(msg)
            print(msg)
            raise arcpy.ExecuteError

        #changing Band 6 name to match metadata
        if BandNum=="6" and spacecraft[8]=="7":
            BandNum=pathname.split("\\")[-1].split("B")[1][0:Band6length]


        print("Processing Band {0}".format(BandNum))

        Oraster=arcpy.Raster(pathname)

        #using the oldMeta/newMeta indixes to pull the min/max for radiance/Digital numbers
        LMax=   float(MText.split(Meta[3].format(BandNum))[1].split("\n")[0])
        LMin=   float(MText.split(Meta[4].format(BandNum))[1].split("\n")[0])
        QCalMax=float(MText.split(Meta[5].format(BandNum))[1].split("\n")[0])
        QCalMin=float(MText.split(Meta[6].format(BandNum))[1].split("\n")[0])

        Radraster=(((LMax - LMin)/(QCalMax-QCalMin)) * (Oraster - QCalMin)) +LMin
        Oraster=0

        if OutputType=="Radiance":
            Radraster.save("{0}\\{1}_B{2}_Radiance.tif".format(OutputFolder,TileName,BandNum))
            Radraster=0

        elif OutputType=="Reflectance/Temperature":
            #Calculating temperature for band 6 if present
            if "6" in BandNum:
                Refraster=1282.71/(arcpy.sa.Ln((666.09/Radraster)+1.0))
                BandPath="{0}\\{1}_B{2}_Temperature.tif".format(OutputFolder,TileName,BandNum)
            #Otherwise calculate reflectance
            else:
                Refraster=( math.pi * Radraster * dSun2) / (ESun[int(BandNum[0])-1] * math.cos(SZA*math.pi/180) )
                BandPath="{0}\\{1}_B{2}_TOA_Reflectance.tif".format(OutputFolder,TileName,BandNum)

            if Save==True:
                Refraster.save(BandPath)
                OutList.append(arcpy.Raster(BandPath))
            else:
                OutList.append(Refraster)
            del Refraster,Radraster

        arcpy.AddMessage( "Reflectance Calculated for Band {0}".format(BandNum))
        print("Reflectance Calculated for Band {0}".format(BandNum))
    f.close()
    return OutList
