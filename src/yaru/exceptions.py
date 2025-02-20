class YaruError(Exception):
    pass


class MissingArgumentTypeHintError(YaruError):
    pass


class InvalidAnnotationTypeError(YaruError):
    pass


class InvalidArgumentTypeHintError(YaruError):
    pass
