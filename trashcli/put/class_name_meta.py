# TODO: remove
class ClassNameMeta(type):
    def __repr__(cls):
        return cls.__name__
