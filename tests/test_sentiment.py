from esc_chatbot.nlp.sentiment import analyze_sentiment


class TestSentiment:
    def test_positive(self) -> None:
        result = analyze_sentiment("ótimo excelente adorei")
        assert result["label"] == "positive"
        assert result["score"] > 0.5

    def test_negative(self) -> None:
        result = analyze_sentiment("ruim péssimo horrível detesto")
        assert result["label"] == "negative"
        assert result["score"] < 0.5

    def test_neutral(self) -> None:
        result = analyze_sentiment("olá tudo bem")
        assert result["label"] == "neutral"
        assert result["score"] == 0.5
