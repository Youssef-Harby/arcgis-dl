import streamlit as st
from arcgis_dl.log import Loger
from arcgis_dl.arcgis_dl import get_services, get_layers, get_query, write_layer
from arcgis_dl.df_selection_table import aggrid_interactive_table
from arcgis_dl.metadata import (
    init_metadata, save_metadata, load_metadata, clear_metadata, \
    get_date_time, convet_time, check_update
)
import datetime
import pandas as pd
import re

# for debug
loger = Loger("home", is_init=True)
# inint metadata
init_metadata()
metadatas = load_metadata()


def downloading(url, time_str, metadatas):
    query = get_query(url)
    if query is not None:
        layer, layer_data, layer_format = query
        data_time = convet_time(time_str)
        if check_update(url, data_time, metadatas):
            write_layer(layer, layer_data, url, layer_format)
            save_metadata({url: get_date_time(url)})
            loger.info("Update metadata: add {}.".format(url))
        else:
            loger.info("Skipping - no update: {}.".format(url))

st.title('ArcGIS Server Downloader')
arc_url = st.text_input('ArcGIS Server Url', 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/Energy',placeholder='Server or Folder or Layer')
arc_token_1 = st.text_input('ArcGIS Server Token')
arc_token_2 = st.text_input('ArcGIS Server Token ALT')

user_input_date = st.date_input(
    "Comparing data changes date: ")
user_input_time = st.time_input(
    "Set an alarm for: ")
if isinstance(user_input_date, datetime.date):
    user_input_date = user_input_date
    user_date_time = datetime.datetime.combine(user_input_date, user_input_time)
    loger.info("Selected comparing date is {}.".format(str(user_date_time)))
else:
    user_date_time = datetime.datetime.now()
    loger.info("The date_input is not a `datetime.date`, aotu set now.")

st.write('Your selected comparing date is: ', user_date_time)

if st.button('Download'):
    loger.info("Downloading start!")
    url = arc_url.rstrip('/')
    if re.search('/[A-Z][A-Za-z]+Server/[^/]+$', url):
        downloading(url, user_input_date, metadatas)
    elif re.search('/[A-Z][A-Za-z]+Server$', url):
        for layer_url in get_layers(url):
            downloading(layer_url, user_input_date, metadatas)
    else:  # elif re.search('/rest/services$', url)
        for service_url in get_services(url):
            for layer_url in get_layers(service_url):
                downloading(layer_url, user_input_date, metadatas)
    loger.info("Downloading finished!")

clear_metadata()  # remove duplicate value
st.write('Table')
meta_df = pd.read_csv('metadata.csv')
selection = aggrid_interactive_table(df=meta_df)

if selection:
    st.write("You selected:")
    st.json(selection["selected_rows"])
