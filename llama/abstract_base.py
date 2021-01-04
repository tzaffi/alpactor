from abc import abstractmethod, abstractclassmethod

from abc import ABCMeta as NativeABCMeta


class DummyAttribute:
    pass


def abstract_attribute(obj=None):
    if obj is None:
        obj = DummyAttribute()
    obj.__is_abstract_attribute__ = True
    return obj


class ABCMeta(NativeABCMeta):
    """
    copied from: https://stackoverflow.com/questions/23831510/abstract-attribute-not-property/23833055
    """

    def __call__(cls, *args, **kwargs):
        instance = NativeABCMeta.__call__(cls, *args, **kwargs)
        abstract_attributes = {
            name for name in dir(instance) if getattr(getattr(instance, name), "__is_abstract_attribute__", False)
        }
        if abstract_attributes:
            raise NotImplementedError(
                "Can't instantiate abstract class {} with"
                " abstract attributes: {}".format(cls.__name__, ", ".join(abstract_attributes))
            )
        return instance


class LlamaABC(metaclass=ABCMeta):
    @abstractclassmethod
    def from_event_json(cls, j: str, debug: bool = False):
        pass

    @abstractclassmethod
    def is_immutable(cls) -> bool:
        pass

    @abstractclassmethod
    def has_timestamp(cls) -> bool:
        pass

    @abstractclassmethod
    def db_table_name(cls) -> str:
        pass

    @abstract_attribute
    def table_id(self) -> str:
        pass

    @abstractmethod
    def as_dict(self) -> dict:
        pass

    @abstractmethod
    def as_event_json(self) -> str:
        pass
