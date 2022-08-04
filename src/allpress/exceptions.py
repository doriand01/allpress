
class NoParagraphDataError(Exception):

    def __init__(self, msg):
        super().__init__(msg)

class ForeignKeyWithoutReferenceError(Exception):

    def __init__(self, msg):
        super().__init__(msg)

class TranslationError:

    def __init__(self, msg):
        super().__init__(msg)