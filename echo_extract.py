# import libraries
from datetime import date
import zipfile
import os
import glob
import requests
from tqdm import tqdm
import pandas as pd
import shutil

# function for asking user yes no questions
def yes_no(prompt):
    """Asks the user a yes/no question and returns True for 'yes' and False for 'no'."""

    while True:
        answer = input(prompt + " (yes/no): ").lower()
        if answer in ("yes", "y"):
            return True
        elif answer in ("no", "n"):
            return False
        else:
            print("Please answer 'yes' or 'no'.")

# function to get a range (years) from user. call function with start and end arguments
def get_user_range(start_limit:int, end_limit:int):
    """Gets a range from the user."""
    while True:
        try:
            start = int(input("Enter start: "))
            if start < start_limit:
                print(f'No data before {start_limit}')
                continue
            if start > end_limit:
                print('Out of range')
                continue
            else:
                break
        except ValueError:
            print("Invalid input. Please enter integers.")
            
    while True:
        try:
            stop = int(input("Enter end: ")) + 1
            if stop > (end_limit + 1):
                print('End date out of range')
                continue
            if stop <= start:
                print('End date cannot be before start date')
                continue
            return range(start, stop)
        except ValueError:
            print("Invalid input. Please enter integers.")
# function to get output path from user
def save_path(prompt, defalut):
    """Ask for a path location to save file"""
    while True:
        answer = input(prompt) or defalut
        if os.path.exists(answer):
            return answer
        else:
            print('folder does not exist. Try again')
            continue

