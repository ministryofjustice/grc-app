from playwright.async_api import Page

class AdminHelpers:
    def __init__(self, page: Page):
        self.page = page

    async def get_top_rows(self, number_of_rows: int):
        """
        Extracts top three rows from table
        """
        rows = await self.page.locator("table tbody tr").all()
        assert len(rows) >= number_of_rows, f"Expected at least {number_of_rows} rows, but found {len(rows)}"
        return [rows[i] for i in range(number_of_rows) ]

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

def unformatted_reference_number(reference_number: str) -> str:
    return "".join(reference_number.split("-"))