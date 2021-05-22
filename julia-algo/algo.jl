
#########################################
# Load data
using Pipe
using MarketTechnicals
using Plots
using PlotThemes
# using TimeSeries
using DataFrames
using StatsPlots
using CSV

theme(:dark)
gr()

ta = readtimearray("data/csv/BTCUSDT-15m.csv", format="yyyy-mm-dd HH:MM", delim=',', meta=nothing)

taf = @pipe ta |> from(_, DateTime(2021, 1, 1)) |> to(_, DateTime(2021, 4, 1)) 

# taf
ema21, ema50 = ema(taf.close, 21), ema(taf.close, 50)
ema100, ema200 = ema(taf.close, 100), ema(taf.close, 200)

# vema21, vema50 = values(ema21), values(ema50)
# vema100, vema200 = values(ema100), values(ema200)

df = innerjoin(DataFrame(taf), DataFrame(ema21),DataFrame(ema50), DataFrame(ema100), DataFrame(ema200),  on=:timestamp)

transform!(df, :, [:close_ema_21,:close_ema_50] => ByRow((x,y) -> 1000*log(x/y)) => :q_ema_21_50_log)
transform!(df, :, [:close_ema_50,:close_ema_100] => ByRow((x,y) -> 1000*log(x/y)) => :q_ema_50_100_log)
transform!(df, :, [:close_ema_100,:close_ema_200] => ByRow((x,y) -> 1000*log(x/y)) => :q_ema_100_200_log)


transform!(df, :, [:close,:close_ema_21] => ByRow((x,y) -> 1000*log(x/y)) => :q_close_ema_21_log)
transform!(df, :, [:close,:close_ema_50] => ByRow((x,y) -> 1000*log(x/y)) => :q_close_ema_50_log)
transform!(df, :, [:close,:close_ema_100] => ByRow((x,y) -> 1000*log(x/y)) => :q_close_ema_100_log)
transform!(df, :, [:close,:close_ema_200] => ByRow((x,y) -> 1000*log(x/y)) => :q_close_ema_200_log)

# rename!(taf, [:Open, :High, :Low, :Close, :Volume])
gr()
pl = plot(timestamp(taf), values(taf.close), lw=0.2, size=(1800,400), xrotation = 60 , xticks=false)
plot!(ema21.close_ema_21, lw=0.2)
plot!(ema50.close_ema_50, lw=0.2)
plot!(ema100.close_ema_100, lw=0.2)
plot!(ema200.close_ema_200, lw=0.2)

pl1 = @df df plot(:timestamp, [:ema_21_50_log, :ema_50_100_log, :ema_100_200_log], lw=0.2)

pl2 = @df df plot(:timestamp, [:ema_close_50_log, :ema_close_100_log, :ema_close_200_log], lw=0.2)
# plot!(0)
# pl1 = plot(df.timestamp, df.ema_21_50_log, df.ema_50_100_log, df.ema_100_200_log)
plot(pl, pl1, pl2, layout=(3,1), dpi=600, lw=0.2)    

# pl1 = plot(ema200.close_ema_200, lw=0.5)
savefig("plot.png")
# gui()


#########################################


dtrf = DataFrame(timestamp=DateTime[], 
reason=String[],
buy=Float32[],
sell=Float32[],
price=Float32[], 
profit=Float32[],
capital=Float32[]
)


# df[1:5,:]
capital, riskPercent = 100., 0.01
isLong, priceIn, priceOut, buySize, profit, stopLoss  = false, 0, 0, 0, 0, 0 
feePercent, stopLossReason = 0.001, "SL"

for r in eachrow(df)
    if isLong
        priceOut = r.close * (1 - feePercent)
        profit = buySize * (priceOut - priceIn)
        if r.close < stopLoss # close SL
            capital += profit
            isLong = false
            push!(dtrf, (r.timestamp, stopLossReason, 0, buySize, priceout, profit, capital))
        elseif r.close > priceIn * (1 + 0.05)
            capital += profit
            isLong = false
            push!(dtrf, (r.timestamp, "TH", 0, buySize, priceOut, profit, capital))
        elseif r.close > priceIn * (1 + 0.005)
        end
    else #not in pos
        if r.q_close_ema_21_log < -10 && r.q_ema_21_50_log > 5
            isLong = true
            position = capital * riskPercent
            priceIn = r.close * (1 + feePercent)
            stopLoss = r.close * (1 - 0.03)
            buySize = position / (priceIn - stopLoss)
            println("priceIn: ", priceIn)
            println("stoploss: ", stopLoss)
            println("buySize: ", buySize)
            
            push!(dtrf, (r.timestamp, "LONG", buySize, 0, priceIn, 0, capital))
            slrsn = "SL"
        end
    end
    # push!(dtrf, (r.timestamp, pricein, priceout, sizep, capt, islong))
end

CSV.write("trades.csv", dtrf)
plot(dtrf.capital)

combine(groupby(dtrf, [:reason]), nrow => :count)

trf = TimeArray(dtrf, timestamp = :timestamp)

filter(r -> r.rsn =="", dtrf)

savefig("plot.png")

@df trf plot()
@df dtrf plot(:timestamp, [:capital], lw=2)

df[df.q_ema_50_100_log .> 10, :]
df[(df.q_close_ema_50_log .< 0) .& (df.q_ema_50_100_log .> 10) , :]

trf

trf[:,:]

#########################################
