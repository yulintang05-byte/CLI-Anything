"""Unit tests for the theme_pages module."""
import pytest
from cli_anything.viral_trends import theme_pages as tp


def test_get_guide_has_steps():
    guide = tp.get_guide()
    assert "step_by_step" in guide
    assert len(guide["step_by_step"]) == 7


def test_get_guide_has_monetization():
    guide = tp.get_guide()
    assert "step_by_step" in guide
    steps = {s["step"]: s for s in guide["step_by_step"]}
    assert 6 in steps


def test_get_step_valid():
    step = tp.get_step(1)
    assert step["step"] == 1
    assert "title" in step
    assert "actions" in step


def test_get_step_invalid():
    with pytest.raises(ValueError, match="Step 99"):
        tp.get_step(99)


def test_get_step_all_steps():
    for i in range(1, 8):
        step = tp.get_step(i)
        assert step["step"] == i


def test_get_monetization_timeline():
    phases = tp.get_monetization_timeline()
    assert len(phases) > 0
    assert all("phase" in p for p in phases)


def test_conversion_metrics_present():
    guide = tp.get_guide()
    metrics = guide.get("conversion_metrics_to_track", {})
    assert "save_rate" in metrics
    assert "follow_rate" in metrics


def test_common_mistakes_present():
    guide = tp.get_guide()
    mistakes = guide.get("common_mistakes", [])
    assert len(mistakes) >= 3


def test_step_3_has_legal_methods():
    step = tp.get_step(3)
    actions_text = " ".join(step.get("actions", []))
    assert "Method A" in actions_text or "curate" in actions_text.lower()
