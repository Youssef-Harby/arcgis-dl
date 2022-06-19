import argparse
import re
from .arcgis_dl import config, get_services, get_layers, get_query, write_layer
from .metadata import get_create_time, load_metadata, check_update, save_metadata


def main():
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
                create_time = get_create_time(service_url)  # get create time about this services
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

main()
