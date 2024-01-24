import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
import folium
import datetime as datetime
import requests
from bs4 import BeautifulSoup
import re


###Scrapping data
#Website links
#url = "https://www.data.gov.uk/dataset/cb7ae6f0-4be6-4935-9277-47e5ce24a11f/road-safety-data"

##Defining functions
#Check that the website is allowed for acces
#<Response [200]>#means able to access
@st.cache_data
def check_acess(url):
    response = requests.get(url)
    if response.status_code == 200:
        notification = "Access to URL is granted!"
    else:
        notification = "Access to URL is denied!, please input a different link!"
    return notification    
                  

#Load all available csv from url and list out all dataset names
@st.cache_data
def load_dataset(html):
    html = requests.get(url)    
    #parse html info
    soup = BeautifulSoup(html.text, 'html.parser')

    #extract all links available from html
    links = []
    for i in soup.find_all('a'):
        link = i.get('href')
        links.append(link)

    #Only keeps the csv ones 
    links_csv = []
    for i in links:
        if "csv" in i:
            links_csv.append(i)       
    
    name_csv = []
    spans = soup.find_all("span", {"class": "visually-hidden"})
    for span in spans:
        text = span.text.strip()  # Remove leading/trailing whitespaces
        if "CSV '" in text and "', Dataset:" in text:
            name = text.split("CSV '", 1)[1].split("', Dataset:", 1)[0].strip()  # Split the string at "CSV            
            if name:  # Only append the name to the list if it's not an empty string
                name_csv.append(name)

    df = pd.DataFrame(list(zip(name_csv, links_csv)), columns=['Name', 'links']).sort_values(by=['Name']).reset_index(drop=True)  
    #Save it as a table
    #links_df = pd.DataFrame({'links':links_csv}).sort_values(by=['links'])  
    return df

@st.cache_data
def display_dataset(df):
    dataset_name = df['Name']
    return dataset_name

@st.cache_data
def get_data(selected_rows):
    # Save the dataset as a dictionary
    downloaded_data = {}
    for Name in selected_rows['Name']:
        csv_url = selected_rows.loc[selected_rows['Name'] == Name, 'links'].values[0]
        downloaded_data[Name] = pd.read_csv(csv_url, low_memory=False)

    return downloaded_data


####App
##Title
st.header("UK Fatal RTA visualisation tool")

##User Input
#User can input a link
url = st.text_input('URL:')

@st.cache_data
#Call back function
def selected_csv(df):
    st.session_state.selected_rows = df[df['tick box'] == True]
     


#Display whether we can webscrap from this link
if url:
  #User has inputted a URL
  st.write(check_acess(url))
  full_df = load_dataset(url)
  csv_df = pd.DataFrame(display_dataset(full_df))

  # Let the user select from the dataframe indices
  selected_names = st.multiselect('Select rows:', full_df.Name)
  selected_rows = full_df[full_df['Name'].isin(selected_names)]

  # Display the selected rows
  st.write('### Selected Rows')
  st.dataframe(selected_rows)
  downloaded_data = get_data(selected_rows)
  downloaded_data
  #downloaded_data[downloaded_data['Name'].isin(selected_names)]

else:
    # The user has not inputted a URL    
  st.write("Please input an URL above")