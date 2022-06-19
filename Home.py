import streamlit as st
from arcgis_dl.__main__ import downloading
from arcgis_dl.arcgis_dl import config, get_services, get_layers, get_query, write_layer
from arcgis_dl.df_selection_table import aggrid_interactive_table
from arcgis_dl.metadata import (
    init_metadata, save_metadata, load_metadata, clear_metadata, \
    get_date_time, convet_time, check_update
)
import pandas as pd
import re

try:
    metadatas = load_metadata()
    # st.write(metadatas)
except:
    init_metadata()


def downloading(url, time_str, metadatas):
    query = get_query(url)
    if query is not None:
        layer, layer_data, layer_format = query
        data_time = convet_time(time_str)
        if data_time == -1:
            data_time = get_date_time(url)
        if check_update(url, data_time, metadatas):
            write_layer(layer, layer_data, url, layer_format)
            save_metadata({url: data_time})
        else:
            print('Skipping - no update:', url)

st.title('ArcGIS Server Downloader')
arc_url = st.text_input('ArcGIS Server Url','https://sampleserver6.arcgisonline.com/arcgis/rest/services/Energy',placeholder='Server or Folder or Layer')
arc_token_1 = st.text_input('ArcGIS Server Token')
arc_token_2 = st.text_input('ArcGIS Server Token ALT')

user_input_date = st.date_input(
     "Comparing data changes date: ")
st.write('Your selected comparing date is:', user_input_date)

if st.button('Download'):
    url = arc_url.rstrip('/')
    if re.search('/[A-Z][A-Za-z]+Server/[^/]+$', url):
        downloading(url, str(user_input_date),metadatas)
    elif re.search('/[A-Z][A-Za-z]+Server$', url):
        for layer_url in get_layers(url):
            downloading(layer_url, str(user_input_date),metadatas)
    else:  # elif re.search('/rest/services$', url)
        for service_url in get_services(url):
            for layer_url in get_layers(service_url):
                downloading(layer_url, str(user_input_date),metadatas)


meta_df = pd.read_csv('metadata.csv')

selection = aggrid_interactive_table(df=meta_df)

if selection:
    st.write("You selected:")
    st.json(selection["selected_rows"])