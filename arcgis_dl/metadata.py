import os.path as osp
import requests
import pandas as pd
import json
import typing
import time
import datetime


METADATAS_PATH = "metadata.csv"


# def _check_time_format(input_time: str) -> bool:
#     try:        
#         datetime.datetime.strptime(input_time, '%Y-%m-%d %H:%M:%S')        
#         return True
#     except ValueError:  
#         return False


def convet_time(input_time: datetime.datetime) -> int:
    time_array = input_time.timetuple()
    return int(round(time.mktime(time_array) * 1000))


def _get_date_time(json_data: typing.Dict) -> int:
    if "editingInfo" in json_data.keys():
        date_time = json_data["editingInfo"]["lastEditDate"]
    else:
        date_time = int(round(time.time() * 1000))
    return date_time


def get_date_time(layer_url: str) -> int:
    request = requests.get(layer_url + "?f=pjson")
    json_info = json.loads(request.text)
    date_time = _get_date_time(json_info)
    return date_time


def init_metadata(meta_path: str = METADATAS_PATH) -> None:
    if osp.exists(meta_path):
        pass
    else:
        columns = ["LayerLink", "LastEditDate"]
        pd.DataFrame(data=None, columns=columns).to_csv(meta_path, index=False, mode="w")


def save_metadata(meta_dict: typing.Dict, 
                  meta_path: str = METADATAS_PATH) -> None:
    data_list = []
    for k, v in meta_dict.items():
        data_list.append([k, v])
    columns = ["LayerLink", "LastEditDate"]
    pdd = pd.DataFrame(data=data_list, columns=columns)
    pdd.to_csv(meta_path, header=False, index=False, mode="a")


def _df2dict(df: pd.DataFrame) -> typing.Dict:
    keys = []
    values = []
    for link in df["LayerLink"]:
        keys.append(link)
    for date in df["LastEditDate"]:
        values.append(date)
    meta_dict = dict(zip(keys, values))
    return meta_dict


def load_metadata(meta_path: str = METADATAS_PATH) -> typing.Dict:
    pdd = pd.read_csv(meta_path)
    # duplicate values keep the latest
    pdd.drop_duplicates(subset=["LayerLink"], keep="last", inplace=True)
    return _df2dict(pdd)


def clear_metadata(meta_path: str = METADATAS_PATH) -> None:
    if osp.exists(meta_path):
        pdd = pd.read_csv(meta_path)
        # duplicate values keep the latest
        pdd.drop_duplicates(subset=["LayerLink"], keep="last", inplace=True)
        pdd.to_csv(meta_path, index=False, mode="w")


def check_update(layer_url: str, date_time: int, metadatas: typing.Dict) -> bool:
    if layer_url not in metadatas.keys() or date_time > metadatas[layer_url]:
        # if `layer_url` not in metadatas (we have not this layer), we need download
        # if input date is later than metadata's date, we need download
        return True
    # we don't need download
    return False


if __name__ == "__main__":
    # test get time
    test_url_1 = "https://services6.arcgis.com/bKYAIlQgwHslVRaK/ArcGIS/rest/services/CasesByGovernoratesViewLayer/FeatureServer/0"
    test_url_2 = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Energy/Geology/FeatureServer"
    time_1 = get_date_time(test_url_1)
    time_2 = get_date_time(test_url_2)
    print(str(time_1) + "\n" + str(time_2))  # time_1 is fixed and time_2 is real time
    # test save csv
    test_dict = {
        test_url_1: time_1,
        test_url_2: time_2
    }
    init_metadata()
    save_metadata(test_dict)
    clear_metadata()
    # test read csv
    meta_dict = load_metadata()
    print(meta_dict)  # should be {layer_link: date_time}
    # test time convet
    dt = datetime.datetime(2022, 6, 19, 10, 25, 23)
    print(convet_time(dt))  # should be 1655605523000
    # test check
    dt_1 = datetime.datetime(2018, 2, 12, 12, 24, 15)
    dt_2 = datetime.datetime(2050, 6, 20, 18, 17, 00)
    print(check_update(test_url_1, convet_time(dt_1), meta_dict))  # should be False
    print(check_update(test_url_2, convet_time(dt_2), meta_dict))  # should be True
