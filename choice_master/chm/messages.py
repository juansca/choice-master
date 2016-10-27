from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

class LoadQuestionsMessageManager():
    ADDED = _('Added: %s')
    SIMILAR = _('Not Added (similar exists): %s')
    REPEATED = _('Not Added (already exits): %s')
    SYNTAX_ERROR = _('Syntax error:  %s')
    INVALID_FORM = _('Please, select a file.')

    def __init__(self):
        self.added = []
        self.similar = []
        self.repeated = []
        self.syntax_error = None
        self.valid_form = True

    def set_messages(self, request):
        if not self.valid_form:
            messages.error(request, self.INVALID_FORM)

        if self.syntax_error:
            messages.error(request, self.SYNTAX_ERROR % self.syntax_error)

        for q in self.added:
            messages.success(request, self.ADDED % q)

        for q in self.similar:
            messages.warning(request, self.SIMILAR % q)

        for q in self.repeated:
            messages.error(request, self.REPEATED % q)
