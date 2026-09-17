"""tests/test_pipeline.py — Unit tests for the pipeline wrapper and retry logic."""
from unittest.mock import AsyncMock, patch
import pytest
from src.week2.pipeline.fake_llm import FakeLLMError
from src.week2.pipeline.pipeline import Answer, Question


@pytest.mark.asyncio
async def test_ask_llm_calls_fake_once():
    fake_ans = Answer(question="test", text="Mocked answer.")
    with patch(
        "src.week2.pipeline.pipeline.fake_ask_llm",
        AsyncMock(return_value=fake_ans),
    ) as mock_call:
        from src.week2.pipeline.pipeline import ask_llm
        from src.week2.pipeline.settings import Settings

        settings = Settings(use_fake=True)
        res = await ask_llm(Question(text="test"), settings=settings)

        assert mock_call.call_count == 1
        assert res.text == "Mocked answer."


@pytest.mark.asyncio
async def test_retry_three_times_on_failure():
    with patch(
        "src.week2.pipeline.pipeline.fake_ask_llm",
        AsyncMock(side_effect=FakeLLMError("Transient API failure")),
    ) as mock_call:
        with patch("asyncio.sleep", AsyncMock()):
            from src.week2.pipeline.pipeline import ask_llm_with_retry
            from src.week2.pipeline.settings import Settings

            settings = Settings(use_fake=True)
            with pytest.raises(FakeLLMError):
                await ask_llm_with_retry(Question(text="fail_test"), tries=3, settings=settings)

            assert mock_call.call_count == 3