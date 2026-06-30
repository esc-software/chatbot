from esc_chatbot.core.storage import MemoryBackend as ConversationMemory


class TestConversationMemory:
    def test_append_and_get(self) -> None:
        mem = ConversationMemory()
        mem.append("user1", {"text": "oi", "intent": "saudacao"})
        entries = mem.get("user1")
        assert len(entries) == 1
        assert entries[0]["text"] == "oi"

    def test_maxlen(self) -> None:
        mem = ConversationMemory()
        for i in range(20):
            mem.append("user1", {"text": f"msg{i}"})
        assert len(mem.get("user1")) == mem.maxlen

    def test_unknown_user_returns_empty(self) -> None:
        mem = ConversationMemory()
        assert mem.get("nonexistent") == []
