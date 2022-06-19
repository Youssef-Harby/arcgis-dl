import argparse
import datetime
import re
from .arcgis_dl import config, get_services, get_layers, get_query, write_layer
from .metadata import (
    init_metadata, save_metadata, load_metadata, clear_metadata, \
    get_date_time, convet_time, check_update
)


def downloading(url, time_str, metadatas):
    query = get_query(url)
    if query is not None:
        layer, layer_data, layer_format = query
        if isinstance(data_time, datetime.datetime()):
            data_time = convet_time(time_str)
        else:
            data_time = get_date_time(url)
        if check_update(url, data_time, metadatas):
            write_layer(layer, layer_data, url, layer_format)
            save_metadata({url: data_time})
        else:
            print('Skipping - no update:', url)


def main():
    # TODO: add input time
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cache-dir',
                        help='directory to write cache of raw content. default: None')
    parser.add_argument('-l', '--layer-dir',
                        help='directory to write layers. default: layers')
    parser.add_argument('-f', '--layer-format', choices=('geojson', 'json'), type=str.lower,
                        help='preferred format of layers to download. default: GeoJSON')
    parser.add_argument('-t', '--layer-type', action='append', type=str.lower,
                        help='type(s) of layers to download. default: Feature Layer, Table')
    parser.add_argument('-k', '--token',
                        help='authentication token')
    parser.add_argument('url', nargs='+',
                        help='site url, folder url, service url, or layer url. requires at least one url.')
    args = parser.parse_args()

    metadatas = load_metadata()

    vargs = vars(args)
    for arg in vargs:
        if vargs[arg] is not None:
            config[arg] = vargs[arg]
            print(config)

    for url in args.url:
        url = url.rstrip('/')
        if re.search('/[A-Z][A-Za-z]+Server/[^/]+$', url):
            downloading(url, metadatas)
        elif re.search('/[A-Z][A-Za-z]+Server$', url):
            for layer_url in get_layers(url):
                downloading(layer_url, metadatas)
        else:  # elif re.search('/rest/services$', url)
            for service_url in get_services(url):
                for layer_url in get_layers(service_url):
                    downloading(layer_url, metadatas)


if __name__ == "__main__":
    # init meta or pass
    init_metadata()
    # run main func
    main()
    # clear csv
    clear_metadata()
