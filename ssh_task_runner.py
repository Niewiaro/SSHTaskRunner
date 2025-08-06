import paramiko
import logging
import toml


# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Init")


if __name__ == "__main__":
    main()
