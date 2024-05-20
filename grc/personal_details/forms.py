from flask_wtf import FlaskForm
from grc.business_logic.constants.personal_details import PersonalDetailsConstants as c
from grc.business_logic.data_structures.personal_details_data import AffirmedGender, ContactDatesAvoid
from grc.lazy.lazy_fields import LazyRadioField, LazyMultiSelectField
from grc.lazy.lazy_form_custom_validators import LazyDataRequired, LazyInteger, LazyEmail
from grc.utils.form_custom_validators import StrictRequiredIf, validate_national_insurance_number, validate_address_field, validate_postcode, validate_date_of_transition, validate_phone_number, validate_statutory_declaration_date, validate_single_date
from wtforms import EmailField, StringField, TelField, SelectField, FieldList, FormField, SubmitField
from wtforms.form import Form


class NameForm(FlaskForm):
    title = StringField(
        validators=[LazyDataRequired(lazy_message=c.TITLE_ERROR)]
    )

    first_name = StringField(
        validators=[LazyDataRequired(lazy_message=c.FIRST_NAME_ERROR)]
    )

    middle_names = StringField()

    last_name = StringField(
        validators=[LazyDataRequired(message=c.LAST_NAME_ERROR)]
    )


class AffirmedGenderForm(FlaskForm):
    affirmedGender = LazyRadioField(
        lazy_choices=[
            (AffirmedGender.MALE.name, c.MALE),
            (AffirmedGender.FEMALE.name, c.FEMALE)
        ],
        validators=[LazyDataRequired(lazy_message=c.NO_AFFIRMED_GENDER_ERROR)]
    )


class TransitionDateForm(FlaskForm):
    transition_date_month = StringField(
        validators=[
            LazyDataRequired(lazy_message=c.ENTER_MONTH_ERROR),
            LazyInteger(min_=1, max_=12, message=c.ENTER_VALID_MONTH_ERROR)
        ]
    )

    transition_date_year = StringField(
        validators=[
            LazyDataRequired(lazy_message=c.ENTER_YEAR_ERROR),
            LazyInteger(min_=1000, message=c.ENTER_VALID_YEAR_ERROR, validators=[validate_date_of_transition])
        ]
    )


class StatutoryDeclarationDateForm(FlaskForm):
    statutory_declaration_date_day = StringField(
        validators=[
            LazyDataRequired(lazy_message=c.ENTER_DAY_ERROR),
            LazyInteger(min_=1, max_=31, lazy_message=c.ENTER_VALID_DAY_ERROR)
        ]
    )

    statutory_declaration_date_month = StringField(
        validators=[
            LazyDataRequired(lazy_message=c.ENTER_MONTH_ERROR),
            LazyInteger(min_=1, max_=12, lazy_message=c.ENTER_VALID_MONTH_ERROR)
        ]
    )

    statutory_declaration_date_year = StringField(
        validators=[
            LazyDataRequired(lazy_message=c.ENTER_YEAR_ERROR),
            LazyInteger(min_=1000, lazy_message=c.ENTER_VALID_YEAR_ERROR,
                        validators=[validate_statutory_declaration_date])
        ]
    )


class PreviousNamesCheck(FlaskForm):
    previousNameCheck = LazyRadioField(
        lazy_choices=[
            (True, c.YES),
            (False, c.NO)
        ],
        validators=[LazyDataRequired(lazy_message=c.PREVIOUS_NAME_CHECK_ERROR)]
    )


