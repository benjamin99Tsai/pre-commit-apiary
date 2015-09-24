from pre_commit_hook.error import ApiarySyntaxError

__author__ = 'admin'

import re

_tab = re.compile('\t').search


class PreValidationBaseMixin(object):
    def pre_validate(self, line):
        return True, None


class PreValidationTabMixin(PreValidationBaseMixin):
    def pre_validate(self, line):
        if _tab(line) is not None:
            valid, error = False, ApiarySyntaxError(message='contains tab in line')
        else:
            valid, error = super(PreValidationTabMixin, self).pre_validate(line)
        return valid, error
