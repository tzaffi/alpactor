import logging


def log(obj_or_info: object, level: int = logging.INFO, msg: str = None):
    qualifier = obj_or_info if isinstance(obj_or_info, str) else type(obj_or_info).__qualname__
    logging.log(level, "%s:[%s]<msg:%s>", qualifier, obj_or_info, msg)