class AddressForm(FlaskForm):
    address_line_one = StringField(
        validators=[LazyDataRequired(lazy_message=c.ADDRESS_ERROR), validate_address_field]
    )

    address_line_two = StringField(validators=[validate_address_field])

    town = StringField(
        validators=[LazyDataRequired(lazy_message=c.ADDRESS_NO_TOWN_ERROR), validate_address_field]
    )

    country = SelectField(
        choices=[
            ('', ''),
            ('United Kingdom', 'United Kingdom'),
            ('Afghanistan', 'Afghanistan'),
            ('Albania', 'Albania'),
            ('Algeria', 'Algeria'),
            ('Andorra', 'Andorra'),
            ('Angola', 'Angola'),
            ('Antigua and Barbuda', 'Antigua and Barbuda'),
            ('Argentina', 'Argentina'),
            ('Armenia', 'Armenia'),
            ('Australia', 'Australia'),
            ('Austria', 'Austria'),
            ('Azerbaijan', 'Azerbaijan'),
            ('Bahrain', 'Bahrain'),
            ('Bangladesh', 'Bangladesh'),
            ('Barbados', 'Barbados'),
            ('Belarus', 'Belarus'),
            ('Belgium', 'Belgium'),
            ('Belize', 'Belize'),
            ('Benin', 'Benin'),
            ('Bhutan', 'Bhutan'),
            ('Bolivia', 'Bolivia'),
            ('Bosnia and Herzegovina', 'Bosnia and Herzegovina'),
            ('Botswana', 'Botswana'),
            ('Brazil', 'Brazil'),
            ('Brunei', 'Brunei'),
            ('Bulgaria', 'Bulgaria'),
            ('Burkina Faso', 'Burkina Faso'),
            ('Burundi', 'Burundi'),
            ('Cambodia', 'Cambodia'),
            ('Cameroon', 'Cameroon'),
            ('Canada', 'Canada'),
            ('Cape Verde', 'Cape Verde'),
            ('Central African Republic', 'Central African Republic'),
            ('Chad', 'Chad'),
            ('Chile', 'Chile'),
            ('China', 'China'),
            ('Colombia', 'Colombia'),
            ('Comoros', 'Comoros'),
            ('Congo', 'Congo'),
            ('Congo (Democratic Republic)', 'Congo (Democratic Republic)'),
            ('Costa Rica', 'Costa Rica'),
            ('Croatia', 'Croatia'),
            ('Cuba', 'Cuba'),
            ('Cyprus', 'Cyprus'),
            ('Czechia', 'Czechia'),
            ('Denmark', 'Denmark'),
            ('Djibouti', 'Djibouti'),
            ('Dominica', 'Dominica'),
            ('Dominican Republic', 'Dominican Republic'),
            ('East Timor', 'East Timor'),
            ('Ecuador', 'Ecuador'),
            ('Egypt', 'Egypt'),
            ('El Salvador', 'El Salvador'),
            ('Equatorial Guinea', 'Equatorial Guinea'),
            ('Eritrea', 'Eritrea'),
            ('Estonia', 'Estonia'),
            ('Eswatini', 'Eswatini'),
            ('Ethiopia', 'Ethiopia'),
            ('Fiji', 'Fiji'),
            ('Finland', 'Finland'),
            ('France', 'France'),
            ('Gabon', 'Gabon'),
            ('Georgia', 'Georgia'),
            ('Germany', 'Germany'),
            ('Ghana', 'Ghana'),
            ('Greece', 'Greece'),
            ('Grenada', 'Grenada'),
            ('Guatemala', 'Guatemala'),
            ('Guinea', 'Guinea'),
            ('Guinea-Bissau', 'Guinea-Bissau'),
            ('Guyana', 'Guyana'),
            ('Haiti', 'Haiti'),
            ('Honduras', 'Honduras'),
            ('Hungary', 'Hungary'),
            ('Iceland', 'Iceland'),
            ('India', 'India'),
            ('Indonesia', 'Indonesia'),
            ('Iran', 'Iran'),
            ('Iraq', 'Iraq'),
            ('Ireland', 'Ireland'),
            ('Israel', 'Israel'),
            ('Italy', 'Italy'),
            ('Ivory Coast', 'Ivory Coast'),
            ('Jamaica', 'Jamaica'),
            ('Japan', 'Japan'),
            ('Jordan', 'Jordan'),
            ('Kazakhstan', 'Kazakhstan'),
            ('Kenya', 'Kenya'),
            ('Kiribati', 'Kiribati'),
            ('Kosovo', 'Kosovo'),
            ('Kuwait', 'Kuwait'),
            ('Kyrgyzstan', 'Kyrgyzstan'),
            ('Laos', 'Laos'),
            ('Latvia', 'Latvia'),
            ('Lebanon', 'Lebanon'),
            ('Lesotho', 'Lesotho'),
            ('Liberia', 'Liberia'),
            ('Libya', 'Libya'),
            ('Liechtenstein', 'Liechtenstein'),
            ('Lithuania', 'Lithuania'),
            ('Luxembourg', 'Luxembourg'),
            ('Madagascar', 'Madagascar'),
            ('Malawi', 'Malawi'),
            ('Malaysia', 'Malaysia'),
            ('Maldives', 'Maldives'),
            ('Mali', 'Mali'),
            ('Malta', 'Malta'),
            ('Marshall Islands', 'Marshall Islands'),
            ('Mauritania', 'Mauritania'),
            ('Mauritius', 'Mauritius'),
            ('Mexico', 'Mexico'),
            ('Micronesia', 'Micronesia'),
            ('Moldova', 'Moldova'),
            ('Monaco', 'Monaco'),
            ('Mongolia', 'Mongolia'),
            ('Montenegro', 'Montenegro'),
            ('Morocco', 'Morocco'),
            ('Mozambique', 'Mozambique'),
            ('Myanmar (Burma)', 'Myanmar (Burma)'),
            ('Namibia', 'Namibia'),
            ('Nauru', 'Nauru'),
            ('Nepal', 'Nepal'),
            ('Netherlands', 'Netherlands'),
            ('New Zealand', 'New Zealand'),
            ('Nicaragua', 'Nicaragua'),
            ('Niger', 'Niger'),
            ('Nigeria', 'Nigeria'),
            ('North Korea', 'North Korea'),
            ('North Macedonia', 'North Macedonia'),
            ('Norway', 'Norway'),
            ('Oman', 'Oman'),
            ('Pakistan', 'Pakistan'),
            ('Palau', 'Palau'),
            ('Panama', 'Panama'),
            ('Papua New Guinea', 'Papua New Guinea'),
            ('Paraguay', 'Paraguay'),
            ('Peru', 'Peru'),
            ('Philippines', 'Philippines'),
            ('Poland', 'Poland'),
            ('Portugal', 'Portugal'),
            ('Qatar', 'Qatar'),
            ('Romania', 'Romania'),
            ('Russia', 'Russia'),
            ('Rwanda', 'Rwanda'),
            ('Samoa', 'Samoa'),
            ('San Marino', 'San Marino'),
            ('Sao Tome and Principe', 'Sao Tome and Principe'),
            ('Saudi Arabia', 'Saudi Arabia'),
            ('Senegal', 'Senegal'),
            ('Serbia', 'Serbia'),
            ('Seychelles', 'Seychelles'),
            ('Sierra Leone', 'Sierra Leone'),
            ('Singapore', 'Singapore'),
            ('Slovakia', 'Slovakia'),
            ('Slovenia', 'Slovenia'),
            ('Solomon Islands', 'Solomon Islands'),
            ('Somalia', 'Somalia'),
            ('South Africa', 'South Africa'),
            ('South Korea', 'South Korea'),
            ('South Sudan', 'South Sudan'),
            ('Spain', 'Spain'),
            ('Sri Lanka', 'Sri Lanka'),
            ('St Kitts and Nevis', 'St Kitts and Nevis'),
            ('St Lucia', 'St Lucia'),
            ('St Vincent', 'St Vincent'),
            ('Sudan', 'Sudan'),
            ('Suriname', 'Suriname'),
            ('Sweden', 'Sweden'),
            ('Switzerland', 'Switzerland'),
            ('Syria', 'Syria'),
            ('Tajikistan', 'Tajikistan'),
            ('Tanzania', 'Tanzania'),
            ('Thailand', 'Thailand'),
            ('The Bahamas', 'The Bahamas'),
            ('The Gambia', 'The Gambia'),
            ('Togo', 'Togo'),
            ('Tonga', 'Tonga'),
            ('Trinidad and Tobago', 'Trinidad and Tobago'),
            ('Tunisia', 'Tunisia'),
            ('Turkey', 'Turkey'),
            ('Turkmenistan', 'Turkmenistan'),
            ('Tuvalu', 'Tuvalu'),
            ('Uganda', 'Uganda'),
            ('Ukraine', 'Ukraine'),
            ('United Arab Emirates', 'United Arab Emirates'),
            ('United Kingdom', 'United Kingdom'),
            ('United States', 'United States'),
            ('Uruguay', 'Uruguay'),
            ('Uzbekistan', 'Uzbekistan'),
            ('Vanuatu', 'Vanuatu'),
            ('Vatican City', 'Vatican City'),
            ('Venezuela', 'Venezuela'),
            ('Vietnam', 'Vietnam'),
            ('Yemen', 'Yemen'),
            ('Zambia', 'Zambia'),
            ('Zimbabwe', 'Zimbabwe')
        ]
    )

    postcode = StringField(
        validators=[StrictRequiredIf('country', ['', 'United Kingdom'],
                                     message=c.NO_POSTCODE_ERROR, validators=[validate_postcode])]
    )


