# candles_functions.jl
using CSV
using DataFrames
using Dates
using Printf
using JSON

function load_json_candles(fname::String)
    # Parse the JSON file into an array of arrays
    raw_data = JSON.parsefile(fname)
    
    # Check if raw_data is an array of arrays
    if isa(raw_data, Vector{Vector{Any}})
        # Convert array of arrays to DataFrame, and assign column names
        data = DataFrame(raw_data, [:timestamp, :open, :high, :low, :close, :volume])
    else
        error("Unexpected JSON structure. Expected an array of arrays.")
    end
    
    # Convert the timestamp from milliseconds to DateTime
    data.timestamp = Dates.unix2datetime.(data.timestamp ./ 1000)
    
    # Set the timestamp column as the index (optional)
    data = setindex!(data, data.timestamp, :timestamp)
    
    return data
end


function json_fname(exchange::String, base::String, qote::String, timeframe::String)
    fname = "/media/mu6mula/Data/Crypto-Data-Feed/freq-user-data/data/$exchange/$(base)_$(qote)-$timeframe.json"
    return fname
end

# Function to load candles
function load_candles(exchange::String, base::String, qote::String, timeframe::String)
    fname = "/media/mu6mula/Data/Crypto-Data-Feed/freq-user-data/data/$exchange/$(base)_$(qote)-$timeframe.json"
    return load_json_candles(fname)
end

# Function to load futures candles
function load_futures_candles(exchange::String, base::String, qote::String, timeframe::String)
    fname = "/media/mu6mula/Data/Crypto-Data-Feed/freq-user-data/data/$exchange/futures/$(base)_$(qote)_$(qote)-$timeframe-futures.json"
    return load_json_candles(fname)
end

# Function to load local candles from CSV
function load_local_candles(data_dir::String, fname::String)
    full_fname = "$data_dir/$fname.csv"
    data = DataFrame(CSV.File(full_fname))
    data.Date = DateTime.(data.Date)  # Convert string to DateTime
    rename!(names(data), lowercase∘string)  # Make all column names lowercase
    data = setindex!(data, data.Date, :date)
    return data
end

# Function to load index candles
function load_index_candles(ticker::String)
    fname = "/media/mu6mula/Data/Crypto-Data-Feed/indexes-data/$ticker.csv"
    data = DataFrame(CSV.File(fname))
    data.Date = DateTime.(data.Date)  # Convert string to DateTime
    rename!(names(data), lowercase∘string)  # Make all column names lowercase
    data = setindex!(data, data.Date, :date)
    return data
end

# Function to load SP500 stock candles
function load_sp500_stock_candles(ticker::String)
    fname = "/media/mu6mula/Data/Crypto-Data-Feed/sp500_data/$ticker.csv"
    data = DataFrame(CSV.File(fname))
    data.Date = DateTime.(data.Date)  # Convert string to DateTime
    rename!(names(data), lowercase∘string)  # Make all column names lowercase
    data = setindex!(data, data.Date, :date)
    return data
end

# Function to load Russel 2000 candles
function load_russel2000_candles(ticker::String)
    fname = "/media/mu6mula/Data/Crypto-Data-Feed/russell_2000_data/$ticker.csv"
    data = DataFrame(CSV.File(fname))
    data.Date = DateTime.(data.Date)  # Convert string to DateTime
    rename!(names(data), lowercase∘string)  # Make all column names lowercase
    data = setindex!(data, data.Date, :date)
    return data
end

# function print_table(pairs::Vector{Tuple{String, Any}}, num_columns::Int = 4)
#     # Calculate the maximum width for each column based on the titles and values
#     max_width = maximum([length(title) for (title, _) in pairs])
    
#     # Increase the max_width if any value is longer than the titles
#     max_value_width = maximum([length(string(value)) for (_, value) in pairs])
#     max_width = max(max_width, max_value_width)
    
#     # Define the format for the columns
#     column_format = "%-" * string(max_width) * "s : %-" * string(max_width) * "s  "

#     # Loop through the pairs and print them in a table format
#     for (i, (title, value)) in enumerate(pairs)
#         if i % num_columns == 1 && i != 1
#             println()
#         end
#         # Print the title-value pair with the proper format
#         @printf(column_format, title, string(value))
#     end

#     # Print a final newline to ensure proper formatting
#     println()
# end
