__author__ = 'admin'

class ApiaryError:

    def __init__(self, error_type='BaseError', message=None):
        self.message = message
        self.type = error_type

    def __str__(self):
        return '[%s] %s' % (self.type, self.message)


class ApiarySyntaxError(ApiaryError):

    def __init__(self, message=None):
        self.message = message
        self.type = 'SyntaxError'

