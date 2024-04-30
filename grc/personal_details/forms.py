from flask_wtf import FlaskForm
from .constants import PersonalDetailsConstants as c
from grc.business_logic.data_structures.personal_details_data import AffirmedGender, ContactDatesAvoid
from grc.lazy.lazy_fields import LazyRadioField
from grc.lazy.lazy_form_custom_validators import LazyDataRequired
from grc.utils.form_custom_validators import StrictRequiredIf, validate_national_insurance_number, validate_address_field, validate_postcode, validate_date_of_transition, validate_phone_number, validate_statutory_declaration_date, validate_single_date, Integer
from wtforms import EmailField, StringField, RadioField, TelField, SelectField, SelectMultipleField, FieldList, FormField, SubmitField
from wtforms.form import Form
from wtforms.validators import DataRequired, Email


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
            DataRequired(message='Enter a month'),
            Integer(min=1, max=12, message='Enter a month as a number between 1 and 12')
        ]
    )

    transition_date_year = StringField(
        validators=[
            DataRequired(message='Enter a year'),
            Integer(min=1000, message='Enter a year as a 4-digit number, like 2000', validators=[validate_date_of_transition])
        ]
    )


class StatutoryDeclarationDateForm(FlaskForm):
    statutory_declaration_date_day = StringField(
        validators=[
            DataRequired(message='Enter a day'),
            Integer(min=1, max=31, message='Enter a day as a number between 1 and 31')
        ]
    )

    statutory_declaration_date_month = StringField(
        validators=[
            DataRequired(message='Enter a month'),
            Integer(min=1, max=12, message='Enter a month as a number between 1 and 12')
        ]
    )

    statutory_declaration_date_year = StringField(
        validators=[
            DataRequired(message='Enter a year'),
            Integer(min=1000, message='Enter a year as a 4-digit number, like 2000',
                    validators=[validate_statutory_declaration_date])
        ]
    )


class PreviousNamesCheck(FlaskForm):
    previousNameCheck = RadioField(
        choices=[
            (True, 'Yes'),
            (False, 'No')
        ],
        validators=[DataRequired(message='Select if you have ever changed your name to reflect your gender')]
    )


class AddressForm(FlaskForm):
    address_line_one = StringField(
        validators=[DataRequired(message='Enter your address'), validate_address_field]
    )

    address_line_two = StringField(validators=[validate_address_field])

    town = StringField(
        validators=[DataRequired(message='Enter your town or city'), validate_address_field]
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
        validators=[StrictRequiredIf('country', ['', 'United Kingdom'], message='Enter your postcode',
                                     validators=[validate_postcode])]
    )


class ContactPreferencesForm(FlaskForm):
    contact_options = SelectMultipleField(
        choices=[
            ('EMAIL', 'Email'),
            ('PHONE', 'Phone call'),
            ('POST', 'Post')
        ],
        validators=[DataRequired(message='Select how would you like to be contacted')]
    )

    email = EmailField(
        validators=[StrictRequiredIf('contact_options', 'EMAIL', message='Enter your email address',
                                     validators=[Email('Enter a valid email address')])]
    )

    phone = TelField(
        validators=[StrictRequiredIf('contact_options', 'PHONE', message='Enter your phone number',
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
    contactDatesCheck = RadioField(
        choices=[
            (ContactDatesAvoid.SINGLE_DATE.name, 'A single date'),
            (ContactDatesAvoid.DATE_RANGE.name, 'A range of dates'),
            (ContactDatesAvoid.NO_DATES.name, 'No dates')
        ],
        validators=[DataRequired(message="Select if you don't want us to contact you at any point in the next 6 months")]
    )

    day = StringField(
        validators=[
            StrictRequiredIf('contactDatesCheck', 'SINGLE_DATE', message='Enter a day', validators=[
                Integer(min=1, max=31, message='Enter a day as a number between 1 and 31')
            ]),
        ]
    )

    month = StringField(
        validators=[
            StrictRequiredIf('contactDatesCheck', 'SINGLE_DATE', message='Enter a month', validators=[
                Integer(min=1, max=12, message='Enter a month as a number between 1 and 12')
            ])
        ]
    )

    year = StringField(
        validators=[
            StrictRequiredIf('contactDatesCheck', 'SINGLE_DATE', message='Enter a year', validators=[
                Integer(min=1000, message='Enter a year as a 4-digit number, like 2000', validators=[
                    validate_single_date
                ])
            ])
        ]
    )

    date_ranges = FieldList(FormField(DateRangeForm))

    add_date_range_button_clicked = SubmitField()

    remove_date_range_button_clicked = SubmitField()


class HmrcForm(FlaskForm):
    tell_hmrc = RadioField(
        choices=[
            (True, 'Yes'),
            (False, 'No')
        ],
        validators=[DataRequired(message='Select if you would like us to tell HMRC after you receive a Gender Recognition Certificate')]
    )

    national_insurance_number = StringField(
        validators=[StrictRequiredIf('tell_hmrc', True, message='Enter your National Insurance number', validators=[validate_national_insurance_number])]
    )


class CheckYourAnswers(FlaskForm):
    # There are no fields on the CheckYourAnswers form
    # But, to avoid a compiler error, we need to write 'pass' here
    pass
