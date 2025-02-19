# MCP Server for Freqtrade

This MCP server provides tools for downloading cryptocurrency trading data using Freqtrade.

## Tools

### freqtrade_download_data

Downloads crypto price data using Freqtrade.

**Parameters:**

- `userdir` (optional): Freqtrade user directory. Defaults to the value set in the environment variable `FREQTRADE_USER_DIR`.
- `exchange` (optional): The exchange to use. Defaults to "binance".
- `timeframes` (optional): List of timeframes (e.g., ["1h", "4h", "1d"]). Defaults to the value set in the environment variable `FREQTRADE_TIMEFRAMES`.
- `pairs` (optional): List of trading pairs (e.g., ["BTC/USDT", "ETH/USDT"]). Defaults to the value set in the environment variable `FREQTRADE_PAIRS`.

**Returns:**

A string indicating the status of the data download.

## Environment Variables

- `FREQTRADE_USER_DIR`: The default user directory for Freqtrade.
- `FREQTRADE_TIMEFRAMES`: The default timeframes for data download.
- `FREQTRADE_PAIRS`: The default trading pairs for data download.

## Usage

To use this MCP server, you need to have Freqtrade installed and configured. Set the required environment variables in your `.env` file or directly in your environment.

### Example

```bash
export FREQTRADE_USER_DIR="/path/to/freqtrade/user/data"
export FREQTRADE_TIMEFRAMES="1h,4h,1d"
export FREQTRADE_PAIRS="BTC/USDT,ETH/USDT"
```

Then, you can use the `freqtrade_download_data` tool to download data:

```python
from mcp_tool import use_mcp_tool

result = use_mcp_tool(
    server_name="freqtrade-server",
    tool_name="freqtrade_download_data",
    arguments={
        "userdir": "/path/to/freqtrade/user/data",
        "exchange": "binance",
        "timeframes": ["1h", "4h", "1d"],
        "pairs": ["BTC/USDT", "ETH/USDT"]
    }
)

print(result)
```

This will download the specified data and return the status.

## MCP COnfiguration for Cline/RooCode:

```
    "freqtrade_download_data": {
      "command": "uv",
      "args": [
        "--directory",
        "/media/mu6mula/Data1/Quant/pk-crypto-tools/2025/mcp-servers/mcp-server-freqtrade",
        "run",
        "freqtrade-downloader.py"
      ],
      "disabled": false,
      "alwaysAllow": []
    },
```