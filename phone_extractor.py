"""
Задача: обработать текстовый файл и извлечь всё, что похоже на номера телефонов.
Содержимое файла может быть любым. Формат записи номера телефона тоже может быть произвольным.
Извлечь необходимо все уникальные номера телефонов в едином формате: +7(YYY)XXX-XX-XX - в порядке их появления.
Реализация класса обязательно на Python 3.11+ с использованием typing и re.
При необходимости использовать loguru, click, asyncio и six.
"""

from pathlib import Path
import re
from typing import Iterator, Optional, TextIO
from loguru import logger

from utils import detect_encoding

RU_PHONE_PATTERN = re.compile(
    r"""
    (?:\+?7|8)        # country code: +7, 7 or 8
    \D*?              # optional non-digits
    (\d{3})           # area code
    \D*?              # optional non-digits
    (\d{3})           # first 3 digits
    \D*?              # next 2 digits
    (\d{2})
    \D*?              # final 2 digits
    (\d{2})
    """,
    re.VERBOSE | re.MULTILINE,
)


class PhoneExtractor:
    @classmethod
    def _extract(
        cls, text_iter: Iterator[str], output_file: Optional[TextIO] = None
    ) -> list[str]:
        seen = set()
        offset = 0  # absolute character offset in file

        for line_num, line in enumerate(text_iter, start=1):
            for match in RU_PHONE_PATTERN.finditer(line):
                normalized = cls._normalize_phone_number(match)
                if normalized not in seen:
                    seen.add(normalized)

                    if output_file:
                        print(normalized, file=output_file)

                    start_pos = match.start()
                    col_num = start_pos + 1  # columns are usually 1-based
                    abs_pos = offset + start_pos

                    logger.debug(
                        f"Extracted: {normalized} (line {line_num}, col {col_num}, offset {abs_pos})"
                    )
            offset += len(line)

        return list(seen)

    @classmethod
    def from_string(cls, input: str) -> list[str]:
        return cls._extract(iter(input.splitlines()))

    @classmethod
    def from_file(
        cls,
        path: str | Path,
        output_path: Optional[str | Path] = None,
        encoding: Optional[str] = None,
    ) -> list[str]:
        # Guess encoding if not provided. Fallback to utf-8.
        if encoding is None:
            encoding = detect_encoding(path)

        with open(path, "r", encoding=encoding, errors="ignore") as f:
            if output_path:
                with open(output_path, "w", encoding="utf-8") as out:
                    return cls._extract(f, output_file=out)
            else:
                return cls._extract(f)

    @classmethod
    def _normalize_phone_number(cls, phone: re.Match) -> str:
        g = phone.groups()
        return f"+7({g[0]}){g[1]}-{g[2]}-{g[3]}"
