# echo-extract.py
Combines multiple years of discharge monitoring records from EPAs NPDES DMR datasets for Idaho dischargers

echo_extract.py is a Python script that uses the requests package to download 
ICIS-NPDES Permit Limit and Discharge Monitoring Report (DMR) Datasets for Idaho 
from https://echo.epa.gov/tools/data-downloads/icis-npdes-dmr-and-limit-data-set. 
It then extracts the downloaded zip files and uses the Pandas package to concatenate
all the files into one .csv file. 

The script can also download the ICIS-NPDES National Dataset (Part1) zip file 
(https://echo.epa.gov/files/echodownloads/npdes_downloads.zip) so that HUC information 
can be added as new columns to the dataframe.

The fields variable contains a dictionary with all the DMR dataset headers. Only the
typically used fields have been selected but any other field can be included by 
uncommenting them (remove the # before it).

The requirements.txt file in this repository can be used when creating a virtual
environment to automatically install the required dependencies. You can also open it to
view which packages you need to install if you will run the script from your base Python 
interpreter. 

You will be asked for the path where you want the downloads and output file to be placed.
You can press enter to place the files in your current working directory, or enter a path
with no quotation marks around it (e.g. C:/project/data not "C:/project/data")

When you run the script it will ask you for the start and end year of the range of data you
want to download. ECHO does not have data before 2009 so it will not let you enter a year
before 2009, the script will also prevent you from entering years after the current year
or years that are before the start year you entered. 

The script will ask if you want to download the permit file to add HUC information to the
dataframe. This file is larger and will take some time to download. If you are re-running
the script in the same folder location and still have the permit file downloaded, you can
skip this download by choosing no and it will use the previous copy of the file when adding
the HUC information.

The last prompt asks if you want to add the HUC information to the DMR datasets. You can
skip adding the information if it is not need by answering no.

Finally, the script will create the output .csv file and will remove the temporary files 
created when unzipping the files. 