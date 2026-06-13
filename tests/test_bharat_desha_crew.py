import os
os.environ.setdefault("OPENROUTER_API_KEY", "x")
os.environ.setdefault("TAVILY_API_KEY", "x")

import config

def test_bharat_desha_table_config():
    assert config.BHARAT_DESHA_TABLE == "bharat_desha"
