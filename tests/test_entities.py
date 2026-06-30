from esc_chatbot.nlp.ner import extract_entities


class TestExtractEntities:
    def test_money_brl(self) -> None:
        result = extract_entities("custa r$ 150")
        assert "money" in result

    def test_numbers(self) -> None:
        result = extract_entities("são 42 unidades")
        assert "numbers" in result
        assert "42" in result["numbers"]

    def test_emails(self) -> None:
        result = extract_entities("meu email é teste@email.com")
        assert "emails" in result
        assert "teste@email.com" in result["emails"]

    def test_phones(self) -> None:
        result = extract_entities("me liga 11999998888")
        assert "phones" in result

    def test_no_entities(self) -> None:
        result = extract_entities("olá tudo bem")
        assert result == {} or all(len(v) == 0 for v in result.values())
