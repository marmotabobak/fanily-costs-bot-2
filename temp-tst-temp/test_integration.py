"""Integration tests for the complete application."""

import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src import bot, config
from tests.constants import TEST_TOKEN, TEST_TOKEN_DICT


class TestIntegration:
    """Integration tests for the complete application."""

    @pytest.mark.asyncio
    async def test_full_application_flow(self):
        """Test the complete application flow with mocked dependencies."""
        with patch.dict(os.environ, TEST_TOKEN_DICT):
            with patch("src.bot.config.setup_logging") as mock_setup_logging:
                with patch("src.bot.config.log_configuration") as mock_log_config:
                    with patch("src.bot.auth.log_access_control") as mock_log_access:
                        with patch("src.bot.db.init_db") as mock_init_db:
                            with patch("src.bot.Bot") as mock_bot_class:
                                with patch("src.bot.Dispatcher") as mock_dp_class:
                                    # Mock bot and dispatcher instances
                                    mock_bot = MagicMock()
                                    mock_dp = MagicMock()
                                    mock_bot_class.return_value = mock_bot
                                    mock_dp_class.return_value = mock_dp

                                    # Mock the polling method
                                    mock_dp.start_polling = AsyncMock()

                                    # Run the main function
                                    try:
                                        await bot.main()
                                    except Exception as e:
                                        # We expect it to fail due to invalid token
                                        assert "Token" in str(e) or "token" in str(e)

                                    # Verify all initialization steps were called
                                    mock_setup_logging.assert_called_once()
                                    mock_log_config.assert_called_once()
                                    mock_log_access.assert_called_once()
                                    mock_init_db.assert_called_once()
                                    mock_bot_class.assert_called_once()
                                    mock_dp_class.assert_called_once()

    def test_environment_variable_loading(self):
        """Test that environment variables are loaded correctly."""
        test_vars = {"BOT_TOKEN": "test-token-123", "LOG_LEVEL": "DEBUG", "ALLOWED_USER_IDS": "123,456,789"}

        with patch.dict(os.environ, test_vars):
            assert config.get_telegram_token() == "test-token-123"
            assert config.get_allowed_user_ids() == {123, 456, 789}

    def test_database_initialization(self):
        """Test database initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"

            with patch.dict(os.environ, {"DB_PATH": str(db_path)}):
                from src.db import init_db

                init_db(str(db_path))

                # Check that database file was created
                assert db_path.exists()

    def test_application_without_env_file(self):
        """Test application behavior without .env file."""
        # Ensure .env doesn't exist
        env_file = Path(".env")
        if env_file.exists():
            env_file.unlink()

        # Test that application handles missing .env gracefully
        with patch.dict(os.environ, {}, clear=True):
            token = config.get_telegram_token()
            assert token == ""

    def test_application_with_env_file(self):
        """Test application behavior with .env file."""
        # Create temporary .env file
        env_content = """BOT_TOKEN={test_token}
LOG_LEVEL=DEBUG
ALLOWED_USER_IDS=123456789,987654321
""".format(
            test_token=TEST_TOKEN
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            env_file = f.name

        # Check if .env already exists and backup it
        original_env_exists = Path(".env").exists()
        original_env_backup = None
        if original_env_exists:
            original_env_backup = Path(".env").read_text()

        try:
            # Copy to project root
            import shutil

            shutil.copy(env_file, ".env")

            # Test that variables are loaded
            with patch.dict(os.environ, {}):
                # Simulate what Makefile does
                import subprocess

                result = subprocess.run(
                    "set -a; source .env; set +a; echo $BOT_TOKEN", shell=True, capture_output=True, text=True
                )

                assert result.returncode == 0
                assert TEST_TOKEN in result.stdout

        finally:
            # Clean up - restore original .env if it existed
            if original_env_exists and original_env_backup:
                Path(".env").write_text(original_env_backup)
            elif not original_env_exists and Path(".env").exists():
                Path(".env").unlink()

            # Clean up temporary file
            if Path(env_file).exists():
                Path(env_file).unlink()

    @pytest.mark.asyncio
    async def test_async_error_handling(self):
        """Test that async errors are handled properly."""
        with patch.dict(os.environ, {"BOT_TOKEN": "invalid-token"}):
            with patch("src.bot.config.setup_logging"):
                with patch("src.bot.config.log_configuration"):
                    with patch("src.bot.auth.log_access_control"):
                        with patch("src.bot.db.init_db"):
                            # This should raise TokenValidationError
                            with pytest.raises(Exception) as exc_info:
                                await bot.main()

                            # Should be TokenValidationError or similar
                            assert "Token" in str(exc_info.value) or "token" in str(exc_info.value)

    def test_configuration_validation(self):
        """Test configuration validation."""
        # Test valid configurations
        valid_configs = [
            TEST_TOKEN_DICT,
            {"BOT_TOKEN": TEST_TOKEN, "LOG_LEVEL": "DEBUG"},
            {"BOT_TOKEN": TEST_TOKEN, "ALLOWED_USER_IDS": "123,456"},
        ]

        for config_vars in valid_configs:
            with patch.dict(os.environ, config_vars):
                # These should not raise exceptions
                config.setup_logging()
                config.get_telegram_token()
                config.get_allowed_user_ids()
                config.log_configuration()

    def test_makefile_integration(self):
        """Test Makefile integration with the application."""
        # Test that make run command exists and is properly formatted
        with open("Makefile", "r") as f:
            makefile_content = f.read()

        # Check that run target exists
        assert "run:" in makefile_content

        # Check that it loads .env
        assert "source .env" in makefile_content

        # Check that it calls python main.py
        assert "python main.py" in makefile_content or "$(PYTHON) main.py" in makefile_content
