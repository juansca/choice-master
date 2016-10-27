from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

class LoadQuestionsMessageManager():
    ADDED = _('Added {0} questions')
    SIMILAR = _('Not added (similar exists): "{0}"')
    REPEATED = _('Not added (already exists): "{0}"')
    SYNTAX_ERROR = _('Syntax error:  "{0}"')
    INVALID_FORM = _('Please, select a file.')
    NO_SUBJECT = _('Not added (The subject "{0}" does not exist): "{1}"')
    NO_TOPIC = _('Not added (The topic "{0}" does not exist): "{1}"')

    def __init__(self):
        self.added = []
        self.similar = []
        self.repeated = []
        self.syntax_error = None
        self.valid_form = True
        self.non_existent_subjects = []
        self.non_existent_topics = []

    def set_messages(self, request):
        if not self.valid_form:
            messages.error(request, self.INVALID_FORM)

        if self.syntax_error:
            messages.error(request,
                           self.SYNTAX_ERROR.format(self.syntax_error))

        if self.added:
            messages.success(request, self.ADDED.format(len(self.added)))

        for q in self.similar:
            messages.warning(request, self.SIMILAR.format(q))

        for q in self.repeated:
            messages.error(request, self.REPEATED.format(q))

        for s, q in self.non_existent_subjects:
            messages.error(request, self.NO_SUBJECT.format(s, q))

        for t, q in self.non_existent_topics:
            messages.error(request, self.NO_TOPIC.format(t, q))
