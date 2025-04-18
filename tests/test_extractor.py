import unittest
import unittest.mock
from phone_extractor import PhoneExtractor
from pathlib import Path


class TestPhoneExtractor(unittest.TestCase):
    # тесты тоже написаны чатгпт, он с этим хорошо справляется

    def test_normalize_phone_number(self):
        raw_number = ("+7", "926", "123", "45", "67")
        match = unittest.mock.MagicMock()
        match.groups.return_value = raw_number[1:]

        normalized_number = PhoneExtractor._normalize_phone_number(match)
        self.assertEqual(normalized_number, "+7(926)123-45-67")

    def test_extract_from_string(self):
        text = "мой номер 8 926 123-45-67 и ещё один номер 8 (927) 000 11 22"
        phones = PhoneExtractor.from_string(text)
        self.assertEqual(len(phones), 2)
        self.assertIn("+7(926)123-45-67", phones)
        self.assertIn("+7(927)000-11-22", phones)

    def test_extract_from_file(self):
        phones = PhoneExtractor.from_file(Path(__file__).parent / "testfile.txt")
        self.assertEqual(len(phones), 5)
        self.assertIn("+7(912)345-67-89", phones)
        self.assertIn("+7(495)123-45-67", phones)
        self.assertIn("+7(903)456-78-90", phones)
        self.assertIn("+7(900)123-45-67", phones)
        self.assertIn("+7(999)888-77-66", phones)
