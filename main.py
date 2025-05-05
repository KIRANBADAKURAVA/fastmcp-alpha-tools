from auth import get_session
import logging
from pathlib import Path
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


@mcp.tool()
def get_datasets(
    instrument_type: str = "EQUITY",
    region: str = "USA",
    delay: int = 1,
    universe: str = "TOP3000",
    theme: str = "false",
) -> pd.DataFrame:
    """
    Retrieve available datasets based on specified parameters.

    Args:
        instrument_type (str, optional): The type of instrument. Defaults to "EQUITY".
        region (str, optional): The region. Defaults to "USA".
        delay (int, optional): The delay. Defaults to 1.
        universe (str, optional): The universe. Defaults to "TOP3000".
        theme (str, optional): The theme. Defaults to "false".

    Returns:
        pandas.DataFrame: A DataFrame containing information about available datasets.
    """
    try:
        # Get the authenticated session (note the function call with parentheses)
        s = get_session()
        
        if s is None:
            logger.error("Failed to initialize session.")
            return pd.DataFrame()  # Return empty DataFrame instead of exiting
        
        logger.info(f"Session initialized: {s._instance}")
        
        # Construct the URL with the provided parameters
        url = (
            f"{brain_api_url}/data-sets?"
            f"instrumentType={instrument_type}&region={region}&delay={delay}&universe={universe}&theme={theme}"
        )
        
        # Make the API request
        result = s.get(url)
        
        # Check if the request was successful
        if result.status_code != 200:
            logger.error(f"API request failed with status code {result.status_code}: {result.text}")
            return pd.DataFrame()
        
        # Process the successful response
        datasets_df = pd.DataFrame(result.json()["results"])
        datasets_df = expand_dict_columns(datasets_df)
        logger.info(f"Fetched {len(datasets_df)} datasets.")
        return datasets_df
        
    except Exception as e:
        logger.error(f"Failed to fetch datasets: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    logger.info("Starting MCP server...")
    mcp.run(host="0.0.0.0", port=9000)