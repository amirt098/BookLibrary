from django.test import TestCase
from runner.bootstrap import get_bootstrapper
from . import interfaces


class ImageGeneratorTestCase(TestCase):
    def setUp(self):
        self.service = get_bootstrapper().get_currency_image_generator()

    def test_generate_image(self):
        request = interfaces.CurrencyRowList(
            rows=[
                interfaces.CurrencyRow(
                    currency_symbol="USD",
                    balance=599,
                    status="status1",
                ),
                interfaces.CurrencyRow(
                    currency_symbol="IRR",
                    balance=111,
                    status="status2",
                ),
                interfaces.CurrencyRow(
                    currency_symbol="TRY",
                    balance=444,
                    status="status3",
                ),
                interfaces.CurrencyRow(
                    currency_symbol="RUB",
                    balance=444,
                    status="status4",
                ),
                interfaces.CurrencyRow(
                    currency_symbol="IQD",
                    balance=444,
                    status="status4",
                ),


            ],
            name="Delkhahi",
            timestamp=1720709075000,
        )
        image = self.service.draw_rows_in_picture(data_rows=request)
        # todo: assertions
