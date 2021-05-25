import os
from unittest.mock import patch

import pytest
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from transformers_interpret import ZeroShotClassificationExplainer
from transformers_interpret.errors import (
    AttributionTypeNotSupportedError,
    InputIdsNotCalculatedError,
)

DISTILBERT_MNLI_MODEL = AutoModelForSequenceClassification.from_pretrained(
    "typeform/distilbert-base-uncased-mnli"
)
DISTILBERT_MNLI_TOKENIZER = AutoTokenizer.from_pretrained(
    "typeform/distilbert-base-uncased-mnli"
)


def test_zero_shot_explainer_init_distilbert():
    zero_shot_explainer = ZeroShotClassificationExplainer(
        DISTILBERT_MNLI_MODEL,
        DISTILBERT_MNLI_TOKENIZER,
    )

    assert zero_shot_explainer.attribution_type == "lig"
    assert zero_shot_explainer.attributions is None
    assert zero_shot_explainer.label_exists is True
    assert zero_shot_explainer.entailment_key == "ENTAILMENT"


def test_zero_shot_explainer_init_attribution_type_error():
    with pytest.raises(AttributionTypeNotSupportedError):
        ZeroShotClassificationExplainer(
            DISTILBERT_MNLI_MODEL,
            DISTILBERT_MNLI_TOKENIZER,
            attribution_type="UNSUPPORTED",
        )


@patch.object(
    ZeroShotClassificationExplainer,
    "_entailment_label_exists",
    return_value=(False, None),
)
def test_zero_shot_explainer_no_entailment_label(mock_method):
    with pytest.raises(ValueError):
        ZeroShotClassificationExplainer(
            DISTILBERT_MNLI_MODEL,
            DISTILBERT_MNLI_TOKENIZER,
        )


def test_zero_shot_explainer_word_attributions():
    zero_shot_explainer = ZeroShotClassificationExplainer(
        DISTILBERT_MNLI_MODEL,
        DISTILBERT_MNLI_TOKENIZER,
    )

    word_attributions = zero_shot_explainer(
        "I have a problem with my iphone that needs to be resolved asap!!",
        labels=["urgent", " not", "urgent", "phone", "tablet", "computer"],
    )
    assert isinstance(word_attributions, list)


def test_zero_shot_explainer_call_word_attributions_early_raises_error():
    with pytest.raises(ValueError):
        zero_shot_explainer = ZeroShotClassificationExplainer(
            DISTILBERT_MNLI_MODEL,
            DISTILBERT_MNLI_TOKENIZER,
        )

        zero_shot_explainer.word_attributions


def test_zero_shot_explainer_word_attributions_include_hypothesis():
    zero_shot_explainer = ZeroShotClassificationExplainer(
        DISTILBERT_MNLI_MODEL,
        DISTILBERT_MNLI_TOKENIZER,
    )

    word_attributions_with_hyp = zero_shot_explainer(
        "I have a problem with my iphone that needs to be resolved asap!!",
        labels=["urgent", " not", "urgent", "phone", "tablet", "computer"],
        include_hypothesis=True,
    )
    word_attributions_without_hyp = zero_shot_explainer(
        "I have a problem with my iphone that needs to be resolved asap!!",
        labels=["urgent", " not", "urgent", "phone", "tablet", "computer"],
        include_hypothesis=False,
    )
    assert len(word_attributions_with_hyp) > len(word_attributions_without_hyp)


def test_zero_shot_explainer_visualize():
    zero_shot_explainer = ZeroShotClassificationExplainer(
        DISTILBERT_MNLI_MODEL,
        DISTILBERT_MNLI_TOKENIZER,
    )

    zero_shot_explainer(
        "I have a problem with my iphone that needs to be resolved asap!!",
        labels=["urgent", " not", "urgent", "phone", "tablet", "computer"],
    )
    zero_shot_explainer.visualize()


def test_zero_shot_explainer_visualize_save():
    zero_shot_explainer = ZeroShotClassificationExplainer(
        DISTILBERT_MNLI_MODEL,
        DISTILBERT_MNLI_TOKENIZER,
    )

    zero_shot_explainer(
        "I have a problem with my iphone that needs to be resolved asap!!",
        labels=["urgent", " not", "urgent", "phone", "tablet", "computer"],
    )
    html_filename = "./test/zero_test.html"
    zero_shot_explainer.visualize(html_filename)
    assert os.path.exists(html_filename)
    os.remove(html_filename)


def test_zero_shot_explainer_visualize_include_hypothesis():
    zero_shot_explainer = ZeroShotClassificationExplainer(
        DISTILBERT_MNLI_MODEL,
        DISTILBERT_MNLI_TOKENIZER,
    )

    zero_shot_explainer(
        "I have a problem with my iphone that needs to be resolved asap!!",
        labels=["urgent", " not", "urgent", "phone", "tablet", "computer"],
        include_hypothesis=True,
    )
    zero_shot_explainer.visualize()


def test_zero_explainer_visualize_save_append_html_file_ending():
    zero_shot_explainer = ZeroShotClassificationExplainer(
        DISTILBERT_MNLI_MODEL,
        DISTILBERT_MNLI_TOKENIZER,
    )

    zero_shot_explainer(
        "I have a problem with my iphone that needs to be resolved asap!!",
        labels=["urgent", " not", "urgent", "phone", "tablet", "computer"],
    )

    html_filename = "./test/zero_test"
    zero_shot_explainer.visualize(html_filename)
    assert os.path.exists(html_filename + ".html")
    os.remove(html_filename + ".html")


def test_zero_shot_model_does_not_have_entailment_label():
    with patch.object(
        DISTILBERT_MNLI_MODEL.config, "label2id", {"l1": 0, "l2": 1, "l3": 2}
    ):
        with pytest.raises(ValueError):
            ZeroShotClassificationExplainer(
                DISTILBERT_MNLI_MODEL,
                DISTILBERT_MNLI_TOKENIZER,
            )


def test_zero_shot_model_uppercase_entailment():
    with patch.object(
        DISTILBERT_MNLI_MODEL.config, "label2id", {"ENTAILMENT": 0, "l2": 1, "l3": 2}
    ):
        ZeroShotClassificationExplainer(
            DISTILBERT_MNLI_MODEL,
            DISTILBERT_MNLI_TOKENIZER,
        )


def test_zero_shot_model_lowercase_entailment():
    with patch.object(
        DISTILBERT_MNLI_MODEL.config, "label2id", {"entailment": 0, "l2": 1, "l3": 2}
    ):
        ZeroShotClassificationExplainer(
            DISTILBERT_MNLI_MODEL,
            DISTILBERT_MNLI_TOKENIZER,
        )