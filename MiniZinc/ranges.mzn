
int: nfl;
int: nst = nfl;
int: bmin;
int: bmax;

set of int: NFL = 1..nfl;
set of int: NST = 1..nst;

set of int: FLAG = 0..1;
array[NFL] of FLAG: flags;
% array[NFL] of NFL: rstart;

include "globals.mzn";
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% int: nfl = 10;
% int: nst = 2;
% set of int: NFL = 1..nfl;
% set of int: NST = 1..nst;

% set of int: FLAG = 0..1;
% array[NFL] of FLAG: ser = [0,0,1,1,1,1,1,0,0,1];
% array[NST] of NFL: start = [3,10];

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% var set of NFL: ra = {i | i in NFL where flags[i] = 1 /\ (i = 1 \/ flags[i-1] = 0) /\ bigenough(i)};

% output [show(ra)];
array[NFL] of var 0..nst: cum;
constraint forall(i in NFL)(flags[i] = 0 -> cum[i] = 0);
constraint forall(i in NFL where flags[i] = 1 /\ (i = 1 \/ flags[i-1] = 0))(cum[i] = 1);
constraint forall(i in NFL where flags[i] = 1 /\ i > 1 /\ flags[i-1] = 1)(cum[i] = 1 + cum[i-1]);

var set of NFL: srstart = {i | i in NFL where cum[i] = 1 /\ (i = 1 \/ cum[i-1] = 0)};
var set of NFL: srend = {i | i in NFL where cum[i] >= 1 /\ (i = nfl \/ cum[i+1] = 0)};

% output [show(srstart), show(srend)];
var NST: nsn = card(srstart);

predicate map_set_2_array(var set of NFL: ss, array[NST] of var 0..nfl: aa) =
    forall(i in nsn+1..nst)(aa[i] = 0) /\
    forall(s in ss)(exists(j in 1..nsn)(aa[j] = s)) /\
    strictly_increasing([if i <= nsn then aa[i] else nfl + i endif | i in NST]);

% array[int] of var int: rstart = [s | s in srstart];
array[1..2] of var set of int: sres = [srstart, srend];
output ["sres=\(sres)"];



% array[NST] of var 0..nst: rstart;
% array[NST] of var 0..nst: rend;
% constraint map_set_2_array(srstart, rstart);
% constraint map_set_2_array(srend, rend);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
solve satisfy;
