from dataclasses import dataclass
from dotenv import load_dotenv
import os
from pathlib import Path

# Buscar .env en el directorio raíz del proyecto (no solo en el cwd)
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)


@dataclass
class Settings:
    base_url: str = "https://api.semanticscholar.org/graph/v1"
    api_key: str | None = os.getenv("S2_API_KEY")
    timeout: int = 30
    max_retries: int = 3


settings = Settings()

