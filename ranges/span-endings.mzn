
array[int] of int: i_spa_sigs;
int: sigs_n = length(i_spa_sigs);
set of int: SIGS_N = 1..sigs_n;
array[SIGS_N] of int: spa_mins;
array[SIGS_N] of int: spa_maxs;

array[int] of int: closes;
int: cln = length(closes);
set of int: CLN = 1..cln;

array[SIGS_N] of var CLN: i_spa_ends;

constraint forall(i in SIGS_N)(i_spa_ends[i] >= i_spa_sigs[i]);
constraint forall(i in SIGS_N)(
    forall(j in i_spa_sigs[i]..i_spa_ends[i])(closes[j] <= spa_maxs[i] /\ closes[j] >= spa_mins[i])
    /\ (i_spa_ends[i]+1 > sigs_n \/ closes[i_spa_ends[i]+1] > spa_maxs[i] \/ closes[i_spa_ends[i]+1] < spa_mins[i])
);

% output [show(i_spa_ends)];

solve satisfy;