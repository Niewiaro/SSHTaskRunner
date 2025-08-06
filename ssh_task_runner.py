import paramiko
import logging
import toml


# --- Logging setup ---
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
)
logger = logging.getLogger(__name__)


# --- Command class ---
class Command:
    """
    Represents a shell command to be executed over SSH.
    """

    def __init__(
        self, command: str, description: str = "", directory: str = None
    ) -> None:
        self.command = command
        self.description = description
        self.directory = directory

    def build(self) -> str:
        if self.directory:
            return f"cd {self.directory} && {self.command}"
        return self.command


# --- SSHTaskRunner class ---
class SSHTaskRunner:
    """
    Executes a sequence of commands over SSH, including parallel execution.

    Loads configuration from a .toml file and manages SSH connections.
    """

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        CONFIG = f"""
        hostname={self.config["ssh"]["host"]},
        username={self.config["ssh"]["user"]},
        password={self.config["ssh"]["password"]},
        port={self.config["ssh"].get("port", 22)},
        """
        logger.debug(CONFIG)

    def _load_config(self, path: str) -> dict:
        """Loads configuration from a TOML file."""
        try:
            return toml.load(path)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise


def main() -> None:
    from pathlib import Path

    CONFIG_PATH = Path(__file__).parent / "config.toml"

    runner = SSHTaskRunner(CONFIG_PATH)


if __name__ == "__main__":
    main()
