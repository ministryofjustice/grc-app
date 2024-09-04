import os
import pathlib
import pytest

@pytest.fixture()
def content_to_ignore():
    content_to_ignore_ = {
        'error-summary.html': [
            ('{{ _(\'There is a problem\') }}', 'There is a problem')
        ],
        'date.html': [
            ('{{ _(\'Day\') }}', 'Day'),
            ('{{ _(\'Month\') }}', 'Month'),
            ('{{ _(\'Year\') }}', 'Year'),
        ],
        'date-range.html': [
            ('{{ _(\'Day\') }}', 'Day'),
            ('{{ _(\'Month\') }}', 'Month'),
            ('{{ _(\'Year\') }}', 'Year'),
            ('_("From")', '"From"'),
            ('_("To")', '"To"'),
            ('"{{ _(\'Remove date range\') }}"', '"Remove date range"'),
            ('"{{ _(\'Add another date range\') }}"', '"Add another date range"')
        ],
        '_summary-list-item.html': [
            ('{{ _(\'Change\') }}', 'Change'),
        ],
    }
    return content_to_ignore_


def test_gov_uk_design_system_folders_in_sync_admin(content_to_ignore):
    """
    The /grc app and the /admin app both contain a templates sub-folder called /govuk-design-system-templates
    Check that these two files are in-sync
    """

    path_to_this_file = pathlib.Path(__file__).parent.absolute()
    path_to_grc_templates = os.path.join(path_to_this_file.parent, 'grc', 'templates', 'govuk-design-system-templates')
    path_to_admin_templates = os.path.join(path_to_this_file.parent, 'admin', 'templates', 'govuk-design-system-templates')

    grc_files = os.listdir(path_to_grc_templates)
    grc_files.sort()
    admin_files = os.listdir(path_to_admin_templates)
    admin_files.sort()

    assert grc_files == admin_files

    for filename in grc_files:
        grc_filename = os.path.join(path_to_grc_templates, filename)
        admin_filename = os.path.join(path_to_admin_templates, filename)

        grc_file = open(grc_filename, 'r')
        grc_file_text = grc_file.read()
        grc_file.close()

        admin_file = open(admin_filename, 'r')
        admin_file_text = admin_file.read()
        admin_file.close()

        print(f"Comparing GRC vs ADMIN govuk-design-system-templates file ({filename})")
        error_message = (f"Gov.UK Design System template files do not match between GRC and ADMIN folders."
                         f" Mis-matching file is ({filename})")
        if filename in content_to_ignore:
            if not files_are_same_with_content_to_ignore(grc_file_text, admin_file_text, content_to_ignore, filename):
                raise Exception(error_message)

        elif grc_file_text != admin_file_text:
            raise Exception(error_message)


def test_gov_uk_design_system_folders_in_sync_dashboard(content_to_ignore):
    """
    The /grc app and the /dashboard app both contain a templates sub-folder called /govuk-design-system-templates
    Check that these two files are in-sync
    """

    path_to_this_file = pathlib.Path(__file__).parent.absolute()
    path_to_grc_templates = os.path.join(path_to_this_file.parent, 'grc', 'templates', 'govuk-design-system-templates')
    path_to_dashboard_templates = os.path.join(path_to_this_file.parent, 'dashboard', 'templates', 'govuk-design-system-templates')

    grc_files = os.listdir(path_to_grc_templates)
    grc_files.sort()
    dashboard_files = os.listdir(path_to_dashboard_templates)
    dashboard_files.sort()

    assert grc_files == dashboard_files

    for filename in grc_files:
        grc_filename = os.path.join(path_to_grc_templates, filename)
        dashboard_filename = os.path.join(path_to_dashboard_templates, filename)

        grc_file = open(grc_filename, 'r')
        grc_file_text = grc_file.read()
        grc_file.close()

        dashboard_file = open(dashboard_filename, 'r')
        dashboard_file_text = dashboard_file.read()
        dashboard_file.close()

        print(f"Comparing GRC vs DASHBOARD govuk-design-system-templates file ({filename})")
        error_message = (f"Gov.UK Design System template files do not match between GRC and DASHBOARD folders."
                         f" Mis-matching file is ({filename})")

        if filename in content_to_ignore:
            if not files_are_same_with_content_to_ignore(grc_file_text, dashboard_file_text, content_to_ignore, filename):
                raise Exception(error_message)

        elif grc_file_text != dashboard_file_text:
            raise Exception(error_message)


def files_are_same_with_content_to_ignore(file_one: str, file_two: str, content_to_ignore: dict, filename):
    for i, content in enumerate(content_to_ignore[filename]):
        file_1_content, file_2_content = content
        if file_1_content in file_one and file_2_content in file_two:
            file_two = file_two.replace(file_2_content, file_1_content)
            content_to_ignore[filename].pop(i)

            if file_one != file_two and not content_to_ignore[filename]:
                print(f'GRC file has different content in {filename} which should not be ignored')
                return False

            if file_one != file_two:
                return files_are_same_with_content_to_ignore(file_one, file_two, content_to_ignore, filename)

            if file_one == file_two and not content_to_ignore[filename]:
                return True

    return False
