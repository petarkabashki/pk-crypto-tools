
int: n;
set of int: N = 1..n;

% array[N] of int: lmin;
array[N] of -1..1: entries;
array[N] of int: highs;
array[N] of int: lows;

solve satisfy;