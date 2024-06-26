from flask_wtf import FlaskForm
from grc.business_logic.constants.feedback import FeedbackConstants as c
from grc.lazy.lazy_form_custom_validators import LazyDataRequired
from wtforms import StringField, RadioField


class FeedbackForm(FlaskForm):
    how_easy_to_complete_application = RadioField(
        choices=[
            ('1_VERY_EASY', c.VERY_EASY),
            ('2_EASY', c.EASY),
            ('3_NEUTRAL', c.NEITHER_EASY_NOR_DIFFICULT),
            ('4_DIFFICULT', c.DIFFICULT),
            ('5_VERY_DIFFICULT', c.VERY_DIFFICULT),
            ('6_COULD_NOT_COMPLETE', c.COULD_NOT_COMPLETE_APPLICATION)
        ],
        validators=[LazyDataRequired(lazy_message=c.HOW_EASY_TO_COMPLETE_APP_ERROR)]
    )

    any_questions_difficult_to_answer = RadioField(
        choices=[
            ('YES', c.YES),
            ('NO', c.NO)
        ],
        validators=[LazyDataRequired(lazy_message=c.QUESTIONS_DIFFICULT_TO_ANSWER_ERROR)]
    )

    which_questions_difficult_to_answer = StringField()

    needed_to_call_admin_team = RadioField(
        choices=[
            ('YES', c.YES),
            ('NO', c.NO)
        ],
        validators=[LazyDataRequired(lazy_message=c.NEEDED_TO_CALL_ADMIN_ERROR)]
    )

    what_did_you_need_help_with = StringField()

    used_doc_checker = RadioField(
        choices=[
            ('YES', c.YES),
            ('NO', c.NO),
            ('DO_NOT_KNOW', c.DONT_KNOW)
        ],
        validators=[LazyDataRequired(lazy_message=c.USE_DOC_CHECKER_ERROR)]
    )

    experience_of_using_doc_checker = StringField()

    any_other_suggestions = StringField()
