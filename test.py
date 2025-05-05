import logging
import pandas as pd
from auth import get_session
import ace_lib as ace
from helpful_functions import expand_dict_columns  # Optional, if needed inside ace.get_datasets()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def get_datasets() -> pd.DataFrame:
    """
    Retrieve available datasets using an authenticated session.

    Returns:
        pandas.DataFrame: A DataFrame containing information about available datasets.
    """
    session = get_session()
    
    if session is None:
        logger.error("Failed to initialize session.")
        exit(1)

    logger.info(f"Session initialized: {session._instance}")

    try:
        datasets = ace.get_datasets(session)
        logger.info(f"Fetched {len(datasets)} datasets.")
        return datasets
    except Exception as e:
        logger.error(f"Failed to fetch datasets: {e}")
        raise

if __name__ == "__main__":
    logger.info("Initializing session...")
    df = get_datasets()
    print(df.head())
