import streamlit as st
from arcgis_dl.arcgis_dl import config, get_services, get_layers, get_query, write_layer
from arcgis_dl.df_selection_table import aggrid_interactive_table
from arcgis_dl.metadata import load_metadata, check_update, save_metadata
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import pandas as pd
import re

st.title('ArcGIS Server Downloader')
arc_url = st.text_input('ArcGIS Server Url','https://sampleserver6.arcgisonline.com/arcgis/rest/services/Energy',placeholder='Server or Folder or Layer')
arc_token_1 = st.text_input('ArcGIS Server Token')
arc_token_2 = st.text_input('ArcGIS Server Token ALT')

user_input_date = st.date_input(
     "Comparing data changes date: ")
st.write('Your selected comparing date is:', user_input_date)

if st.button('Download'):
    metadatas = load_metadata()
    url = arc_url.rstrip('/')
    print(url)
    if re.search('/[A-Z][A-Za-z]+Server/[^/]+$', url):
        query = get_query(url)
        if query is not None:
            layer, layer_data, layer_format = query
            write_layer(layer, layer_data, url, layer_format)
    elif re.search('/[A-Z][A-Za-z]+Server$', url):
        for layer_url in get_layers(url):
            query = get_query(layer_url)
            if query is not None:
                layer, layer_data, layer_format = query
                write_layer(layer, layer_data, layer_url, layer_format)
    # elif re.search('/rest/services$', url):
    else:
        for service_url in get_services(url):
            create_time = check_update(service_url)  # get create time about this services
            # if services data is change, downloading, else skipping
            if check_update(service_url, create_time, metadatas):
                for layer_url in get_layers(service_url):
                    query = get_query(layer_url)
                    if query is not None:
                        layer, layer_data, layer_format = query
                        write_layer(layer, layer_data, layer_url, layer_format)
                # update metadata
                metadatas[service_url] = create_time
            else:
                print('Skipping - service not update', service_url)
        save_metadata(metadatas)  # save new metadata


meta_df = pd.read_csv('metadata.csv')

selection = aggrid_interactive_table(df=meta_df)

if selection:
    st.write("You selected:")
    st.json(selection["selected_rows"])