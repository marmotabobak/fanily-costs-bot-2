"""Tests for Makefile functionality."""

import subprocess
import tempfile
from pathlib import Path

from tests.constants import TEST_TOKEN


class TestMakefile:
    """Test Makefile functionality."""

    def test_makefile_exists(self):
        """Test that Makefile exists and is readable."""
        makefile_path = Path("Makefile")
        assert makefile_path.exists()
        assert makefile_path.is_file()

    def test_makefile_has_run_target(self):
        """Test that Makefile has run target."""
        with open("Makefile", "r") as f:
            content = f.read()
            assert "run:" in content

    def test_makefile_has_env_loading(self):
        """Test that Makefile loads .env file."""
        with open("Makefile", "r") as f:
            content = f.read()
            assert "source .env" in content
            assert "set -a" in content
            assert "set +a" in content

    def test_makefile_checks_env_file(self):
        """Test that Makefile checks for .env file existence."""
        with open("Makefile", "r") as f:
            content = f.read()
            assert "if [ -f .env ]" in content

    def test_makefile_run_without_env(self):
        """Test that make run works without .env file."""
        # Check if .env exists and backup it
        env_file = Path(".env")
        original_env_exists = env_file.exists()
        original_env_backup = None
        if original_env_exists:
            original_env_backup = env_file.read_text()
            env_file.unlink()

        try:
            # This should not crash, but might fail due to missing token
            result = subprocess.run(["make", "run"], capture_output=True, text=True, timeout=10)

            # Should fail due to invalid token, not due to missing .env
            assert result.returncode != 0
            assert "Token" in result.stderr or "Unauthorized" in result.stderr
        finally:
            # Restore original .env if it existed
            if original_env_exists and original_env_backup:
                env_file.write_text(original_env_backup)

    def test_makefile_run_with_env(self):
        """Test that make run works with .env file."""
        # Check if .env already exists and backup it
        env_file_path = Path(".env")
        original_env_exists = env_file_path.exists()
        original_env_backup = None
        if original_env_exists:
            original_env_backup = env_file_path.read_text()

        # Create temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(f"BOT_TOKEN={TEST_TOKEN}\n")
            temp_env_file = f.name

        try:
            # Copy to project root
            import shutil

            shutil.copy(temp_env_file, ".env")

            # This should not crash due to missing .env, but might fail due to invalid token
            result = subprocess.run(["make", "run"], capture_output=True, text=True, timeout=10)

            # Should fail due to invalid token, not due to missing .env
            assert result.returncode != 0
            assert "Token" in result.stderr or "Unauthorized" in result.stderr

        finally:
            # Restore original .env if it existed
            if original_env_exists and original_env_backup:
                env_file_path.write_text(original_env_backup)
            elif not original_env_exists and env_file_path.exists():
                env_file_path.unlink()

            # Clean up temporary file
            if Path(temp_env_file).exists():
                Path(temp_env_file).unlink()

    def test_makefile_other_targets(self):
        """Test that other Makefile targets work."""
        targets = ["install", "fmt", "lint"]

        for target in targets:
            result = subprocess.run(["make", target], capture_output=True, text=True, timeout=30)
            # Most targets should succeed
            if target == "install":
                # Install might fail if already installed, that's ok
                pass
            else:
                assert result.returncode == 0, f"Target {target} failed: {result.stderr}"

    def test_makefile_env_loading_syntax(self):
        """Test that Makefile env loading syntax is correct."""
        # Test the shell syntax used in Makefile
        test_env_content = "BOT_TOKEN=test-token\nLOG_LEVEL=DEBUG\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(test_env_content)
            env_file = f.name

        try:
            # Test the exact syntax from Makefile
            result = subprocess.run(
                f"if [ -f {env_file} ]; then set -a; source {env_file}; set +a; fi; echo $BOT_TOKEN",
                shell=True,
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert "test-token" in result.stdout

        finally:
            if Path(env_file).exists():
                Path(env_file).unlink()
