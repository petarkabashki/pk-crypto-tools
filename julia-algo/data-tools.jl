using DelimitedFiles
using Statistics
(data,header)=readdlm("data/csv/BTC_USDT-15m.csv", ',', header=true)

nrows,ncols = size(data)
(t,o,h,l,c) = [data[:,x] for x in 1:ncols]

##############################################
### EMAS

emaNs = [21,50,100]
emaQs = emaNs .|> x-> (2/(1+x))
emaFs = emaQs |> q -> (c, p) -> q*(c-p) + p

emas = emaNs .|> n -> vcat(fill(mean(c[1:n-1]), n-1), [ 0 for i=n:nrows ])

emas = ( ( emaNs .|> n -> (n, (2/(1+n)), mean(c[1:n-1])) ) .|> ((n,q,m),) -> (n,q,m,zeros(nrows)) ) .|> ((n,q,mean,ze),) -> accumulate!( (a,c) -> q*(c-a) + a, ze, c)

##############################################

temas = [[t]; emas]

ptemas = [ [temas[1][i], temas[2][i], temas[3][i], temas[4][i]] for i=1:nrows]

##############################################
### True Range

trueRange = zeros(nrows)
# atr = zeros(nrows)

# (emaslow, emafast, emascalp) = (zeros(Float32, nrows), zeros(Float32, nrows), zeros(Float32, nrows))

# [100,50,21] .|>(x->(2/(1+x)))
