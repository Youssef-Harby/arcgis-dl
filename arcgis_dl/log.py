import os.path as osp
import logging


PATH = osp.abspath(osp.dirname(osp.dirname(__file__)))
LOG_FILE_PATH = osp.join(PATH, "DEBUG.log")


class Loger:
    # avoid duplicate output
    __instance = None
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            obj = object.__new__(cls)
            cls.__instance = obj
        return cls.__instance

    def __init__(self, 
                 log_name: str, 
                 fname: str = LOG_FILE_PATH,
                 is_init: bool = False) -> None:
        if "logger" not in self.__dict__:
            self.log_name = log_name
            self.fname = fname
            self.is_init = is_init
            self._setup_logger()
        
    def _setup_logger(self) -> None:
        self.log = logging.getLogger(self.log_name)
        self.log.setLevel(logging.INFO)
        fh = logging.FileHandler(
            self.fname, 
            encoding="UTF-8",
            mode="w" if self.is_init else "a"
        )  # file
        formator = logging.Formatter(
            fmt = "[%(asctime)s] => %(message)s",
            datefmt="%Y/%m/%d %X"
        )
        fh.setFormatter(formator)
        self.log.addHandler(fh)

    def info(self, inf: str) -> None:
        self.log.info(inf)
