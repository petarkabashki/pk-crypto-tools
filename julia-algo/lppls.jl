#%%

using Plots
using Optim
using Distributed
using DataFrames
using Dates
using Random
using CSV
using LinearAlgebra


# export LPPLSModel

# export LPPLSModel

mutable struct LPPLSModel
    observations::Array{Float64, 2}
    coef::Dict{Symbol, Float64}
    indicator_result::Array{Any, 1}
end

function LPPLSModel(observations::Array{Float64, 2})
    LPPLSModel(observations, Dict{Symbol, Float64}(), [])
end

function lppls(t, tc, m, w, a, b, c1, c2)
    dt = abs(tc - t) + 1e-8
    return a + dt^m * (b + (c1 * cos(w * log(dt)) + c2 * sin(w * log(dt))))
end

function func_restricted(model::LPPLSModel,x)
    tc, m, w = x
    rM = matrix_equation(model, tc, m, w)
    a, b, c1, c2 = rM[:, 1]
    delta = lppls.(model.observations[1, :], tc, m, w, a, b, c1, c2)
    delta = delta - model.observations[2, :]
    return sum(delta.^2)
end

function matrix_equation(model::LPPLSModel, tc, m, w)
    T = model.observations[1, :]
    P = model.observations[2, :]
    N = length(T)

    dT = abs.(tc .- T) .+ 1e-8
    phase = log.(dT)

    fi = dT.^m
    gi = fi .* cos.(w .* phase)
    hi = fi .* sin.(w .* phase)

    fi_pow_2 = fi.^2
    gi_pow_2 = gi.^2
    hi_pow_2 = hi.^2

    figi = fi .* gi
    fihi = fi .* hi
    gihi = gi .* hi

    yi = P
    yifi = yi .* fi
    yigi = yi .* gi
    yihi = yi .* hi

    matrix_1 = [
        N sum(fi) sum(gi) sum(hi);
        sum(fi) sum(fi_pow_2) sum(figi) sum(fihi);
        sum(gi) sum(figi) sum(gi_pow_2) sum(gihi);
        sum(hi) sum(fihi) sum(gihi) sum(hi_pow_2)
    ]

    matrix_2 = [
        sum(yi);
        sum(yifi);
        sum(yigi);
        sum(yihi)
    ]

    matrix_1 += 1e-8 * I(4)
    return matrix_1 \ matrix_2
end

function estimate_params(model::LPPLSModel, seed, minimizer)
    result = optimize(x -> func_restricted(model, x), seed, minimizer)
    # print(result)
    if Optim.converged(result)
        tc, m, w = Optim.minimizer(result)
        rM = matrix_equation(model, tc, m, w)
        a, b, c1, c2 = rM[:, 1]
        c = sqrt(c1^2 + c2^2)
        model.coef = Dict(:tc => tc, :m => m, :w => w, :a => a, :b => b, :c => c, :c1 => c1, :c2 => c2)
        return tc, m, w, a, b, c, c1, c2
    else
        throw(ArgumentError("Optimization failed"))
    end
end

function fit(model::LPPLSModel, max_searches, minimizer=NelderMead())
    obs === nothing ? model.observations : obs
    search_count = 0

    while search_count < max_searches
        t1 = obs[1, 1]
        t2 = obs[end,1]
        init_limits = [
            (t2 - 0.2 * (t2 - t1), t2 + 0.2 * (t2 - t1)),
            (0.1, 1.0),
            (6.0, 13.0)
        ]

        non_lin_vals = [rand(a[1]:a[2]) for a in init_limits]
        tc, m, w = non_lin_vals
        seed = [tc, m, w]

        try
            return estimate_params(model, seed, minimizer)
        catch
            search_count += 1
        end
    end
    return 0, 0, 0, 0, 0, 0, 0, 0
end

function plot_fit(model::LPPLSModel, show_tc=false)
    tc, m, w, a, b, c, c1, c2 = values(model.coef)
    time_ord = [Dates.Date(Dates.UTM(1970, 1, 1) + Dates.Day(d)) for d in model.observations[1, :]]
    t_obs = model.observations[1, :]
    lppls_fit = [lppls(t, tc, m, w, a, b, c1, c2) for t in t_obs]
    price = model.observations[2, :]

    first = t_obs[1]
    last = t_obs[end]

    O = (w / (2.0 * π)) * log((tc - first) / (tc - last))
    D = (m * abs(b)) / (w * abs(c))

    plot(time_ord, price, label="price", color="black", linewidth=0.75)
    plot!(time_ord, lppls_fit, label="lppls fit", color="blue", alpha=0.5)
    grid!(:both)
    ylabel!("ln(p)")
    legend!(:topright)
end

###########################################

fname = "/media/mu6mula/Data/Quant/pk-crypto-tools/lppls-master/lppls/data/nasdaq_dotcom.csv"
data = DataFrame(CSV.File(fname))

# Convert date strings to ordinal dates and adjust closing prices to logarithms
# time = [Dates.Date(Dates.parse(string(t1), "yyyy-mm-dd")) for t1 in data.Date]
ordinal_time = Dates.value.(data.Date) #[Dates.value(t) for t in time]
price = log.(data."Adj Close")

# Prepare observations
observations = hcat(ordinal_time, price)

# Maximum number of searches as suggested by literature
MAX_SEARCHES = 25

# Create an instance of LPPLSModel
lppls_model = LPPLSModel(observations)

# Fit the model to the data and get back the parameters
tc, m, w, a, b, c, c1, c2 = fit(lppls_model, MAX_SEARCHES)

println("tc: $tc, m: $m, w: $w, a: $a, b: $b, c: $c, c1: $c1, c2: $c2")

# Visualize the fit
plot_fit(lppls_model)