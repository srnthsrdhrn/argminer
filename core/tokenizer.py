from typing import List
from abc import ABC, abstractmethod
from langdetect import detect

from core.exceptions import NotSupportedException


class Tokenizer(ABC):
    def __init__(self, languages_supported='en'):
        self.languages_supported = languages_supported

    @abstractmethod
    def tokenize(self, text: str) -> List[str]:
        """
        Abstract method which tokenizes a given string. This has been left empty on purpose. Needs to be implemented by
        child class
        :param text: String to tokenize
        :return: List of tokens
        """
        pass

    def _is_language_supported(self, text: str) -> bool:
        """
        Utility function to determine whether the text is in a supported language.
        Will raise a NotSupportedException if language is not supported/
        :param text: text to analyse
        :return: True if it is supported. Will raise error if not supported.
        """
        language = self._detect_language(text)
        if language in self.languages_supported:
            return True
        else:
            raise NotSupportedException(f"The text is in a language that is not supported. Identified Language: {language}")

    def _detect_language(self, text):
        """
        Utility function to detect language
        :param text: text to detect language
        :return: language_code
        """
        return detect(text=text)
