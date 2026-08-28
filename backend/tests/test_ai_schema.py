from google import genai
from google.genai import _transformers

from app.models import AnswerMapping


def test_answer_mapping_schema_is_supported_by_google_genai() -> None:
    client = genai.Client(api_key="test-key")
    converted = _transformers.t_schema(client._api_client, AnswerMapping)

    assert converted is not None
    assert "exclusiveMinimum" not in str(AnswerMapping.model_json_schema())
