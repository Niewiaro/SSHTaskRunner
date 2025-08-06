import logging
import paramiko


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

    from typing import List

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.main_ssh = self._create_connection()
        logger.info("Main SSH connection established.")

    def _load_config(self, path: str) -> dict:
        """Loads configuration from a TOML file."""

        import toml

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
        result = {
            "description": description,
            "command": full_cmd,
            "stdout": None,
            "stderr": None,
            "exit_status": None,
        }

        try:
            stdin, stdout, stderr = ssh.exec_command(full_cmd)

            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            exit_status = stdout.channel.recv_exit_status()

            result["stdout"] = out
            result["stderr"] = err
            result["exit_status"] = exit_status

            return result

        except Exception as e:
            result["stdout"] = ""
            result["stderr"] = str(e)
            result["exit_status"] = -1

            return result

    def _log_result(self, result: dict) -> None:
        """Logs the result of command execution."""

        logger.info(f"Command: {result["description"]}")
        logger.info(f"Exit status: {result['exit_status']}")

        if result["stdout"].strip():
            logger.info("STDOUT:\n" + result["stdout"].strip())

        if result["stderr"].strip():
            if result["exit_status"] == 0:
                logger.info("STDERR (informational):\n" + result["stderr"].strip())
            else:
                logger.error("STDERR:\n" + result["stderr"].strip())

    def execute(self, sequence: List[Command]) -> None:
        """
        Executes a sequence of commands.

        Aborts on first failure.
        """

        try:
            for step in sequence:
                if isinstance(step, Command):
                    result = self._run_command(self.main_ssh, step)
                    self._log_result(result)

                    if result["exit_status"] != 0:
                        logger.error("Execution aborted due to command failure.")
                        return
                else:
                    raise ValueError("Invalid step in sequence.")

            logger.info("All commands completed successfully.")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
        finally:
            self.main_ssh.close()
            logger.info("Main SSH connection closed.")


def main() -> None:
    from pathlib import Path

    CONFIG_PATH = Path(__file__).parent / "config.toml"

    repo_dir = "/home"

    show_files = {
        "command": "ls",
        "description": "Show files.",
    }
    show_all_files = {
        "command": "ls -al",
        "description": "Show all files.",
    }

    command_0 = Command(**show_files, directory=repo_dir)
    command_1 = Command(**show_all_files, directory=repo_dir)

    runner = SSHTaskRunner(CONFIG_PATH)

    sequence = [command_0, command_1]
    runner.execute(sequence)


if __name__ == "__main__":
    main()
