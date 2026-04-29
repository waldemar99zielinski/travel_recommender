from __future__ import annotations

import sys
from pathlib import Path

import uvicorn

sys.path.append(str(Path(__file__).resolve().parent / "src"))

from api.core.configuration import ApiEnvironment
from api.core.configuration import load_api_configuration


def main() -> None:
    configuration = load_api_configuration()
    uvicorn.run(
        "api.main:app",
        app_dir="src",
        host=configuration.host,
        port=configuration.port,
        reload=configuration.env == ApiEnvironment.development,
    )


if __name__ == "__main__":
    main()
