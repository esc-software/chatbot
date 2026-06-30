from esc_chatbot.config import settings
from esc_chatbot.nlp.lang_detect import detect_lang
from esc_chatbot.nlp.preprocess import clean
from esc_chatbot.nlp.spell import correct


class TestClean:
    def test_basic_clean(self) -> None:
        assert clean("Olá, Mundo!!!") == "olá mundo"

    def test_blacklist_removed(self) -> None:
        assert "drop table" not in clean("drop table users")

    def test_repeated_chars(self) -> None:
        assert clean("aaaaaaa") == ""

    def test_max_length(self) -> None:
        long_text = "a" * 400
        assert len(clean(long_text)) <= 300

    def test_special_chars_removed(self) -> None:
        assert clean("teste@#$%") == "teste"


class TestDetectLang:
    def test_english_detected(self) -> None:
        assert detect_lang("Hello how are you") == "en"
        assert detect_lang("What is this") == "en"

    def test_portuguese_detected(self) -> None:
        assert detect_lang("olá tudo bem") == "pt"
        assert detect_lang("como vai você") == "pt"


class TestSpellCorrection:
    def test_common_abbreviations(self) -> None:
        assert "você" in correct("vc")
        assert "tudo" in correct("td")
        assert "também" in correct("tb")
        assert "porque" in correct("pq")
