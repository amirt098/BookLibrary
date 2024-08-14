import re
from os.path import splitext
from typing import List
import magic
from . import interfaces
from lib import data_classes as lib_dataclasses

PATTERN = r"[^a-zA-Z0-9\s\u0600-\u06FF\u0660-\u0669]"

mime_type_map = {
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'odt': 'application/vnd.oasis.opendocument.text',
    'pdf': 'application/pdf',
    'ppt': 'application/vnd.ms-powerpoint',
    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'xls': 'application/vnd.ms-excel',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'txt': 'text/plain',
    'pem': 'text/plain',
    'crt': 'text/plain',
    'cert': 'text/plain',
    'cer': 'text/plain',
    'csr': 'text/plain',
    'req': 'text/plain',
}
MIME_TYPE = {
    "image": ['image/jpeg', 'image/png'],
    "pdf": ['application/pdf']
}
EXTENSION = {
    "image": ["jpg", "jpeg", "png"],
    "pdf": ["pdf"]
}

SPECIAL_CHARACTER = {
    "dot": '.',
    "dash": '-',
    "underscore": '_'
}


class FileValidator(interfaces.AbstractFileValidator):
    def validate_files(self, files: List[lib_dataclasses.File]):
        if self.max_file_count and len(files) > self.max_file_count:
            raise interfaces.FileCountLimitExceededException(limit=self.max_file_count)

        if self.max_file_name_length and any(len(file.name) > self.max_file_name_length for file in files):
            raise interfaces.FileNameLengthExceededException(limit=self.max_file_name_length)

        if self.max_each_file_size_in_bytes and any(
                len(file.buffer) > self.max_each_file_size_in_bytes for file in files):
            raise interfaces.FileSizeLimitExceededException(limit=self.max_each_file_size_in_bytes)

        if self.allowed_special_characters_in_file_name and any(
                not set(re.findall(PATTERN, splitext(file.name)[0])).issubset(
                    self._allowed_special_characters_in_file_name) for file in files):
            raise interfaces.InvalidFileNameException(allowed_characters=self.allowed_special_characters_in_file_name)

        if self.max_total_size_in_bytes and sum(len(file.buffer) for file in files) > self.max_total_size_in_bytes:
            raise interfaces.TotalSizeLimitExceededException(limit=self.max_total_size_in_bytes)

        if self.acceptable_file_types and any(not self._is_extension_and_mime_type_valid(file) for file in files):
            raise interfaces.UnacceptableFileTypeException(allowed_types=self.acceptable_file_types)

    @property
    def _allowed_special_characters_in_file_name(self) -> List[str]:
        special_characters = []
        for character in self.allowed_special_characters_in_file_name:
            special_characters.append(SPECIAL_CHARACTER[character])
        return special_characters

    def _is_extension_and_mime_type_valid(self, file: lib_dataclasses.File) -> bool:
        extensions = []
        mime_types = []
        for acceptable_file_type in self.acceptable_file_types:
            extensions.extend(EXTENSION[acceptable_file_type])
            mime_types.extend(MIME_TYPE[acceptable_file_type])
        extension = file.name.split('.')[-1]
        if extension.lower() not in extensions:
            return False
        if magic.from_buffer(file.buffer, mime=True) not in mime_types:
            return False
        return True
