import subprocess
import shlex
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os

mcp = FastMCP("Freqtrade Data Downloader")

@mcp.tool()
def freqtrade_download_data(userdir: str = None, exchange: str = "binance", timeframes: str = None, pairs: str = None) -> str:
    """
    Downloads historical data for trading pairs using Freqtrade.

    Args:
        userdir: Path to the Freqtrade user data directory (e.g., ./freq-user-data). If not provided, it will be loaded from the .env file.
        exchange: The exchange to download data from (e.g., binance). Defaults to "kucoin".
        timeframes: List of timeframes to download (e.g., ["3d", "1d", "1h"]). If not provided, it will be loaded from the .env file.
        pairs: List of trading pairs to download data for (e.g., ["BTC/USDT", "ETH/USDT"]). If not provided, it will be loaded from the .env file.

    Returns:
        The output of the freqtrade download-data command as a string.
    """
    load_dotenv()  # Load environment variables from .env file

    if userdir is None:
        userdir = os.getenv('USERDIR', './freq-user-data')
    if timeframes is None:
        timeframes = os.getenv('TIMEFRAMES', '1d')
    timeframes = timeframes.split()
    if pairs is None:
        pairs = os.getenv('PAIRS', 'BTC/USDT ETH/USDT')
    pairs = pairs.split()

    timeframes_arg = " ".join(timeframes)
    pairs_arg = " ".join(pairs)

    command = f"freqtrade download-data --userdir {userdir} --data-format-ohlcv json --exchange {exchange} -t {timeframes_arg} --timerange=20200101-  -p {pairs_arg}"

    try:
        process_output = subprocess.run(
            shlex.split(command),  # Use shlex.split for safe command execution
            capture_output=True,
            text=True,  # Decode output as text
            check=True  # Raise an exception for non-zero exit codes
        )
        output = process_output.stdout
        error_output = process_output.stderr
        if error_output:
            output += f"\n\nERROR OUTPUT:\n{error_output}" # Append error output to the main output

        return f"Command executed successfully:\n\n{command}\n\nOutput:\n{output}"

    except subprocess.CalledProcessError as e:
        return f"Command failed with exit code {e.returncode}:\n\n{command}\n\nError Output:\n{e.stderr}\n\nStandard Output:\n{e.stdout}"
    except FileNotFoundError:
        return "Error: freqtrade command not found. Please ensure Freqtrade is installed and in your PATH."
    except Exception as e:
        return f"An unexpected error occurred:\n\n{str(e)}"

if __name__ == "__main__":
    mcp.run()