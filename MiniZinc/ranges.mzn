
array[int] of int: brng;

int: sern;
array[1..2] of int: vola;
array[1..2] of int: box;
set of int: SERN = 1..sern;

include "globals.mzn";
array[1..2,SERN] of var SERN: idxs;
var SERN: nsn;

constraint idxs[1,1] > 1;
constraint idxs[1,nsn] < sern;

constraint strictly_increasing([if i <= nsn then idxs[1,i] else sern + i endif | i in SERN]);
constraint forall(i in 1..nsn)(brng[idxs[1,i]] != brng[idxs[1,i]+idxs[2,i]+1]);
constraint forall(i in 1..nsn)(idxs[2,i] >= box[1]);
constraint forall(i in 1..nsn)(brng[idxs[1,i]] >= vola[1] /\ brng[idxs[1,i]] <= vola[2]);
constraint forall(i in 1..nsn)(forall(j in idxs[1,i]..idxs[1,i]+idxs[2,i])(brng[i] = brng[idxs[1,i]]));
constraint disjunctive(idxs[1,..], [if i <= nsn then idxs[2,i] else 0 endif | i in SERN]);

var int: obj = sum(i in 1..nsn)(idxs[2,i]);

solve :: seq_search([
             int_search([nsn], dom_w_deg, indomain_random),
         ]) maximize obj;