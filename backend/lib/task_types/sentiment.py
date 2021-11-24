from functools import cache

import pyarrow
from transformers import pipeline

from pipeline.task import OneToOneRowwiseTask


class HuggingFaceTextClassificationModel:
    def __init__(self, name):
        self.name = name

    @property
    @cache
    def classifier(self):
        return pipeline("text-classification", model=self.name, tokenizer=self.name)

    @property
    def classes(self):
        label2id = self.classifier.model.config.label2id
        return sorted(list(label2id), key=lambda label: label2id[label])

    def __call__(self, text):
        label2id = self.classifier.model.config.label2id
        for results in self.classifier(text, return_all_scores=True):
            results.sort(key=lambda r: label2id[r["label"]])
            return tuple(r["score"] for r in results)


class SentimentAnalysis(OneToOneRowwiseTask):
    def __init__(self, model: str, **other):
        super().__init__(**other)
        self.model = HuggingFaceTextClassificationModel(model)

    def args(self):
        return {
            **super().to_dict(),
            "model": self.model.name,
        }

    def configure(self) -> bool:
        return True

    def schema(self) -> pyarrow.Schema:
        return pyarrow.schema(
            {label: pyarrow.float64() for label in self.model.classes}
        )

    def execute(self, text: str):
        return self.model(text)
