Mark New (1,*), David Lister (2), Mike Hulme (3), Ian Makin (4)

A high-resolution data set of surface climate over global land areas

Climate Research, 2000, Vol 21, pg 1-25

(1) School of Geography and the Environment, University of Oxford, 
    Mansfield Road, Oxford OX1 3TB, United Kingdom
(2) Climatic Research Unit, and (3) Tyndall Centre for Climate Change Research,
    both at School of Environmental Sciences, University of East Anglia,
    Norwich NR4 7TJ, United Kingdom
(4) International Water Management Institute, PO Box 2075, Colombo, Sri Lanka

ABSTRACT: We describe the construction of a 10-minute latitude/longitude data
set of mean monthly surface climate over global land areas, excluding Antarctica.
The climatology includes 8 climate elements - precipitation, wet-day frequency,
temperature, diurnal temperature range, relative humidity,sunshine duration,
ground frost frequency and windspeed - and was interpolated from a data set
of station means for the period centred on 1961 to 1990. Precipitation was first
defined in terms of the parameters of the Gamma distribution, enabling the 
calculation of monthly precipitation at any given return period. The data are
compared to an earlier data set at 0.5º latitude/longitude resolution and
show added value over most regions. The data will have many applications in
applied climatology, biogeochemical modelling, hydrology and agricultural
meteorology and are available through the School of Geography Oxford 
(http://www.geog.ox.ac.uk), the International Water Management Institute
"World Water and Climate Atlas" (http://www.iwmi.org) and the Climatic
Research Unit (http://www.cru.uea.ac.uk).

----------------------------------------------------------------------------
This readme file is a brief description of the formats and units in the 
CRU/Oxford/IWMI 10-minute mean climate grids for global land areas.

Please read the pdf document of the above article on this site 
(new_et_al_10minute_climate_CR.pdf), for details of the data sources,
gridding methodology, etc. BEFORE contacting the distributers with queries.


Nomenclature and Units
----------------------
pre	precipitation		mm/month
	cv of precipitation	percent
rd0	wet-days		no days with >0.1mm rain per month
tmp	mean temperature	Deg C
dtr	mean diurnal temp-	Deg C (note tmx=tmp+0.5*dtr; tmn=tmp-0.5*dtr)
	 erature range
reh	relative humidity	percent
sunp	sunshine		percent of maximum possible (percent of daylength)
frs	ground-frost		no days with groudn-frost per month
wnd	10m windspeed		m/s
elv	elevation		km


Data format
-----------
1.  All grid files except elevation (elv) and precipitation (pre)
latitutde, longitude, 12 monthly values (Jan to December)
lat and lon are in degrees decimal
format='(2f9.3,12f7.1)'
Example (first line of tmp file):
  -59.083  -26.583    0.2    0.3    0.2   -1.9   -6.0   -9.8  -13.6   -9.2   -8.1   -5.3   -2.3   -1.1

2.  Precipitation
latitude, longitude, 12 monthly means of precip, 12 monthly CVs of precip
format='(2f9.3,24f7.1)'
Example (first line of pre file):
  -59.083  -26.583  105.4  121.3  141.3  146.7  159.6  162.4  141.5  151.1  141.6  124.9  110.0   93.9   35.2   38.7   38.4 
  27.5   49.5   40.8   50.8   33.5   42.2   56.6   35.5   43.4

3.  Elevation
latitude, longitude, elevation
format='(3f9.3)'
Example (first line of elv file):
  -59.083  -26.583    0.193