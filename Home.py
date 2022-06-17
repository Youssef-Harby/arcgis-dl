from prometheus_client import generate_latest
import streamlit as st
from arcgis_dl.arcgis_dl import config, get_services, get_layers, get_query, write_layer
import re

st.title('ArcGIS Server Downloader')
arc_url = st.text_input('ArcGIS Server Url','https://sampleserver6.arcgisonline.com/arcgis/rest/services/Energy',placeholder='Server or Folder or Layer')
arc_token_1 = st.text_input('ArcGIS Server Token')
arc_token_2 = st.text_input('ArcGIS Server Token ALT')

if st.button('Download'):
    url = arc_url.rstrip('/')
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
    #elif re.search('/rest/services$', url):
    else:
        for service_url in get_services(url):
            for layer_url in get_layers(service_url):
                query = get_query(layer_url)
                if query is not None:
                    layer, layer_data, layer_format = query
                    write_layer(layer, layer_data, layer_url, layer_format)