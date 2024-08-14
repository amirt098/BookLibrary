import os
from unittest import TestCase
from . import interfaces
from lib import data_classes as lib_dataclasses
from .services import FileValidator


class FileValidatorTestCase(TestCase):
    def setUp(self) -> None:
        self.service = FileValidator()

    def test_bad_max_file_count(self):
        self.service.set_max_file_count(value=1)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        files = []
        with open(f'{current_dir}/data/test.test.png', 'rb') as file:
            files.append(lib_dataclasses.File(
                buffer=file.read(),
                name=file.name.split('/')[-1]

            ))
        with open(f'{current_dir}/data/test_test.pdf', 'rb') as file:
            files.append(lib_dataclasses.File(
                buffer=file.read(),
                name=file.name.split('/')[-1]

            ))
        with self.assertRaises(interfaces.FileCountLimitExceededException):
            self.service.validate_files(files=files)

    def test_happy_max_file_count(self):
        self.service.set_max_file_count(value=1)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        files = []
        with open(f'{current_dir}/data/test.test.png', 'rb') as file:
            files.append(lib_dataclasses.File(
                buffer=file.read(),
                name=file.name.split('/')[-1]

            ))
        self.service.validate_files(files=files)

    def test_bad_max_file_name(self):
        self.service.set_max_file_name_length(value=2)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        files = []
        with open(f'{current_dir}/data/test.test.png', 'rb') as file:
            files.append(lib_dataclasses.File(
                buffer=file.read(),
                name=file.name.split('/')[-1]

            ))
        with self.assertRaises(interfaces.FileNameLengthExceededException):
            self.service.validate_files(files=files)

    def test_happy_max_file_name(self):
        self.service.set_max_file_name_length(value=16)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        files = []
        with open(f'{current_dir}/data/test.test.png', 'rb') as file:
            files.append(lib_dataclasses.File(
                buffer=file.read(),
                name=file.name.split('/')[-1]

            ))
        self.service.validate_files(files=files)

    def test_max_each_file_size_in_bytes(self):
        self.service.set_max_each_file_size_in_bytes(100)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        files = []
        with open(f'{current_dir}/data/test.test.png', 'rb') as file:
            files.append(lib_dataclasses.File(
                buffer=file.read(),
                name=file.name.split('/')[-1]

            ))
        with self.assertRaises(interfaces.FileSizeLimitExceededException):
            self.service.validate_files(files=files)

    def test_happy_max_each_file_size_in_bytes(self):
        self.service.set_max_each_file_size_in_bytes(1024 * 1024)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        files = []
        with open(f'{current_dir}/data/test.test.png', 'rb') as file:
            files.append(lib_dataclasses.File(
                buffer=file.read(),
                name=file.name.split('/')[-1]

            ))
        self.service.validate_files(files=files)

    def test_allowed_special_characters_in_file_name(self):
        self.service.set_allowed_special_characters_in_file_name(
            [interfaces.SpecialCharacter.UNDERSCORE.value]
        )
        current_dir = os.path.dirname(os.path.abspath(__file__))
        files = []
        with open(f'{current_dir}/data/test.test.png', 'rb') as file:
            files.append(lib_dataclasses.File(
                buffer=file.read(),
                name=file.name.split('/')[-1]

            ))
        with self.assertRaises(interfaces.InvalidFileNameException):
            self.service.validate_files(files=files)

    def test_happy_allowed_special_characters_in_file_name(self):
        self.service.set_allowed_special_characters_in_file_name(
            [interfaces.SpecialCharacter.DOT.value]
        )
        current_dir = os.path.dirname(os.path.abspath(__file__))
        files = []
        with open(f'{current_dir}/data/test.test.png', 'rb') as file:
            files.append(lib_dataclasses.File(
                buffer=file.read(),
                name=file.name.split('/')[-1]

            ))
        self.service.validate_files(files=files)

    def test_max_total_size_in_bytes(self):
        self.service.set_max_total_size_in_bytes(100)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        files = []
        with open(f'{current_dir}/data/test.test.png', 'rb') as file:
            files.append(lib_dataclasses.File(
                buffer=file.read(),
                name=file.name.split('/')[-1]

            ))
        with open(f'{current_dir}/data/test_test.pdf', 'rb') as file:
            files.append(lib_dataclasses.File(
                buffer=file.read(),
                name=file.name.split('/')[-1]

            ))
        with self.assertRaises(interfaces.TotalSizeLimitExceededException):
            self.service.validate_files(files=files)

    def test_happy_max_total_size_in_bytes(self):
        self.service.set_max_total_size_in_bytes(1024 * 1024)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        files = []
        with open(f'{current_dir}/data/test.test.png', 'rb') as file:
            files.append(lib_dataclasses.File(
                buffer=file.read(),
                name=file.name.split('/')[-1]

            ))
        with open(f'{current_dir}/data/test_test.pdf', 'rb') as file:
            files.append(lib_dataclasses.File(
                buffer=file.read(),
                name=file.name.split('/')[-1]

            ))
        self.service.validate_files(files=files)

    def test_acceptable_file_types1(self):
        self.service.set_acceptable_file_types([interfaces.FileType.PDF.value])
        current_dir = os.path.dirname(os.path.abspath(__file__))
        files = []
        with open(f'{current_dir}/data/test.test.png', 'rb') as file:
            files.append(lib_dataclasses.File(
                buffer=file.read(),
                name=file.name.split('/')[-1]

            ))
        with self.assertRaises(interfaces.UnacceptableFileTypeException):
            self.service.validate_files(files=files)

    def test_acceptable_file_types2(self):
        self.service.set_acceptable_file_types([interfaces.FileType.PDF.value])
        current_dir = os.path.dirname(os.path.abspath(__file__))
        files = []
        with open(f'{current_dir}/data/test_fake.pdf', 'rb') as file:
            files.append(lib_dataclasses.File(
                buffer=file.read(),
                name=file.name.split('/')[-1]

            ))
        with self.assertRaises(interfaces.UnacceptableFileTypeException):
            self.service.validate_files(files=files)

    def test_happy_acceptable_file_types(self):
        self.service.set_acceptable_file_types([interfaces.FileType.IMAGE.value])
        current_dir = os.path.dirname(os.path.abspath(__file__))
        files = []
        with open(f'{current_dir}/data/test.test.png', 'rb') as file:
            files.append(lib_dataclasses.File(
                buffer=file.read(),
                name=file.name.split('/')[-1]

            ))
        self.service.validate_files(files=files)

