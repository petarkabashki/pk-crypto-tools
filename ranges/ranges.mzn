% Use this editor as a MiniZinc scratch book
float: max_diff;
int: Imax_diff = floor(max_diff * 1000);
int: min_rng_n;
array[int] of int : series;
int: series_n = length(series);
set of int: SER_N = 1..series_n;
set of int: SER_N0 = 0..series_n;
int: ser_min = min(series);
int: ser_max = max(series);
set of int: SER_RNG = ser_min..ser_max;
set of int: SER_RNG0 = 0..ser_max;
int: rng_n = series_n div min_rng_n;
set of int: RNG_N = 1..rng_n;


include "globals.mzn";

array[SER_N] of var SER_RNG0: series_fu_min;
array[SER_N] of var SER_RNG0: series_fu_max;
array[SER_N] of var SER_RNG0: series_ba_min;
array[SER_N] of var SER_RNG0: series_ba_max;

constraint forall(i in 1..min_rng_n-1)(series_ba_min[i] = 0 /\ series_ba_max[i] = 0);
constraint forall(i in series_n - min_rng_n + 2..series_n)(series_fu_min[i] = ser_max /\ series_fu_max[i] = ser_min);

constraint forall(i in min_rng_n..series_n)(
    series_ba_min[i] = min(j in i-min_rng_n+1..i)(series[j]) /\
    series_ba_max[i] = max(j in i-min_rng_n+1..i)(series[j])
);

constraint forall(i in 1..(series_n - min_rng_n+1))(
    series_fu_min[i] = min(j in i..i+min_rng_n-1)(series[j]) /\
    series_fu_max[i] = max(j in i..i+min_rng_n-1)(series[j])
);

% output [show(Imax_diff)];
array[SER_N] of var int: series_ba_diff = [if i < min_rng_n then Imax_diff+1 else floor(1000*series_ba_max[i] / series_ba_min[i] - 1000) endif | i in SER_N];
%  = [if i < min_rng_n then Imax_diff+1 else floor(1000*(series_ba_max[i] / series_ba_min[i] - 1)) endif | i in SER_N];
% constraint forall(i in 1..min_rng_n-1)(series_ba_diff[i] = 0);
% constraint forall(i in min_rng_n+1..series_n)(series_ba_diff[i] = floor(1000*(series_fu_max[i] / series_fu_min[i] - 1)));
% array[SER_N] of var int: series_fu_diff = [if i > series_n - min_rng_n + 1 then Imax_diff+1 else floor(1000*(series_fu_max[i] / series_fu_min[i] - 1)) endif | i in SER_N];

% output ["series_fu_diff=", show(series_fu_diff), ";\n", "se?ries_ba_diff=", show(series_ba_diff), ";\n"];
% output [show(series_ba_diff)];

% array[SER_N] of var bool: flar_rng_start;
% array[SER_N] of var bool: flar_rng_end;
% constraint flar_rng_start = [if series_fu_diff[i] <= max_diff then if i > 1 then series_fu_diff[i-1] > max_diff else true endif else false endif | i in SER_N];
% constraint flar_rng_end = [if series_ba_diff[i] <= max_diff then if i < series_n then series_ba_diff[i+1] > max_diff else true endif else false  endif | i in SER_N];


% var set of int: starts_bag = {i | i in SER_N where flar_rng_start[i]};
% var set of int: ends_bag = {i | i in SER_N where flar_rng_end[i]};
% output [show(starts_bag)];

% output [show(ar_rng_start)];
% output [show(sum(ar_rng_start))];

% array[RNG_N] of var SER_N0: ar_rng_start;
% array[RNG_N] of var SER_N0: ar_rng_end;

% var RNG_N: n_ranges;
% constraint n_ranges = sum(flar_rng_start);

% constraint forall(i in 1..n_ranges)(ar_rng_start[i] in starts_bag);
% constraint forall(i in 1..n_ranges)(ar_rng_end[i] in ends_bag);

% constraint forall(i in n_ranges+1..rng_n)(ar_rng_start[i] = 0 /\ ar_rng_end[i] = 0);
% constraint forall(i in 1..n_ranges-1)(ar_rng_start[i] < ar_rng_start[i+1] /\ ar_rng_end[i] < ar_rng_end[i+1]);
% constraint forall(i in 1..n_ranges)(ar_rng_start[i] <= ar_rng_end[i] - min_rng_n + 1);

% constraint disjunctive(ar_rng_start, [if i <= n_ranges then ar_rng_end[i] - ar_rng_start[i] + 1 else 0 endif | i in RNG_N]);

% constraint forall(i in 1..n_ranges)(ar_rng_end[i] >= ar_rng_start[i] + min_rng_n - 1);
% constraint forall(i in 1..n_ranges)(forall(j in ar_rng_start[i]..ar_rng_end[i] - min_rng_n + 1)(series_fu_diff[j] <= max_diff));

solve satisfy;