import streamlit as st
from arcgis_dl.log import Loger
from arcgis_dl.arcgis_dl import config, get_services, get_layers, get_query, write_layer
from arcgis_dl.df_selection_table import aggrid_interactive_table
from arcgis_dl.metadata import (
    init_metadata, save_metadata, load_metadata, clear_metadata,
    get_date_time, convet_time, check_update
)
import datetime
import pandas as pd
import re
import urllib3
import urllib3.contrib.pyopenssl

# urllib3 setting
urllib3.disable_warnings(urllib3.connectionpool.InsecureRequestWarning)
urllib3.contrib.pyopenssl.inject_into_urllib3()
# for debug
loger = Loger("home", is_init=True)
# inint metadata
st.set_page_config(layout="wide")
init_metadata()
metadatas = load_metadata()

def downloading(url, time_str, metadatas):
    query = get_query(url)
    if query is not None:
        layer, layer_data, parameters, fcount = query
        layer_format = parameters["f"]
        offset = parameters["resultOffset"]
        data_time = convet_time(time_str)
        if check_update(url, data_time, metadatas):
            write_layer(layer, layer_data, url, layer_format)
            save_metadata({url: (get_date_time(url), fcount, offset)})
            loger.info("Update metadata: add {}.".format(url))
        else:
            loger.info("Skipping - no update: {}.".format(url))


st.title('ArcGIS Server Downloader')
arc_url = st.text_input('ArcGIS Server Url',
                        'https://sampleserver6.arcgisonline.com/arcgis/rest/services/Energy',
                        placeholder='Server or Folder or Layer')

arc_token_1 = st.text_input('ArcGIS Server Token')

downloading_option = st.radio(
     "Downloading methods",
     ('Select the Layers', 'Download All Layers'),
     index=1)

if downloading_option == 'Select the Layers':
    layer_urls = get_layers(arc_url)
    # i think just need to display layer's name
    layer_names = [layer_url.replace(arc_url + "/", "") for layer_url in layer_urls]
    selected_names = st.multiselect("Select Layers to Download", layer_names)
    selected_layers = [arc_url + "/" + selected_name for selected_name in selected_names]
else:
    selected_layers = get_layers(arc_url)
loger.info("You selected: {}.".format(selected_layers))

# if you dont input, `text_input` will return str (`""` rather than `None`)
# reference: https://docs.streamlit.io/library/api-reference/widgets/st.text_input
if arc_token_1 != "":
    config['token'] = arc_token_1
else:
    config['token'] = None
loger.info("Token is: {}.".format(config['token']))

# download offset
arc_offset = st.text_input("Offset With Downloading", "0")
config['offset'] = int(arc_offset) if arc_offset != "" else 0
loger.info("Offset is: {}.".format(config['offset']))

arc_timeout = st.text_input('ArcGIS Server Timeout', "900")
# Timeout value connect was 900, but it must be an int, float or None
# we should convert str to int (`text_input` will return str)
config['timeout'] = int(arc_timeout) if arc_timeout != "" else 900
loger.info("Timeout is: {}.".format(config['timeout']))

user_input_date = st.date_input(
    "Comparing data changes date: ")
user_input_time = st.time_input(
    "Set an alarm for: ")
if isinstance(user_input_date, datetime.date):
    user_input_date = user_input_date
    user_date_time = datetime.datetime.combine(
        user_input_date, user_input_time)
    loger.info("Selected comparing date is {}.".format(str(user_date_time)))
else:
    user_date_time = datetime.datetime.now()
    loger.info("The date_input is not a `datetime.date`, aotu set now.")

st.write('Your selected comparing date is: ', user_date_time)

if st.button('Download'):
    loger.info("Downloading start!")
    with st.spinner("Please wait..."):
        url = arc_url.rstrip('/')
        if re.search('/[A-Z][A-Za-z]+Server/[^/]+$', url):
            downloading(url, user_input_date, metadatas)
        elif re.search('/[A-Z][A-Za-z]+Server$', url):
            for layer_url in selected_layers:  # get_layers(url):
                downloading(layer_url, user_input_date, metadatas)
        else:  # elif re.search('/rest/services$', url)
            for service_url in get_services(url):
                for layer_url in selected_layers:  # get_layers(service_url):
                    downloading(layer_url, user_input_date, metadatas)
    loger.info("Downloading finished!")
    st.success("Downloading finished!")
    config['token'] = None

clear_metadata()  # remove duplicate value
st.write('Table')
meta_df = pd.read_csv('metadata/metadata.csv')
selection = aggrid_interactive_table(df=meta_df)

if selection:
    st.write("You selected:")
    st.json(selection["selected_rows"])
