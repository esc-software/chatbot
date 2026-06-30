import json
import random
from collections import defaultdict
from pathlib import Path

import faiss
import numpy as np
from gensim.models import Word2Vec

from ..config import settings
from .intents import INTENTS
from .preprocess import clean


class NLPAttention:
    def __init__(self) -> None:
        self.vector_size = settings.vector_size
        self.corpus: list[list[str]] = []
        self.labels: list[str] = []
        self.tags: list[str] = []
        self.tag_to_idx: dict[str, int] = {}
        self.idx_to_tag: dict[int, str] = {}
        self.w2v: Word2Vec | None = None
        self.index: faiss.Index | None = None
        self.meta: list[str] = []
        self._last_responses: dict[str, str] = {}
        self._pattern_map: dict[str, str] = {}

        self._build_pattern_map()
        self._build_or_load()

    def _build_corpus(self) -> None:
        for intent in INTENTS["intents"]:
            for p in intent["patterns"]:
                self.corpus.append(clean(p).split())
                self.labels.append(intent["tag"])
            for p in intent.get("patterns_en", []):
                self.corpus.append(clean(p).split())
                self.labels.append(intent["tag"])
        self.tags = sorted(set(self.labels))
        self.tag_to_idx = {t: i for i, t in enumerate(self.tags)}
        self.idx_to_tag = {i: t for t, i in self.tag_to_idx.items()}

    def _build_pattern_map(self) -> None:
        for intent in INTENTS["intents"]:
            for p in intent["patterns"] + intent.get("patterns_en", []):
                key = clean(p)
                if key:
                    self._pattern_map[key] = intent["tag"]

    def _build_or_load(self) -> None:
        w2v_path = Path(settings.w2v_path)
        faiss_path = Path(settings.faiss_path)
        meta_path = Path(settings.meta_path)

        if w2v_path.exists() and faiss_path.exists() and meta_path.exists():
            try:
                self.w2v = Word2Vec.load(str(w2v_path))
                self.index = faiss.read_index(str(faiss_path))
                with open(str(meta_path)) as f:
                    self.meta = json.load(f)
                return
            except Exception:
                pass

        self._build_corpus()
        self._train()

    def _train(self) -> None:
        self.w2v = Word2Vec(
            sentences=self.corpus,
            vector_size=self.vector_size,
            window=3,
            min_count=1,
            workers=2,
        )
        vectors: list[np.ndarray] = []
        self.meta = []
        for intent in INTENTS["intents"]:
            for p in intent["patterns"]:
                vectors.append(self._embed(p))
                self.meta.append(intent["tag"])
            for p in intent.get("patterns_en", []):
                vectors.append(self._embed(p))
                self.meta.append(intent["tag"])
        arr = np.array(vectors).astype("float32")
        self.index = faiss.IndexFlatL2(self.vector_size)
        self.index.add(arr)

    def retrain(self) -> None:
        self._build_pattern_map()
        self._build_corpus()
        self._train()
        self.save()

    def _embed(self, text: str) -> np.ndarray:
        return self._embed_tokens(clean(text).split())

    def _embed_tokens(self, tokens: list[str]) -> np.ndarray:
        if self.w2v is None:
            return np.zeros(self.vector_size)
        vecs = [self.w2v.wv[w] for w in tokens if w in self.w2v.wv]
        if not vecs:
            return np.zeros(self.vector_size)
        return np.mean(vecs, axis=0).astype("float32")

    def retrieve(
        self,
        text: str,
        context: list[str] | None = None,
        pre_cleaned: bool = False,
    ) -> tuple[str, float]:
        if self.index is None:
            return "fallback", 0.0

        if pre_cleaned:
            query_tokens = text.split()
            query_text = text
        else:
            cleaned = clean(text)
            query_tokens = cleaned.split()
            query_text = cleaned

        tag = self._pattern_map.get(query_text)
        if tag:
            return tag, 1.0

        if context:
            ctx_tokens: list[str] = []
            for ctx in context[-3:]:
                ctx_tokens.extend(ctx.split())
            query_tokens = ctx_tokens + query_tokens

        vec = self._embed_tokens(query_tokens).reshape(1, -1)
        D, I = self.index.search(vec, k=3)
        best_score = float(D[0][0])
        best_idx = int(I[0][0])
        best_confidence = 1.0 / (1.0 + best_score)

        if best_confidence >= settings.nlp_confidence_threshold:
            return self.meta[best_idx], best_confidence

        candidates: list[tuple[str, float]] = []
        seen = set()
        for i in range(3):
            idx = int(I[0][i])
            tag = self.meta[idx]
            if tag not in seen:
                seen.add(tag)
                conf = 1.0 / (1.0 + float(D[0][i]))
                candidates.append((tag, conf))

        candidates.sort(key=lambda x: x[1], reverse=True)
        if candidates:
            return candidates[0], candidates[0][1]

        return "fallback", best_confidence

    def get_diverse_response(self, intent: str, responses: list[str]) -> str:
        if not settings.response_diversity:
            return random.choice(responses)

        last = self._last_responses.get(intent)
        available = [r for r in responses if r != last]
        if not available:
            available = responses
        chosen = random.choice(available)
        self._last_responses[intent] = chosen
        return chosen

    def is_loaded(self) -> bool:
        return self.w2v is not None and self.index is not None

    def save(self) -> None:
        if self.w2v:
            self.w2v.save(settings.w2v_path)
        if self.index:
            faiss.write_index(self.index, settings.faiss_path)
        with open(settings.meta_path, "w") as f:
            json.dump(self.meta, f)
