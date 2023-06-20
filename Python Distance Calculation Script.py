import requests
import pandas as pd

apikey = input('Enter API Key: ')

####################################################################################################################
########################################################## FUNCTIONS ###############################################
####################################################################################################################
## API Function (a max of 20 addresses can be searched per API Call/Function)

## Endpoint - Initalise Requests session and set API Url
ses = requests.Session()

# https://developers.google.com/maps/documentation/distance-matrix/overview
apiEndPoint = "https://maps.googleapis.com/maps/api/distancematrix/json?"

def apiCall(postCodes: str, Destination: str):
    # Payload
    hrs = {
        'key':apikey,
        'origins':postCodes,
        'destinations':Destination,
        'units':'imperial'
    }
    # Repsonse
    response = ses.get(apiEndPoint,params=hrs) 

    # The response can have upto 20 address results, so need to loop through and populate duration & distance Lists (the lists are defined further below in the code)
    for Postcode in response.json()['rows']:
        try:
            distance = Postcode['elements'][0]['distance']['text']
            duration = Postcode['elements'][0]['duration']['text']
            distancedf.append(distance)
            durationdf.append(duration)
        # Exception included incase of a bad postcode that cant be found
        except:
            distancedf.append('error')
            durationdf.append('error')

####################################################################################################################
########################################################## STEP 1 ##################################################
####################################################################################################################
## Read CSV File (or change to Excel) with postcodes
## 1.1 - Read and assigned csv files to be used as dataframes
DataFrame = pd.read_excel('./TestData.xlsx')

####################################################################################################################
########################################################## STEP 2 ##################################################
####################################################################################################################
## This step involves sending the postcode to the API and then adding the result into an empty list, 
## so that it can be joined onto the Dataframe at the end

## 2.1 - Define Empty Lists/Columns that will be populated
distancedf = [] # Empty Distance List which will be populated with distances and then added to the main DF
durationdf = [] # Empty Duration List which will be populated with durations and then added to the main DF

## 2.2 - Sort Dataframe
DataFrame = DataFrame.sort_values(by=['Destination']) ## To make sure the list is sorted by Destination

## 2.3 - Query all Destinations in the list (to create a seperate DF for each Destination)
DestinationList = DataFrame['Destination'].unique() #This returns a list of all Destinations (only listed once, hence the unique)

## 2.4 - Loop through each Destination
for eachDestination in DestinationList:
    ## 2.5 - Create a filtered DF based on Destination in list and get the list of Origin postcodes for that Destination
    filteredDF = DataFrame[DataFrame['Destination'] == eachDestination] # Creates a dataframe that is filtered on a single Destination
    OriginPostcodes = filteredDF['Origin'] # list of Origin postcodes from the new filtered DF
    DestinationCode = filteredDF['Destination'].values[0] # Destination postcode (first code in list) to be searched against all Origin postcodes

    ## 2.6 = Loop through Origin Postcodes and append 20 of them to a string for API search
    postcodeStringList = '' # Empty string to be populated in below loop (the API calls only takes a string, not an actual list)
    for index,postcode in enumerate(OriginPostcodes):
        postcodeStringList = postcodeStringList + f'{postcode}|' # the '|' acts as a delimiter for the addresses
        if (index+1) % 20 == 0: # A Max of 20 addressses per API call, so once 20 addresses have been added to the list, pass into the API call and repeat
            apiCall(postcodeStringList,DestinationCode)
            postcodeStringList = '' # reset list for new loop

    ## 2.7 Pass any remaining postcodes into the API (the above function only calls if index reaches a multiple of 20, if not, the function isnt called, so we call it again here)
    if len(postcodeStringList) > 0:
        apiCall(postcodeStringList,DestinationCode)

####################################################################################################################
########################################################## STEP 3 ##################################################
####################################################################################################################
## The final step involves merging the lists (one is distance and the other is duration) back into the DF
## and then finaling, outputinng the final result DF and Error DF to excel

## 3.1 - Merge the two columns (now populated), into the main original dataframe
DataFrame['Distance'] = distancedf
DataFrame['Duration'] = durationdf

## 3.2 - Output final dataframe to Excel
DataFrame.to_csv('./results.csv', index=False)
print('Complete')
