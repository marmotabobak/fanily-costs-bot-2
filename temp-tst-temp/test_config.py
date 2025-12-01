"""Tests for configuration and async functionality."""

import os
from unittest.mock import patch

import pytest

from src import config


class TestConfig:
    """Test configuration management."""

    @pytest.mark.fast
    @pytest.mark.unit
    def test_setup_logging(self):
        """Test that logging is configured correctly."""
        # This test ensures logging setup doesn't crash
        config.setup_logging()
        # If we get here without exception, test passes

    @pytest.mark.fast
    @pytest.mark.unit
    def test_get_telegram_token_from_env(self):
        """Test getting token from environment variable."""
        with patch.dict(os.environ, {"BOT_TOKEN": "test-token-123"}):
            token = config.get_telegram_token()
            assert token == "test-token-123"

    @pytest.mark.fast
    @pytest.mark.unit
    def test_get_telegram_token_empty(self):
        """Test getting token when not set."""
        with patch.dict(os.environ, {}, clear=True):
            token = config.get_telegram_token()
            assert token == ""

    @pytest.mark.fast
    @pytest.mark.unit
    def test_get_allowed_user_ids_raw(self):
        """Test getting raw user IDs from environment."""
        with patch.dict(os.environ, {"ALLOWED_USER_IDS": "123,456,789"}):
            user_ids = config.get_allowed_user_ids_raw()
            assert user_ids == "123,456,789"

    @pytest.mark.fast
    @pytest.mark.unit
    def test_parse_allowed_user_ids_valid(self):
        """Test parsing valid user IDs."""
        user_ids = config.parse_allowed_user_ids("123,456,789")
        assert user_ids == {123, 456, 789}

    @pytest.mark.fast
    @pytest.mark.unit
    def test_parse_allowed_user_ids_with_spaces(self):
        """Test parsing user IDs with spaces."""
        user_ids = config.parse_allowed_user_ids("123, 456 , 789")
        assert user_ids == {123, 456, 789}

    @pytest.mark.fast
    @pytest.mark.unit
    def test_parse_allowed_user_ids_empty(self):
        """Test parsing empty string."""
        user_ids = config.parse_allowed_user_ids("")
        assert user_ids == set()

    @pytest.mark.fast
    @pytest.mark.unit
    def test_parse_allowed_user_ids_invalid(self):
        """Test parsing invalid user IDs (should skip invalid ones)."""
        user_ids = config.parse_allowed_user_ids("123,invalid,456")
        assert user_ids == {123, 456}

    @pytest.mark.fast
    @pytest.mark.unit
    def test_get_allowed_user_ids(self):
        """Test getting parsed user IDs."""
        with patch.dict(os.environ, {"ALLOWED_USER_IDS": "123,456"}):
            user_ids = config.get_allowed_user_ids()
            assert user_ids == {123, 456}

    @pytest.mark.fast
    @pytest.mark.unit
    def test_log_configuration(self):
        """Test that configuration logging doesn't crash."""
        with patch.dict(os.environ, {"BOT_TOKEN": "test", "LOG_LEVEL": "INFO"}):
            # This test ensures logging doesn't crash
            config.log_configuration()
            # If we get here without exception, test passes
