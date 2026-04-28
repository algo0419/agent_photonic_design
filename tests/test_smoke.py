from PhotonicsAI.KnowledgeBase.DesignLibrary._directional_coupler import get_model_ana
from PhotonicsAI.config import CONF


def test_openai_reasoning_model_default():
    assert CONF.openai_reasoning_model


def test_directional_coupler_5050_baseline():
    model = get_model_ana(wl=1.55, length=6.0)
    s31 = abs(model[("o1", "o3")]) ** 2
    s41 = abs(model[("o1", "o4")]) ** 2
    assert round(float(s31), 6) == 0.5
    assert round(float(s41), 6) == 0.5
