import os.path as osp
import requests
import pandas as pd
import typing
import time


METADATAS_PATH = "metadata.csv"


def _get_date_time(html_str: str) -> str:
    SSTR = "<b>Last Edit Date:</b>"
    ESTR = "<br/>"
    idx_start = html_str.find(SSTR)
    if idx_start != -1:  # Last Edit Date is find
        idx_start = html_str.find(SSTR) + len(SSTR)
        idx_end = idx_start + html_str[idx_start: ].find(ESTR)
        date_time = html_str[idx_start: idx_end].strip()
    else:  # Last Edit Date not find
        tm = time.localtime(time.time())
        ymd = "/".join([str(tm.tm_mon), str(tm.tm_mday), str(tm.tm_year)])
        hms = ":".join([str(tm.tm_hour if tm.tm_hour < 12 else tm.tm_hour - 12), str(tm.tm_min), str(tm.tm_sec)])
        ap = "AM" if tm.tm_hour < 12 else "PM"
        date_time = " ".join([ymd, hms, ap])
    return date_time


def get_date_time(layer_url: str) -> str:
    request = requests.get(layer_url)
    date_time = _get_date_time(request.text)
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


def check_update(layer_url: str, date_time: str, metadatas: typing.Dict) -> bool:
    if layer_url in metadatas.keys() and date_time == metadatas[layer_url]:
        return False
    return True


if __name__ == "__main__":
    # test get time
    test_url_1 = "https://services6.arcgis.com/bKYAIlQgwHslVRaK/ArcGIS/rest/services/CasesByGovernoratesViewLayer/FeatureServer/0"
    test_url_2 = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Energy/Geology/FeatureServer"
    time_1 = get_date_time(test_url_1)
    time_2 = get_date_time(test_url_2)
    print(time_1 + "\n" + time_2)  # time_1 is fixed and time_2 is real time
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
    # test check
    print(check_update(test_url_1, get_date_time(test_url_1), meta_dict))  # should be False
    print(check_update(test_url_2, get_date_time(test_url_2), meta_dict))  # should be True
