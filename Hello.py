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
            name = text.split("CSV '", 1)[1].split("', Dataset:", 1)[0].strip()  # Split the string at "CSV             name = text.split("CSV '", 1)[1].split("' , Dataset:", 1)[0].strip()  # Split the string at "CSV" and take the second part
            if name:  # Only append the name to the list if it's not an empty string
                name_csv.append(name)

    df = pd.DataFrame(list(zip(name_csv, links_csv)), columns=['Name', 'links']).sort_values(by=['Name'])       
    #Save it as a table
    #links_df = pd.DataFrame({'links':links_csv}).sort_values(by=['links'])  
    return df

@st.cache_data
def display_dataset(df):
    dataset_name = df['Name']
    return dataset_name

def get_data(links_df):    
    #Filter to keep only the tables I need
    donwnload_list = links_df[links_df.links.str.contains('statistics-casualty-2')].reset_index(drop=True)
    #use regex to extract the year from url
    donwnload_list['year'] = donwnload_list['links'].str.extract(r'(\d{4})')

    #Save the dataset as dictionary
    accidents = {}
    for index, row in donwnload_list.iterrows():
        accidents[row['year']] = pd.read_csv(row['links'], low_memory=False)

    full_df = accidents
    
    return full_df


####App
##Title
st.header("UK Fatal RTA visualisation tool")

##User Input
#User can input a link
url = st.text_input('URL:')


#Call back function
def selected_csv(df):
    st.session_state.selected_rows = df[df['tick box'] == True]
    
#Display whether we can webscrap from this link
if url:
    #User has inputted a URL
    st.write(check_acess(url))
    csv_df = pd.DataFrame(display_dataset(load_dataset(url)))
    csv_df['tick box'] = False
    #st.dataframe(display_dataset(load_dataset(url)))
    edited_df = st.data_editor(
        csv_df,
        column_config={
            "tick box": st.column_config.CheckboxColumn(
                "Use:",
                help = "Select the datasets you would like to use",
                default=False
            )
        },
        disabled=["widgets"],
        hide_index=True,
    )
    selected_csv(edited_df)
    #####Not quite sure about this part######
    if 'selected_rows' in st.session_state:
        st.dataframe(st.session_state.selected_rows)
    ##########################################    
else:
    # The user has not inputted a URL    
    st.write("Please input an URL above")


