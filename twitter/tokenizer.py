import re
from typing import List

import contextualSpellCheck
import spacy
from spacy.tokenizer import Tokenizer as spacyTokenizer
from ttp import ttp


class TwitterTokenizer:
    """
    This class will remove emojis, twitter mentions, and stop words.
    In addition to that it will tokenize the text.
    """

    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        contextualSpellCheck.add_to_pipe(self.nlp)
        self.tokenizer = spacyTokenizer(self.nlp.vocab)

    def _preprocess_text(self, text):
        p = ttp.Parser()
        result = p.parse(text)
        removed_html = re.sub('<[^>]*>', '', result.html)
        removed_hashtags = re.sub('(#|\$|@)[^ ]*', '', removed_html)
        trimmed_sentence = removed_hashtags.replace("\n", " ").replace("  ", " ").strip()
        # spelling_corrected = TextBlob(trimmed_sentence).tokens
        doc = self.nlp(trimmed_sentence)
        return doc._.outcome_spellCheck

    def tokenize(self, text: str) -> List[str]:
        """
        Function to tokenize Twitter messages.
        :param text: The text to tokenize
        :return:list of strings called tokens
        """

        processed_text = self._preprocess_text(text)
        tokens = self.tokenizer(processed_text)
        return tokens
