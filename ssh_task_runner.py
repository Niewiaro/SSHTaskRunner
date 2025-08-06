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


# --- SSHTaskRunner class ---
class SSHTaskRunner:
    """
    Executes a sequence of commands over SSH, including parallel execution.

    Loads configuration from a .toml file and manages SSH connections.
    """

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.main_ssh = self._create_connection()

    def _load_config(self, path: str) -> dict:
        """Loads configuration from a TOML file."""

        try:
            return toml.load(path)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    def _create_connection(self) -> paramiko.SSHClient:
        """Creates and returns a new SSH connection."""

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=self.config["ssh"]["host"],
            username=self.config["ssh"]["user"],
            password=self.config["ssh"]["password"],
            port=self.config["ssh"].get("port", 22),
        )
        return ssh

    def _run_command(self, ssh: paramiko.SSHClient, command: Command) -> dict:
        """Executes a single command on a given SSH connection."""

        full_cmd = command.build()
        description = command.description or command.command
        logger.info(f"Executing: {description}")

        try:
            stdin, stdout, stderr = ssh.exec_command(full_cmd)

            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            exit_status = stdout.channel.recv_exit_status()

            logger.info(f"Finished: {description} (exit={exit_status})")

            return {
                "description": description,
                "command": full_cmd,
                "stdout": out,
                "stderr": err,
                "exit_status": exit_status,
            }

        except Exception as e:
            logger.exception(f"Failed to execute: {description}")
            return {
                "description": description,
                "command": full_cmd,
                "stdout": "",
                "stderr": str(e),
                "exit_status": -1,
            }

    def test(self, command: Command):
        self._run_command(self.main_ssh, command)


def main() -> None:
    from pathlib import Path

    CONFIG_PATH = Path(__file__).parent / "config.toml"

    repo_dir = "/home"

    show_files = {
        "command": "ls -al",
        "description": "Show files.",
    }

    command = Command(**show_files, directory=repo_dir)

    runner = SSHTaskRunner(CONFIG_PATH)

    runner.test(command)


if __name__ == "__main__":
    main()
