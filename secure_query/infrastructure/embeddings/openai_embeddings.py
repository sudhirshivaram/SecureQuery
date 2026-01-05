"""
Embeddings Service

Converts text to vector embeddings using OpenAI or local models.
"""

import os
from typing import List, Optional

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Lazy import for sentence-transformers to avoid dependency issues
SENTENCE_TRANSFORMERS_AVAILABLE = None  # Will check when needed


class EmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self, provider: str = "sentence-transformers", api_key: Optional[str] = None):
        """
        Initialize embedding service.

        Args:
            provider: "openai" or "sentence-transformers" (free/local)
            api_key: OpenAI API key (if using openai provider)
        """
        self.provider = provider

        if provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI package not installed. Install with: pip install openai")

            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            self.model = "text-embedding-3-small"  # Cheaper, faster

        elif provider == "sentence-transformers":
            # Lazy import to avoid dependency issues
            try:
                from sentence_transformers import SentenceTransformer
                # all-MiniLM-L6-v2 is fast and good for similarity search
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                raise ImportError(
                    "Sentence-transformers not installed. Install with: pip install sentence-transformers"
                )

        else:
            raise ValueError(f"Unknown provider: {provider}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        if self.provider == "openai":
            return self._embed_with_openai(texts)
        elif self.provider == "sentence-transformers":
            return self._embed_with_sentence_transformers(texts)

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        return self.embed_texts([text])[0]

    def _embed_with_openai(self, texts: List[str]) -> List[List[float]]:
        """Use OpenAI embeddings."""
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )

        embeddings = [item.embedding for item in response.data]
        return embeddings

    def _embed_with_sentence_transformers(self, texts: List[str]) -> List[List[float]]:
        """Use local sentence-transformers model (FREE)."""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    @staticmethod
    def create_auto(api_key: Optional[str] = None) -> "EmbeddingService":
        """
        Auto-detect and create best available embedding service.

        Priority: OpenAI (with key) → sentence-transformers (free)
        """
        # Try OpenAI first if we have a key
        if OPENAI_AVAILABLE and (api_key or os.getenv("OPENAI_API_KEY")):
            return EmbeddingService(provider="openai", api_key=api_key)

        # Try sentence-transformers (may fail if Keras issues)
        try:
            return EmbeddingService(provider="sentence-transformers")
        except (ImportError, Exception):
            pass

        raise RuntimeError(
            "No embedding provider available. Please:\n"
            "  1. Set OPENAI_API_KEY or GEMINI_API_KEY environment variable\n"
            "  OR install: pip install sentence-transformers"
        )
