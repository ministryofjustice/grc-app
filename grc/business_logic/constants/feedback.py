from flask_babel import lazy_gettext as _l, pgettext
from .base import BaseConstants


class FeedbackConstants(BaseConstants):

    YES = pgettext('FEEDBACK', 'Yes')
    NO = pgettext('FEEDBACK', 'No')
    YES_USED_DOC_CHECKER = pgettext('FEEDBACK_DOC_CHECKER', 'Yes')
    NO_USED_DOC_CHECKER = pgettext('FEEDBACK_DOC_CHECKER', 'No')

    VERY_EASY = _l('Very easy')
    EASY = _l('Easy')
    NEITHER_EASY_NOR_DIFFICULT = _l('Neither easy nor difficult')
    DIFFICULT = _l('Difficult')
    VERY_DIFFICULT = _l('Very difficult')
    COULD_NOT_COMPLETE_APPLICATION = _l("I couldn't complete  my application")

    # Errors
    HOW_EASY_TO_COMPLETE_APP_ERROR = _l('Select how easy it was to complete your application')
    QUESTIONS_DIFFICULT_TO_ANSWER_ERROR = _l('Select if you found any of the questions difficult to answer')
    NEEDED_TO_CALL_ADMIN_ERROR = _l('Select if you needed to call the admin team for help with your application')
    USE_DOC_CHECKER_ERROR = _l('Select if you used the tool to check which documents you needed to submit with your'
                               ' application')

