% Creates start and end indexes from signal and l-shifted signal

array[int] of bool: ba_in;
int: df_n = length(ba_in);
set of int: DF_N = 1..df_n;
int: lag_n;

set of DF_N: gba_sig;
set of DF_N: gba_is_beg;
set of DF_N: gba_is_end;
int:spa_n = card(gba_sig);
set of int: SPA_N=1..spa_n;

array[SPA_N] of var gba_is_end: spa_ends;

constraint forall(i in SPA_N)(sum(j in gba_is_beg[i]..spa_ends[i])(ba_in[j]) == );

include "globals.mzn";
% set of int: SPA_N = 1..spa_n;

% constraint spa_n = card(ba_sig_bag);
% array[DF_N] of var DF_N: spa_beg;
% array[DF_N] of var DF_N: spa_end;

% constraint forall(i in spa_n+1..df_n)(spa_beg[i]=df_n /\ spa_end[i]=df_n);
% constraint forall(i in 1..spa_n)(spa_beg[i] in begs_bag);
% constraint strictly_increasing([if i <= spa_n then spa_beg[i] else df_n + i endif | i in DF_N]);
% constraint strictly_increasing([if i <= spa_n then spa_end[i] else df_n + i endif | i in DF_N]);

% constraint forall(i in 1..spa_n)(spa_beg[i] < spa_end[i]);
% array[DF_N] of var bool: span_in;
% constraint forall(i in ba_sig_bag)(forall(j in i - lag_n + 1..i)(span_in[j] = true));
% constraint forall(i in lag_n..df_n)();
% ba_sig_lsh;

solve satisfy;
