import os
import json
import getpass
import logging
from pathlib import Path
import requests
from urllib.parse import urljoin

import pandas as pd
from ace_lib import SingleSession
from helpful_functions import (
    expand_dict_columns,
    save_pnl,
    save_simulation_result,
    save_yearly_stats,
)

from mcp.server.fastmcp import FastMCP

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

mcp = FastMCP("Demo")
brain_api_url = "https://api.worldquantbrain.com"


def get_credentials() -> tuple[str, str]:
    """Retrieve or prompt for platform credentials."""
    credential_email = os.environ.get("BRAIN_CREDENTIAL_EMAIL")
    credential_password = os.environ.get("BRAIN_CREDENTIAL_PASSWORD")

    credentials_folder_path = os.path.join(os.path.expanduser("~"), "secrets")
    credentials_file_path = os.path.join(credentials_folder_path, "platform-brain.json")

    if Path(credentials_file_path).exists() and os.path.getsize(credentials_file_path) > 2:
        with open(credentials_file_path) as file:
            data = json.load(file)
    else:
        os.makedirs(credentials_folder_path, exist_ok=True)
        if credential_email and credential_password:
            email = credential_email
            password = credential_password
        else:
            email = input("Email:\n")
            password = getpass.getpass(prompt="Password: ")
        data = {"email": email, "password": password}
        with open(credentials_file_path, "w") as file:
            json.dump(data, file)
    return (data["email"], data["password"])


def start_session() -> SingleSession:
    """Start a new session with the WorldQuant BRAIN platform."""
    while True:
        s = SingleSession()
        s.auth = get_credentials()
        try:
            r = s.post(f"{brain_api_url}/authentication")
            logger.debug(f"Session ID: {id(s)}, Auth response: {r.status_code}, {r.json()}")

            if r.status_code == requests.status_codes.codes.unauthorized:
                if r.headers.get("WWW-Authenticate") == "persona":
                    biometrics_url = urljoin(r.url, r.headers["Location"])
                    logger.info("Biometrics authentication required.")
                    print(f"Complete biometrics authentication and press any key to continue:\n{biometrics_url}\n")
                    input()
                    while True:
                        retry_response = s.post(biometrics_url)
                        if retry_response.status_code == 201:
                            logger.info("Biometric authentication successful.")
                            return s
                        else:
                            input("Biometric authentication incomplete. Retry and press any key when ready:\n")
                else:
                    logger.error("Incorrect email or password.")
                    with open(os.path.join(os.path.expanduser("~"), "secrets/platform-brain.json"), "w") as file:
                        json.dump({}, file)
                    continue
            return s

        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication failed: {e}")
            raise


@mcp.tool()
def get_datasets(
    s: SingleSession,
    instrument_type: str = "EQUITY",
    region: str = "USA",
    delay: int = 1,
    universe: str = "TOP3000",
    theme: str = "false",
) -> pd.DataFrame:
    """
    Retrieve available datasets based on specified parameters.

    Args:
        s (SingleSession): An authenticated session object.
        instrument_type (str, optional): The type of instrument. Defaults to "EQUITY".
        region (str, optional): The region. Defaults to "USA".
        delay (int, optional): The delay. Defaults to 1.
        universe (str, optional): The universe. Defaults to "TOP3000".
        theme (str, optional): The theme. Defaults to "false".

    Returns:
        pandas.DataFrame: A DataFrame containing information about available datasets.
    """
    url = (
        f"{brain_api_url}/data-sets?"
        f"instrumentType={instrument_type}&region={region}&delay={delay}&universe={universe}&theme={theme}"
    )
    result = s.get(url)
    datasets_df = pd.DataFrame(result.json()["results"])
    datasets_df = expand_dict_columns(datasets_df)
    logger.info(f"Fetched {len(datasets_df)} datasets.")
    return datasets_df


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run(host="0.0.0.0", port=8000)
