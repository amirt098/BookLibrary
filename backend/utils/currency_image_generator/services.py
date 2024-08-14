import logging
from typing import Dict

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFile import ImageFile

import arabic_reshaper
from utils.date_time import interfaces as date_time_interfaces
from utils.number_formatter import interfaces as number_formatter_interfaces
from . import interfaces

from io import BytesIO

logger = logging.getLogger(__name__)


class CurrencyImageGeneratorService(interfaces.AbstractImageGenerator):
    def __init__(
            self,
            english_font_path: str,
            farsi_font_path: str,
            country_mappings: Dict[str, str],  # example : {"USD": "us"}
            date_time_utils: date_time_interfaces.AbstractDateTimeUtils,
            number_formatter: number_formatter_interfaces.AbstractNumberFormatter,
            image_width: int = 800,
            cell_width: int = 200,
            cell_height: int = 50,
            n_cols: int = 4,
    ):
        self.image_width = image_width
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.n_cols = n_cols
        self.font_path = english_font_path
        self.english_font_path = english_font_path
        self.farsi_font_path = farsi_font_path
        self.country_mappings = country_mappings
        self.date_time_utils = date_time_utils
        self.number_formatter = number_formatter

    def draw_rows_in_picture(self, data_rows: interfaces.CurrencyRowList):
        n_rows = len(data_rows.rows)
        image_height = (n_rows + 2) * 50
        date = self.date_time_utils.convert_timestamp_to_date_time(
            timestamp=data_rows.timestamp,
            calendar_type=date_time_interfaces.CalendarType.JALALI,
        )
        date = f'{date.year}/{date.month}/{date.day}   {date.hour}:{date.minute}'
        image = Image.new("RGB", (self.image_width, image_height), "white")
        draw = ImageDraw.Draw(image)

        try:
            english_font = ImageFont.truetype(self.english_font_path, 15)
            farsi_font = ImageFont.truetype(self.farsi_font_path, 15)
        except IOError:
            english_font = farsi_font = ImageFont.load_default()

        # Define colors
        header_bg_color = (200, 200, 200)
        row_bg_color_1 = (240, 240, 240)
        row_bg_color_2 = (255, 255, 255)
        border_color = (255, 255, 255)
        text_color = (50, 50, 50)

        headers = ["وضعیت", "مانده حساب", "نام ارز", "*"]
        headers = [arabic_reshaper.reshape(header) for header in headers]

        draw.rectangle([0, 0, self.image_width / 2, self.cell_height], fill=header_bg_color)
        draw.rectangle([self.image_width / 2, 0, self.image_width, self.cell_height], fill=header_bg_color)
        bbox_name = draw.textbbox((0, 0), data_rows.name, font=english_font)
        bbox_date = draw.textbbox((0, 0), date, font=english_font)
        text_width_name, text_height_name = bbox_name[2] - bbox_name[0], bbox_name[3] - bbox_name[1]
        text_width_date, text_height_date = bbox_date[2] - bbox_date[0], bbox_date[3] - bbox_date[1]
        text_x_name = (self.image_width / 2 - text_width_name) / 2
        text_y_name = (self.cell_height - text_height_name) / 2
        text_x_date = (self.image_width / 2 - text_width_date) / 2 + self.image_width / 2
        text_y_date = (self.cell_height - text_height_date) / 2
        draw.text((text_x_name, text_y_name), data_rows.name, fill=text_color, font=english_font)
        draw.text((text_x_date, text_y_date), date, fill=text_color, font=english_font)

        # Draw table headers
        for col in range(self.n_cols):
            x1 = col * self.cell_width
            y1 = self.cell_height
            x2 = (col + 1) * self.cell_width
            y2 = 2 * self.cell_height
            draw.rectangle([x1, y1, x2, y2], fill=header_bg_color, outline=border_color)
            header_text = headers[col]
            bbox = draw.textbbox((0, 0), header_text, font=farsi_font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            text_x = x1 + (self.cell_width - text_width) / 2
            text_y = y1 + (self.cell_height - text_height) / 2
            draw.text((text_x, text_y), header_text, fill=text_color, font=farsi_font)

        # Draw table rows
        for row in range(1, n_rows + 1):
            bg_color = row_bg_color_1 if row % 2 == 1 else row_bg_color_2
            for col in range(self.n_cols):
                x1 = col * self.cell_width
                y1 = (row + 1) * self.cell_height
                x2 = (col + 1) * self.cell_width
                y2 = (row + 2) * self.cell_height
                draw.rectangle([x1, y1, x2, y2], fill=bg_color, outline=border_color)

                if col == 3:  # Last column, draw the flag
                    icon_file = self._find_icon_file(data_rows.rows[row - 1].currency_symbol)
                    icon_size = (int(self.cell_width * 0.3), int(self.cell_height * 0.6))
                    icon_file = icon_file.resize(icon_size, Image.LANCZOS)
                    icon_x = x1 + (self.cell_width - icon_size[0]) // 2
                    icon_y = y1 + (self.cell_height - icon_size[1]) // 2
                    image.paste(icon_file, (icon_x, icon_y), icon_file.convert('RGBA'))
                elif col == 2:
                    cell_text = f"{data_rows.rows[row - 1].currency_symbol}"
                    bbox = draw.textbbox((0, 0), cell_text, font=english_font)
                    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    text_x = x1 + (self.cell_width - text_width) / 2
                    text_y = y1 + (self.cell_height - text_height) / 2
                    draw.text((text_x, text_y), cell_text, fill=text_color, font=english_font)
                elif col == 1:
                    cell_text = f"{self.number_formatter.format_decimal(data_rows.rows[row - 1].balance)}"
                    bbox = draw.textbbox((0, 0), cell_text, font=english_font)
                    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    text_x = x1 + (self.cell_width - text_width) / 2
                    text_y = y1 + (self.cell_height - text_height) / 2
                    draw.text((text_x, text_y), cell_text, fill=text_color, font=english_font)
                elif col == 0:
                    cell_text = f"{data_rows.rows[row - 1].status}"
                    bbox = draw.textbbox((0, 0), cell_text, font=english_font)
                    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    text_x = x1 + (self.cell_width - text_width) / 2
                    text_y = y1 + (self.cell_height - text_height) / 2
                    draw.text((text_x, text_y), cell_text, fill=text_color, font=english_font)


        buffer = BytesIO()
        image.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        buffer.close()

        return image_bytes

    def _find_icon_file(self, currency_code: str) -> ImageFile:
        if '_' in currency_code:
            currency_code = currency_code.split('_')[0]
        file = self.country_mappings.get(currency_code) or self.country_mappings["default"]
        filename = './png250px/' + file + '.png'

        icon = Image.open(filename)

        return icon
