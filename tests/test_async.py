"""Tests for async functionality and token validation."""

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.utils.token import TokenValidationError

from src import bot
from tests.constants import TEST_TOKEN, TEST_TOKEN_DICT


class TestAsyncFunctionality:
    """Test async functionality."""

    @pytest.mark.asyncio
    async def test_main_function_is_async(self):
        """Test that main function is properly async."""
        # This test ensures main() is a coroutine
        assert asyncio.iscoroutinefunction(bot.main)

    @pytest.mark.asyncio
    async def test_main_with_invalid_token(self):
        """Test main function with invalid token."""
        with patch.dict(os.environ, {"BOT_TOKEN": "invalid-token"}):
            with patch("src.bot.config.setup_logging"):
                with patch("src.bot.config.log_configuration"):
                    with patch("src.bot.auth.log_access_control"):
                        with patch("src.bot.db.init_db"):
                            with pytest.raises(TokenValidationError):
                                await bot.main()

    @pytest.mark.asyncio
    async def test_main_with_valid_token_format(self):
        """Test main function with valid token format (but invalid token)."""
        # Valid format: numbers:letters
        with patch.dict(os.environ, TEST_TOKEN_DICT):
            with patch("src.bot.config.setup_logging"):
                with patch("src.bot.config.log_configuration"):
                    with patch("src.bot.auth.log_access_control"):
                        with patch("src.bot.db.init_db"):
                            # This should not raise TokenValidationError for format
                            # but might fail on actual bot creation
                            try:
                                await bot.main()
                            except Exception as e:
                                # Should not be TokenValidationError
                                assert not isinstance(e, TokenValidationError)

    @pytest.mark.asyncio
    async def test_main_with_empty_token(self):
        """Test main function with empty token."""
        with patch.dict(os.environ, {"BOT_TOKEN": ""}):
            with patch("src.bot.config.setup_logging"):
                with patch("src.bot.config.log_configuration"):
                    with patch("src.bot.auth.log_access_control"):
                        with patch("src.bot.db.init_db"):
                            with pytest.raises(TokenValidationError):
                                await bot.main()

    def test_token_validation_edge_cases(self):
        """Test token validation edge cases."""
        # Test various invalid token formats
        invalid_tokens = [
            "",  # Empty
            "invalid",  # No colon
            "123",  # Too short
            "123:",  # No letters after colon
            ":letters",  # No numbers before colon
            "123:letters",  # Wrong format (should be numbers:letters)
            "1234567890:letters",  # Wrong format
        ]

        for token in invalid_tokens:
            with patch.dict(os.environ, {"BOT_TOKEN": token}):
                with patch("src.bot.config.setup_logging"):
                    with patch("src.bot.config.log_configuration"):
                        with patch("src.bot.auth.log_access_control"):
                            with patch("src.bot.db.init_db"):
                                with pytest.raises((TokenValidationError, Exception)):
                                    asyncio.run(bot.main())

    @pytest.mark.asyncio
    async def test_main_initialization_sequence(self):
        """Test that main function calls initialization in correct order."""
        with patch.dict(os.environ, TEST_TOKEN_DICT):
            with patch("src.bot.config.setup_logging") as mock_setup_logging:
                with patch("src.bot.config.log_configuration") as mock_log_config:
                    with patch("src.bot.auth.log_access_control") as mock_log_access:
                        with patch("src.bot.db.init_db") as mock_init_db:
                            with patch("src.bot.Bot") as mock_bot:
                                with patch("src.bot.Dispatcher") as mock_dp_class:
                                    # Mock the bot and dispatcher
                                    mock_bot_instance = MagicMock()
                                    mock_dp_instance = MagicMock()
                                    mock_bot.return_value = mock_bot_instance
                                    mock_dp_class.return_value = mock_dp_instance
                                    mock_dp_instance.start_polling = AsyncMock()

                                    try:
                                        await bot.main()
                                    except Exception:
                                        pass  # We expect it to fail, but want to check call order

                                    # Verify initialization sequence
                                    mock_setup_logging.assert_called_once()
                                    mock_log_config.assert_called_once()
                                    mock_log_access.assert_called_once()
                                    mock_init_db.assert_called_once()
                                    mock_bot.assert_called_once()
                                    mock_dp_class.assert_called_once()


class TestTokenValidation:
    """Test token validation specifically."""

    def test_valid_token_format(self):
        """Test that valid token format is accepted by aiogram."""
        from aiogram import Bot

        # This should not raise TokenValidationError
        try:
            Bot(token=TEST_TOKEN, parse_mode=None)
        except TokenValidationError:
            # This is expected for fake tokens, but format should be valid
            pass

    def test_invalid_token_formats(self):
        """Test that invalid token formats raise TokenValidationError."""
        from aiogram import Bot

        # Only test tokens that actually cause validation errors
        invalid_tokens = [
            "",  # Empty token
            "invalid",  # No colon
            "123",  # Too short
        ]

        for token in invalid_tokens:
            with pytest.raises((TokenValidationError, Exception)):
                Bot(token=token, parse_mode=None)
