import paramiko
import logging
import toml


# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
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


def main() -> None:
    logger.info("Init")


if __name__ == "__main__":
    main()
