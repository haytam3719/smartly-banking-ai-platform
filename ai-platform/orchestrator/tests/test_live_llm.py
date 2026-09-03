import os,pytest
@pytest.mark.live_llm
@pytest.mark.skipif(os.getenv('LIVE_LLM_TESTS')!='1',reason='set LIVE_LLM_TESTS=1 with LLM configuration')
async def test_live_llm_configuration_is_explicit():
    assert os.getenv('LLM_BASE_URL') and os.getenv('LLM_API_KEY') and os.getenv('LLM_MODEL')
