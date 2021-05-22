
######################################################
## Loads csvs into JuliaDB
using Glob
using JSON
using CSV
using Tables
using DataFrames

json_dir = "src/freqtrade/user_data/data/binance"
json_filefile_paths = glob("$json_dir/*") 
json_files = map(f -> replace(f, "$json_dir/"=>""),json_filefile_paths)
# json_filename  = json_files[1]
json_filename = "BTC-12h.json"
json_files[1]
json_data = JSON.parsefile("$json_dir/$()")
json_data[:,2] = Float64(json_data[:,2])
json_data
json_data[:,2]
# jtable = jsontable(json_data)

# loadtable(json_files[1])

df = DataFrame(json_data)
df
rename!(df, :x1 => :time, :x2 => :open, :x3 => :high, :x4 => :low, :x5 => :close, :x6 => :volume  )
df = df[:, [:time, :open, :high, :low, :close, :volume]]

table = Arrow.Table(df)

df[3,:open]
Arrow.write("klines.arrow", df)
# dirname(pwd())
a=1

######################################################



######################################################



######################################################



######################################################



######################################################



######################################################



######################################################



######################################################



######################################################



######################################################



######################################################



######################################################



