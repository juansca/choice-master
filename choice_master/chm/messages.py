from django.utils.translation import ugettext_lazy as _
from django.contrib import messages


class LoadQuestionsMessageManager():
    ADDED = _('Added {0} questions')
    SYNTAX_ERROR = _('Syntax error:  "{0}"')
    INVALID_FORM = _('Please, select a valid file.')
    NO_SUBJECT = _('Not added (The subject "{0}" does not exist): "{1}"')
    NO_TOPIC = _('Not added (The topic "{0}" does not exist): "{1}"')
    VALIDATION_ERROR = _('{0}. In question "{1}"')

    def __init__(self):
        self.added = []
        self.syntax_error = None
        self.form_is_valid = True
        self.no_subject = []
        self.no_topic = []
        self.validation_errors = []
        self.messages = messages

    def set_messages(self, request):
        if not self.form_is_valid:
            messages.error(request, self.INVALID_FORM)

        if self.syntax_error:
            messages.error(request,
                           self.SYNTAX_ERROR.format(self.syntax_error))

        for e, q in self.validation_errors:
            msg = self.VALIDATION_ERROR.format('; '.join(e.messages), q)
            messages.error(request, msg)

        if self.added:
            messages.success(request, self.ADDED.format(len(self.added)))

        for s, q in self.no_subject:
            messages.error(request, self.NO_SUBJECT.format(s, q))

        for t, q in self.no_topic:
            messages.error(request, self.NO_TOPIC.format(t, q))