# main program
def main():
    # return_dir will be used to switch back to the current working directory
    return_dir = os.getcwd()
    path = save_path('Enter folder path for output or press enter to save here: ', './')
    os.chdir(path)
    # end_limit sets end of get_user_range function to current year
    end_limit = date.today().year
    # using function to get range from user. Start limit set to 2009 as ECHO does not have data before then
    user_range = get_user_range(2009, end_limit)

    # Requesting data for each year in user provided range from ECHO website
    with requests.Session() as session:
        os.makedirs('./echo_data/temp', exist_ok=True)
        for year in user_range:
            try:
                response = session.get(f'https://echo.epa.gov/files/echodownloads/NPDES_by_state_year/ID_FY{year}_NPDES_DMRS_LIMITS.zip', stream=True)
                if response.status_code != 200:
                    raise Exception
                total_size = int(response.headers.get('content-length', 0))
                with open(f'./echo_data/temp/{year}.zip', 'wb') as download:
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc=f'{year}') as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            download.write(chunk)
                            pbar.update(len(chunk))
            except:
                print(f'Could not download {year}')
        # Ask user if they want permit file for including HUC info and download from ECHO if yes
        if yes_no('Download permits file to include HUC info?'):
            os.makedirs('./echo_data/HUC', exist_ok=True)
            try:
                response = session.get('https://echo.epa.gov/files/echodownloads/npdes_downloads.zip', stream=True)
                if response.status_code != 200:
                    raise Exception
                total_size = int(response.headers.get('content-length', 0))
                with open(f'./echo_data/HUC/huc.zip', 'wb') as download:
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc='Permits.zip') as pbar:
                            for chunk in response.iter_content(chunk_size=8192):
                                download.write(chunk)
                                pbar.update(len(chunk))
            except:
                print('Permit file download failed')
    # unzips downloaded DMR data
    for x in glob.glob('./echo_data/temp/*.zip'):
            with zipfile.ZipFile(x) as unzip:
                unzip.extract(unzip.namelist()[0], './echo_data/temp')


    # Gathers a list of all .csv files in the temp folder
    files = glob.glob('./echo_data/temp/*.csv')

    # !!!! The fields variable contains the columns in the DMR data. Uncomment '#' to activate, you will also need to provide a data type

    fields = {#'ACTIVITY_ID', 
            'EXTERNAL_PERMIT_NMBR':'object', #'VERSION_NMBR',
        #'PERM_FEATURE_ID', 
            'PERM_FEATURE_NMBR':'category', #'PERM_FEATURE_TYPE_CODE': 'category',
        #'LIMIT_SET_ID': 'category',
        'LIMIT_SET_DESIGNATOR': 'category', #'LIMIT_SET_SCHEDULE_ID',
        #'LIMIT_ID': 'category', 
        # 'LIMIT_BEGIN_DATE', 'LIMIT_END_DATE', 'NMBR_OF_SUBMISSION',
        #'NMBR_OF_REPORT', 
            'PARAMETER_CODE':'object', 'PARAMETER_DESC':'object', 'MONITORING_LOCATION_CODE':'category',
            #'STAY_TYPE_CODE', 'LIMIT_VALUE_ID', 'LIMIT_VALUE_TYPE_CODE', 'LIMIT_VALUE_NMBR', 'LIMIT_UNIT_CODE',
        #'LIMIT_UNIT_DESC', 'STANDARD_UNIT_CODE', 'STANDARD_UNIT_DESC',
        #'LIMIT_VALUE_STANDARD_UNITS', 'STATISTICAL_BASE_CODE',
        'STATISTICAL_BASE_TYPE_CODE':'category',
            #'LIMIT_VALUE_QUALIFIER_CODE',
        #'OPTIONAL_MONITORING_FLAG', 'LIMIT_SAMPLE_TYPE_CODE',
        #'LIMIT_FREQ_OF_ANALYSIS_CODE', 'STAY_VALUE_NMBR', 'LIMIT_TYPE_CODE', 'DMR_EVENT_ID',
            'MONITORING_PERIOD_END_DATE':'object', 
            #'DMR_SAMPLE_TYPE_CODE', 'DMR_FREQ_OF_ANALYSIS_CODE', 'REPORTED_EXCURSION_NMBR', 'DMR_FORM_VALUE_ID', 
            'VALUE_TYPE_CODE':'category', #'DMR_VALUE_ID',
        'DMR_VALUE_NMBR':'object', #'DMR_UNIT_CODE', 
            'DMR_UNIT_DESC':'object',
        #'DMR_VALUE_STANDARD_UNITS',
            'DMR_VALUE_QUALIFIER_CODE':'category',
        #'VALUE_RECEIVED_DATE', 'DAYS_LATE', 'NODI_CODE', 'EXCEEDENCE_PCT',
        #'NPDES_VIOLATION_ID', 'VIOLATION_CODE', 'RNC_DETECTION_CODE',
        #'RNC_DETECTION_DATE', 'RNC_RESOLUTION_CODE', 'RNC_RESOLUTION_DATE'
            }
    df = pd.concat([pd.read_csv(f, usecols= fields.keys(), dtype=fields) for f in files])
    # combine the HUC information if user answers yes
    if yes_no('Add HUC info? (permit file required)'):
        try:
            zipfile.ZipFile('./echo_data/HUC/huc.zip').extract('ICIS_PERMITS.csv', './echo_data/HUC')
            df1 = pd.read_csv('./echo_data/HUC/ICIS_PERMITS.csv', usecols=['EXTERNAL_PERMIT_NMBR', 'RAD_WBD_HUC12S']).dropna().drop_duplicates()
            df1 = df1[df1.EXTERNAL_PERMIT_NMBR.str.startswith('ID')].reset_index(drop=True)
            df1['RAD_WBD_HUC12S'] = df1['RAD_WBD_HUC12S'].str.split('|')
            df1 = df1.explode('RAD_WBD_HUC12S', ignore_index=True)
            df1[['HUC', 'waterbody']] = df1['RAD_WBD_HUC12S'].str.split(':', expand=True)
            df1 = df1.drop('RAD_WBD_HUC12S', axis=1)
            df1 = df1.groupby('EXTERNAL_PERMIT_NMBR', as_index=False).agg({'HUC': ';'.join, 'waterbody': '; '.join })
            df = df.merge(df1,how='left', on='EXTERNAL_PERMIT_NMBR')
        except:
            print('Adding HUC info failed. Try downloading the permits file.')
    # export output in csv format
    df.to_csv(f'./echo_data/{user_range[0]}-{user_range[-1]}_dmrs.csv', index=False, encoding='utf-8-sig')
    # delete temp folder. Comment this out if you want to keep seperate files. May cause issues if script is run again
    shutil.rmtree('./echo_data/temp')
    # return to original working directory
    os.chdir(return_dir)
    print('Process complete')

if __name__ == '__main__':
    main()
