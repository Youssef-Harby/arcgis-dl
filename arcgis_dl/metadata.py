import os.path as osp
import requests
import typing
import pyarrow as pa
import pyarrow.parquet as pq
import xml.etree.ElementTree as ET


METADATAS_PATH = "metadata.parquet"


def get_create_time(url: str) -> str:
    meta_url = url + "/info/metadata"
    request = requests.get(meta_url)
    root = ET.fromstring(request.text)
    esri = root.find("Esri")
    if esri is not None:
        date = esri.find("CreaDate")
        time = esri.find("CreaTime")
        if date is not None and time is not None:
            server_create_time = str(date.text) + str(time.text)
            return server_create_time
    return ""


def check_update(url: str, create_time: str, metadatas: typing.Dict) -> bool:
    if url in metadatas.keys() and create_time == metadatas[url]:
        return False
    return True


def save_metadata(rest_metas: typing.Dict, 
                  metadata_path: str = METADATAS_PATH) -> None:
    table = pa.Table.from_pydict(rest_metas)
    pq.write_table(table, metadata_path, compression="GZIP")


def load_metadata(metadata_path: str = METADATAS_PATH) -> typing.Dict:
    if osp.exists(metadata_path):
        table = pq.read_table(metadata_path)
        rest_metas = table.to_pydict()
        for k, v in rest_metas.items():
            rest_metas[k] = "".join(v)
        return rest_metas
    else:
        return {}


if __name__ == "__main__":
    # # test
    # rest_metas = {
    #     "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Energy/Geology/FeatureServer": "2018020817395100",
    #     "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Energy/Geology/MapServer": "2018020817395100",
    #     "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Energy/HSEC/FeatureServer": "2018020818053900",
    #     "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Energy/HSEC/MapServer": "2018020818053900",
    #     "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Energy/Infrastructure/FeatureServer": "2018020818461800",
    #     "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Energy/Infrastructure/MapServer": "2018020818461800"
    # }
    test_url = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Energy/Geology/FeatureServer"
    create_time = get_create_time(test_url)
    print(create_time)
    # save_metadata(rest_metas)
    metadatas = load_metadata()
    print(metadatas)
    print(check_update(test_url, create_time, metadatas))
