from flask_wtf import FlaskForm


def remove_date_ranges(form: FlaskForm):
    for _ in range(len(form.date_ranges)):
        form.date_ranges.pop_entry()
