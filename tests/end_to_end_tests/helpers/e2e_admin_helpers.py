from playwright.async_api import Page


class AdminHelpers:
    """
    This class is used to create helper functions when end-to-end testing the GRC admin app
    """

    def __init__(self, page: Page):
        self.page = page

    async def get_top_rows(self, number_of_rows: int, table_name: str = ""):
        """
        Extracts top three rows from table
        """
        rows = await self.page.locator(f"table{table_name} tbody tr").all()
        assert len(rows) >= number_of_rows, f"Expected at least {number_of_rows} rows, but found {len(rows)}"
        return [rows[i] for i in range(number_of_rows)]

    async def get_row_reference_number(self, row):
        """
        Extracts reference number from a table row
        """
        if row is None:
            return None

        th_locator = row.locator("th.reference-number")

        if await th_locator.count() == 0:  # Edge case: No matching <th> found
            return None

        reference_number = await th_locator.inner_text()

        assert reference_number.strip(), "Reference number is empty"

        return unformatted_reference_number(reference_number.strip())

    async def get_ref_num_complete_tab(self, row):
        """
               Extracts reference number from a table row
               """
        if row is None:
            return None

        text_locator = row.locator("div.govuk-checkboxes__item > input")

        if await text_locator.count() == 0:  # Edge case: No matching id found
            return None

        reference_number_completed = await text_locator.get_attribute('id')

        print("reference_number_completed -", reference_number_completed)

        assert reference_number_completed.strip(), "Reference number is empty"

        return unformatted_reference_number(reference_number_completed.strip())


def unformatted_reference_number(reference_number: str) -> str:
    """
    Unformat a reference number from XXX-XXX to XXXXXX
    """
    return "".join(reference_number.split("-"))


async def get_nth_value_to_click(row):
    """
        clicks on the nth view application
        """
    if row is None:
        return None

    href_locator = row.locator("a.href")

    if await href_locator.count() == 0:  # Edge case: No matching <th> found
        return None

    await href_locator.click()
