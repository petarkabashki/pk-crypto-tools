#!/bin/bash

# To run this script, navigate to the directory where you saved it in your terminal,
# ensure it has execute permissions (chmod +x download-data.sh), and then run it using:
# ./download-data.sh

# Script to download freqtrade data for multiple pairs and timeframes.

# --- Configuration ---
USERDIR="./.freqtrade"  # Replace with your freqtrade user directory
DATADIR="./data"   # Data directory
CONFIG_FILE="--config $USERDIR/config.json"  # Optional: Specify a config file
EXCHANGE="binance"           # Default exchange
DEFAULT_FORMAT="json"        # Default data format
DEFAULT_PAIR="BTC"           # Default base asset
DEFAULT_QUOTE="USDT"
DEFAULT_TIMEFRAME="1w"      # Default timeframe

# --- Input Validation and Usage ---

usage() {
    echo "Usage: $0 [-p <pair1,pair2,...> -t <timeframe1,timeframe2,...> -s <start_date> -e <end_date> -x <exchange> -f <format> -c <config_file> -q <quote_asset>]"
    echo "       -p, --pairs       (Optional) Comma-separated list of trading pairs (e.g., BTC/USDT,ETH/USDT). Defaults to BTC."
    echo "       -t, --timeframes  (Optional) Comma-separated list of timeframes (e.g., 5m,1h,1d). Defaults to 1w."
    echo "       -s, --start       (Optional) Start date for timerange (YYYYMMDD format).  Defaults to last year's start."
    echo "       -e, --end         (Optional) End date for timerange (YYYYMMDD format). Defaults to now."
    echo "       -x, --exchange    (Optional) Exchange name. Defaults to 'binance'."
    echo "       -f, --format      (Optional) Data format (json, csv, hdf5). Defaults to 'json'."
    echo "       -c, --config      (Optional) Path to a custom configuration file."
    echo "       -q, --quote       (Optional) Quote asset (e.g., USDT, BUSD). Defaults to 'USDT'."
    exit 1
}

# --- Default Values ---
CURRENT_YEAR=$(date +%Y)
LAST_YEAR=$((CURRENT_YEAR - 1))
DEFAULT_START_DATE="${LAST_YEAR}0101"  # Start of last year
DEFAULT_END_DATE=$(date +%Y%m%d)      # Current date

# --- Parse command-line arguments ---
START_DATE="$DEFAULT_START_DATE"
END_DATE="$DEFAULT_END_DATE"
DATA_FORMAT="$DEFAULT_FORMAT"
PAIRS="$DEFAULT_PAIR"          # Default to BTC
TIMEFRAMES="$DEFAULT_TIMEFRAME"  # Default to 1w
QUOTE_ASSET="$DEFAULT_QUOTE"
CUSTOM_CONFIG="--prepend"

while getopts ":p:t:s:e:x:f:c:q:" opt; do
    case $opt in
        p)
            PAIRS="$OPTARG"
            ;;
        t)
            TIMEFRAMES="$OPTARG"
            ;;
        s)
            START_DATE="$OPTARG"
            ;;
        e)
            END_DATE="$OPTARG"
            ;;
        x)
            EXCHANGE="$OPTARG"
            ;;
        f)
            DATA_FORMAT="$OPTARG"
            ;;
        c)
            CUSTOM_CONFIG="--config $OPTARG"
            ;;
        q)
            QUOTE_ASSET="$OPTARG"
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            usage
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            usage
            ;;
    esac
done

# --- Data Download Loop ---
# set -x # Enable script tracing - to show each command

# Handle pairs - if default, use "BTC/USDT", otherwise process comma-separated string
if [ "$PAIRS" = "$DEFAULT_PAIR" ]; then
    PAIR_STRING="$DEFAULT_PAIR/$QUOTE_ASSET"
else
    PAIR_STRING="$PAIRS"
fi

# Process pairs - append default quote if no quote is provided in PAIRS
IFS=','
read -r -a PAIR_LIST_TEMP <<< "$PAIR_STRING"
PAIR_STRING_WITH_QUOTE=""
FIRST_PAIR=true
for pair_temp in "${PAIR_LIST_TEMP[@]}"; do
    if [[ "$pair_temp" != */* ]]; then # Check if pair already has "/"
        pair_with_quote="${pair_temp^^}/$QUOTE_ASSET" # Append quote asset and uppercase base
    else
        pair_with_quote="$pair_temp" # Use as provided
    fi
    if $FIRST_PAIR; then
        PAIR_STRING_WITH_QUOTE="$pair_with_quote"
        FIRST_PAIR=false
    else
        PAIR_STRING_WITH_QUOTE="$PAIR_STRING_WITH_QUOTE,$pair_with_quote"
    fi
done
PAIR_STRING="$PAIR_STRING_WITH_QUOTE"

# Process timeframes into positional parameters
IFS=',' set -- $TIMEFRAMES
TIMEFRAME_ARGS="$@"


echo "Downloading data for pairs: $PAIR_STRING"
echo "Downloading data for timeframes: $TIMEFRAMES"
echo "Using exchange: $EXCHANGE"
echo "Using data format: $DATA_FORMAT"
echo "Using timerange: $START_DATE-$END_DATE"

# Construct the timerange argument
TIMERANGE="--timerange=$START_DATE-$END_DATE"

# Build the common arguments part of the command.
COMMON_ARGS=(
    --userdir "$USERDIR"
    --datadir "$DATADIR"
    $CUSTOM_CONFIG
    --exchange "$EXCHANGE"
    --data-format-ohlcv "$DATA_FORMAT"
)


# Iterate through timeframes (using positional parameters)
for timeframe in $TIMEFRAME_ARGS; do
    # Iterate through pairs (handling comma-separated string)
    IFS=','
    read -r -a PAIR_LIST <<< "$PAIR_STRING"
    for pair in "${PAIR_LIST[@]}"; do
        echo "Downloading data for pair: $pair, timeframe: $timeframe"

        CURRENT_PAIR="$pair" # Use pair from loop - no longer hardcoded

        # Construct and execute the freqtrade command.
        COMMAND=(freqtrade download-data
            "${COMMON_ARGS[@]}"  # Add the common arguments
            --pairs "$CURRENT_PAIR" # Use pair from loop
            # -vvv # Add verbose logging for debugging
            --timeframes "$timeframe"
            $TIMERANGE
        )
        # Execute the command and capture output and exit code
        OUTPUT=$("${COMMAND[@]}" 2>&1)  # Capture both stdout and stderr
        EXIT_CODE=$?

        # Print the output and check for success
        echo "$OUTPUT"
        if [ $EXIT_CODE -ne 0 ]; then
            echo "Error downloading data for pair: $pair, timeframe: $timeframe" >&2
            # Consider whether to exit or continue here
        else
            echo "Successfully downloaded data for pair: $pair, timeframe: $timeframe"
        fi
    done
done

echo "Data download process completed."
echo "IMPORTANT: Please check the output above for any FREQTRADE ERRORS or WARNINGS!"
exit 0