class ContactPreferencesForm(FlaskForm):
    contact_options = LazyMultiSelectField(
        lazy_choices=[
            ('EMAIL', c.EMAIL),
            ('PHONE', c.PHONE),
            ('POST', c.POST)
        ],
        validators=[LazyDataRequired(lazy_message=c.NO_CONTACT_PREFERENCES_ERROR)]
    )

    email = EmailField(
        validators=[StrictRequiredIf('contact_options', 'EMAIL', message=c.NO_EMAIL_ADDRESS_ERROR,
                                     validators=[LazyEmail(lazy_message=c.EMAIL_ADDRESS_INVALID_ERROR)])]
    )

    phone = TelField(
        validators=[StrictRequiredIf('contact_options', 'PHONE', message=c.NO_PHONE_NUMBER_ERROR,
                                     validators=[validate_phone_number])]
    )


class DateRangeForm(Form):

    """
    Can't use StrictIfRequired on this form as it is used as a subform therefore get errors when validating.
    Validation needs to be checked in the controller after Flask validation on submit and errors dynamically
     added to form errors.
    """

    from_date_day = StringField()

    from_date_month = StringField()

    from_date_year = StringField()

    to_date_day = StringField()

    to_date_month = StringField()

    to_date_year = StringField()


class ContactDatesForm(FlaskForm):
    contactDatesCheck = LazyRadioField(
        lazy_choices=[
            (ContactDatesAvoid.SINGLE_DATE.name, c.SINGLE_DATE),
            (ContactDatesAvoid.DATE_RANGE.name, c.DATE_RANGE),
            (ContactDatesAvoid.NO_DATES.name, c.NO_DATES)
        ],
        validators=[LazyDataRequired(lazy_message=c.NO_CONTACT_DATES_OPTION_ERROR)]
    )

    day = StringField(
        validators=[
            StrictRequiredIf('contactDatesCheck', 'SINGLE_DATE', message=c.ENTER_DAY_ERROR, validators=[
                    LazyInteger(min_=1, max_=31, lazy_message=c.ENTER_VALID_DAY_ERROR)
            ])
        ]
    )

    month = StringField(
        validators=[
            StrictRequiredIf('contactDatesCheck', 'SINGLE_DATE', message=c.ENTER_MONTH_ERROR, validators=[
                LazyInteger(min_=1, max_=12, lazy_message=c.ENTER_VALID_MONTH_ERROR)
            ])
        ]
    )

    year = StringField(
        validators=[
            StrictRequiredIf('contactDatesCheck', 'SINGLE_DATE', message=c.ENTER_YEAR_ERROR, validators=[
                LazyInteger(min_=1000, lazy_message=c.ENTER_VALID_YEAR_ERROR, validators=[
                    validate_single_date
                ])
            ])
        ]
    )

    date_ranges = FieldList(FormField(DateRangeForm))

    add_date_range_button_clicked = SubmitField()

    remove_date_range_button_clicked = SubmitField()


class HmrcForm(FlaskForm):
    tell_hmrc = LazyRadioField(
        lazy_choices=[
            (True, c.YES),
            (False, c.NO)
        ],
        validators=[LazyDataRequired(lazy_message=c.NO_HMRC_OPTION_ERROR)]
    )

    national_insurance_number = StringField(
        validators=[StrictRequiredIf('tell_hmrc', True, message=c.ENTER_NI_NUMBER_ERROR,
                                     validators=[validate_national_insurance_number])]
    )


class CheckYourAnswers(FlaskForm):
    # There are no fields on the CheckYourAnswers form
    # But, to avoid a compiler error, we need to write 'pass' here
    pass
