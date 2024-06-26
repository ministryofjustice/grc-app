from flask_wtf import FlaskForm
from grc.business_logic.constants.birth_and_registration import BirthRegistrationConstants as c
from wtforms import StringField
from grc.business_logic.data_structures.birth_registration_data import AdoptedInTheUkEnum
from grc.utils.form_custom_validators import validate_date_of_birth, Integer
from grc.lazy.lazy_form_custom_validators import LazyDataRequired, LazyInteger
from grc.lazy.lazy_fields import LazyRadioField


class NameForm(FlaskForm):
    first_name = StringField(validators=[LazyDataRequired(lazy_message=c.FIRST_NAME_ERROR)])

    middle_names = StringField() # Middle names are optional, so no validators are required here

    last_name = StringField(validators=[LazyDataRequired(lazy_message=c.LAST_NAME_ERROR)])


class DobForm(FlaskForm):
    day = StringField(
        validators=[
            LazyDataRequired(lazy_message=c.ENTER_DAY_ERROR),
            LazyInteger(min_=1, max_=31, message=c.ENTER_VALID_DAY_ERROR)
        ]
    )

    month = StringField(
        validators=[
            LazyDataRequired(lazy_message=c.ENTER_MONTH_ERROR),
            LazyInteger(min_=1, max_=12, message=c.ENTER_VALID_MONTH_ERROR)
        ]
    )

    # The user must be 18 years old or older to apply
    year = StringField(
        validators=[
            LazyDataRequired(lazy_message=c.ENTER_YEAR_ERROR),
            LazyInteger(min_=1000, message=c.ENTER_VALID_YEAR_ERROR, validators=[validate_date_of_birth])
        ]
    )


class UkCheckForm(FlaskForm):
    birth_registered_in_uk = LazyRadioField(
        lazy_choices=[
            (True, c.YES),
            (False, c.NO)
        ],
        validators=[LazyDataRequired(lazy_message=c.SELECT_BIRTH_REGISTERED_IN_UK_ERROR)]
    )


class CountryForm(FlaskForm):
    country_of_birth = StringField(validators=[LazyDataRequired(lazy_message=c.ENTER_COUNTRY_OF_BIRTH_ERROR)])


class PlaceOfBirthForm(FlaskForm):
    place_of_birth = StringField(validators=[LazyDataRequired(lazy_message=c.ENTER_PLACE_OF_BIRTH_ERROR)])


class MothersNameForm(FlaskForm):
    first_name = StringField(validators=[LazyDataRequired(lazy_message=c.ENTER_MOTHERS_FIRST_NAME_ERROR)])

    last_name = StringField(validators=[LazyDataRequired(lazy_message=c.ENTER_MOTHERS_LAST_NAME_ERROR)])

    maiden_name = StringField(validators=[LazyDataRequired(lazy_message=c.ENTER_MOTHERS_MAIDEN_NAME_ERROR)])


class FatherNameCheckForm(FlaskForm):
    fathers_name_on_certificate = LazyRadioField(
        lazy_choices=[
            (True, c.YES),
            (False, c.NO)
        ],
        validators=[LazyDataRequired(lazy_message=c.SELECT_FATHERS_NAME_ON_CERTIFICATE_ERROR)]
    )


class FathersNameForm(FlaskForm):
    first_name = StringField(validators=[LazyDataRequired(lazy_message=c.ENTER_FATHERS_FIRST_NAME_ERROR)])

    last_name = StringField(validators=[LazyDataRequired(lazy_message=c.ENTER_FATHERS_LAST_NAME_ERROR)])


class AdoptedForm(FlaskForm):
    adopted = LazyRadioField(
        lazy_choices=[
            (True, c.YES),
            (False, c.NO)
        ],
        validators=[LazyDataRequired(lazy_message=c.ENTER_ADOPTED_ERROR)]
    )


class AdoptedUKForm(FlaskForm):
    adopted_uk = LazyRadioField(
        lazy_choices=[
            (AdoptedInTheUkEnum.ADOPTED_IN_THE_UK_YES.name, c.YES),
            (AdoptedInTheUkEnum.ADOPTED_IN_THE_UK_NO.name, c.NO),
            (AdoptedInTheUkEnum.ADOPTED_IN_THE_UK_DO_NOT_KNOW.name, c.DONT_KNOW)
        ],
        validators=[LazyDataRequired(lazy_message=c.SELECT_ADOPTED_UK_ERROR)]
    )


class ForcesForm(FlaskForm):
    forces = LazyRadioField(
        lazy_choices=[
            (True, c.YES),
            (False, c.NO)
        ],
        validators=[LazyDataRequired(lazy_message=c.SELECT_FORCES_ERROR)]
    )


class CheckYourAnswers(FlaskForm):
    # There are no fields on the CheckYourAnswers form
    # But, to avoid a compiler error, we need to write 'pass' here
    pass
