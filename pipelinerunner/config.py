import os

from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv() # loading .env file


@dataclass
class DevOpsConfig:
    personal_access_token: str = os.getenv("AZURE_DEVOPS_PERSONAL_ACCESS_TOKEN")
    organization_name: str = os.getenv("AZURE_DEVOPS_ORGANIZATION_NAME")

    @classmethod
    def validate(cls):
        """Ensures all required environment variables are set and not empty."""
        missing = [
            var for var, value in cls().__dict__.items() if not value
        ]
        if missing:
            raise MissingEnvVars(f"Missing required environment variables: {', '.join(missing)}")


DevOpsConfig.validate()


class MissingEnvVars(ValueError):
    pass
