import abc
import enum
from typing import List, IO
from lib import data_classes as lib_dataclasses


class FileType(str, enum.Enum):
    IMAGE = 'image'
    PDF = 'pdf'


class SpecialCharacter(str, enum.Enum):
    DOT = 'dot'
    DASH = 'dash'
    UNDERSCORE = 'underscore'


class BadConfiguration(Exception):
    pass


class InvalidFiles(Exception):
    pass


class FileSizeLimitExceededException(InvalidFiles):
    def __init__(self, limit: int):
        super().__init__(f'At least one of files is bigger than {limit} bytes.')


class TotalSizeLimitExceededException(InvalidFiles):
    def __init__(self, limit: int):
        super().__init__(f'Sum of file sizes is bigger than {limit} bytes.')


class FileNameLengthExceededException(InvalidFiles):
    def __init__(self, limit: int):
        super().__init__(f'At least one of files has a name with length more than {limit} characters.')


class FileCountLimitExceededException(InvalidFiles):
    def __init__(self, limit: int):
        super().__init__(f'Number of files is more than {limit}.')


class UnacceptableFileTypeException(InvalidFiles):
    def __init__(self, allowed_types: List[FileType]):
        super().__init__(f'Only {", ".join([str(i) for i in allowed_types])} files can be accepted by now.')


class InvalidFileNameException(InvalidFiles):
    def __init__(self, allowed_characters: List[SpecialCharacter]):
        super().__init__(
            f'File name only can have alphanumeric characters plus {", ".join([str(i) for i in allowed_characters])}.')


class AbstractFileValidator(abc.ABC):
    def __init__(self):
        self.max_each_file_size_in_bytes: int | None = None
        self.max_total_size_in_bytes: int | None = None
        self.max_file_count: int | None = None
        self.max_file_name_length: int | None = None
        self.acceptable_file_types: List[FileType] | None = None
        self.allowed_special_characters_in_file_name: List[SpecialCharacter] | None = None

    def set_max_each_file_size_in_bytes(self, value: int | None):
        # TODO: validate value and raise BadConfiguration if needed
        self.max_each_file_size_in_bytes = value
        return self

    def set_max_total_size_in_bytes(self, value: int | None):
        # TODO: validate value and raise BadConfiguration if needed
        self.max_total_size_in_bytes = value
        return self

    def set_max_file_count(self, value: int | None):
        # TODO: validate value and raise BadConfiguration if needed
        self.max_file_count = value
        return self

    def set_max_file_name_length(self, value: int | None):
        # TODO: validate value and raise BadConfiguration if needed
        self.max_file_name_length = value
        return self

    def set_acceptable_file_types(self, value: List[FileType] | None):
        # TODO: validate value and raise BadConfiguration if needed
        self.acceptable_file_types = value
        return self

    def set_allowed_special_characters_in_file_name(self, value: List[SpecialCharacter] | None):
        # TODO: validate value and raise BadConfiguration if needed
        self.allowed_special_characters_in_file_name = value

    @abc.abstractmethod
    def validate_files(self, files: List[lib_dataclasses.File]):
        """validates files against all rules.
        If a rule configuration is None, the whole rule will not be applied.

        Args:
            files (List[File]): files to be validates

        Raises:
            FileSizeLimitExceededException: in case max_each_file_size_in_bytes is not None and at least one file size exceeds it.
            TotalSizeLimitExceededException: in case max_total_size_in_bytes is not None and sum of file sizes exceeds it.
            FileCountLimitExceededException: in case max_file_count is not None and files count exceeds it.
            FileNameLengthExceededException: in case max_file_name_length is not None and at least one file name length exceeds it.
            UnacceptableFileTypeException: in case acceptable_file_types is not None and at least one of file types is not within it.
            InvalidFileNameException: in case allowed_special_characters_in_file_name is not None and at least one file name contains a non-alphanumeric character that is not within it.

        """
        raise NotImplementedError
