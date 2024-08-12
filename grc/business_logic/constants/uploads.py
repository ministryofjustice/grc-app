from flask_babel import lazy_gettext as _l


class UploadsConstants:

    UPLOAD_FILE = _l('Upload file')
    SAVE_AND_CONTINUE = _l('Save and continue')

    # Errors
    UPLOAD_OR_SAVE_ERROR = _l("Click on either the 'Upload file' button or 'Save and continue' button")
    FILE_TYPE_PUBLIC_ERROR = _l('Select a JPG, BMP, PNG, TIF or PDF file smaller than 10MB')
