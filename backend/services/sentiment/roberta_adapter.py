
from transformers import pipeline

from backend.services.sentiment.base_model import (
    BaseSentimentModel
)

from backend.services.sentiment.sentiment_result import (
    SentimentResult
)


class RoBERTaAdapter(
    BaseSentimentModel
):

    def __init__(self):

        self.model = pipeline(
            "sentiment-analysis",
            model=
            "cardiffnlp/twitter-roberta-base-sentiment-latest"
        )

    def predict(
        self,
        text: str
    ) -> SentimentResult:

        # long complaints exceed the model's 512-token limit and crashed /analyze;
        # sentiment is read from the first 512 tokens
        result = self.model(
            text,
            truncation=True,
            max_length=512,
        )[0]
        sentiment = result["label"].capitalize()
        return SentimentResult(
            sentiment=sentiment,
            confidence=float(
                result["score"]
            ),
            model_name="roberta"
        )