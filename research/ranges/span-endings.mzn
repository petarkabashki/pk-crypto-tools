
array[int] of int: i_spa_sigs;
int: sigs_n = length(i_spa_sigs);
set of int: SIGS_N = 1..sigs_n;
array[SIGS_N] of int: spa_mins;
array[SIGS_N] of int: spa_maxs;

array[int] of int: closes;
int: cln = length(closes);
set of int: CLN = 1..cln;
array[CLN] of int: ba_mins;
array[CLN] of int: ba_maxs;
array[CLN] of int: min_to_end;
array[CLN] of int: max_to_end;
int: cmin;
int: cmax;
set of int: C_RNG = cmin..cmax;

array[SIGS_N] of var CLN: i_lo_ends;
array[SIGS_N] of var CLN: i_hi_ends;


array[SIGS_N] of var C_RNG: lo_fu_mins;
array[SIGS_N] of var C_RNG: hi_fu_maxs;

constraint forall(i in SIGS_N)(lo_fu_mins[i] = min_to_end[i_lo_ends[i]]);
constraint forall(i in SIGS_N)(hi_fu_maxs[i] = max_to_end[i_hi_ends[i]]);

constraint forall(i in SIGS_N)(i_lo_ends[i] >= i_spa_sigs[i] /\ i_hi_ends[i] >= i_spa_sigs[i]);

constraint forall(i in SIGS_N)(forall(j in i_spa_sigs[i]..i_hi_ends[i])(closes[j] <= spa_maxs[i] ));
constraint forall(i in SIGS_N)(forall(j in i_spa_sigs[i]..i_lo_ends[i])(closes[j] >= spa_mins[i] ));

constraint forall(i in SIGS_N)(min_to_end[i_lo_ends[i]] < spa_mins[i]);
% constraint forall(i in SIGS_N)(spa_maxs[i] <= max_to_end[i_hi_ends[i]]);

%     /\ if i_spa_ends[i]+1 > sigs_n then false else (closes[i_spa_ends[i]+1] > spa_maxs[i] \/ closes[i_spa_ends[i]+1] < spa_mins[i]) endif


% constraint forall(i in 1..sigs_n)(max_to_end[i_hi_ends[i]] > spa_maxs[i]);
% constraint forall(i in 1..sigs_n)(min_to_end[i_lo_ends[i]] < spa_mins[i]);
% i_lo_ends[i] = sigs_n 
% constraint forall(i in 1..sigs_n)(min_to_end[i_spa_sigs[i]] <= closes[i_spa_sigs[i]] -> closes[i_lo_ends[i]+1] <     spa_mins[i]);
% constraint 

% constraint i_spa_ends[i]+1 > sigs_n ->
% i_spa_ends[i]+1 > sigs_n \/ 
% output [show(i_spa_ends)];
% var int: obj = sum(i in SIGS_N)(i_spa_ends[i]-i_spa_sigs[i]);
% solve maximize obj;
solve satisfy;