
array[int] of int: series;

int: ser_n;
set of int: SERN = 1..ser_n;

int: swn = ser_n div 5; %ceil(ser_n / (7*1));
set of int: SWN = 1..swn;

include "globals.mzn";
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

int: minspan = 4;
int: minperc = 5;

var SWN: nsn;
% array[SWN,1..2] of var SERN: idxs;
% array[SWN] of var SERN: la;
% array[SWN] of var SERN: ha;
array[1..2, SWN] of var SERN: lha;

% constraint increasing(la);
constraint forall(i in nsn+1..swn, j in 1..2)(lha[j,i] = ser_n);
constraint forall(j in 1..2)(strictly_increasing([if i <= nsn then lha[j,i] else ser_n + i endif | i in SWN]));

constraint forall(i in 1..nsn-1)(lha[2,i] < lha[1,i+1]);
% constraint forall(j in 1..2)(all_different([if i <=nsn then lha[j,i] else swn + i endif | i in SWN]));
constraint disjunctive(lha[1,..], [if i<=nsn then lha[2,i] - lha[1,i] else 0 endif | i in SWN]);
% constraint all_different([ if i <= nsn then ha[i] else ser_n + i endif | i in SERN]);
% constraint all_different([ if i <= nsn then la[i] else ser_n + i endif | i in SERN]);

constraint forall(i in 1..nsn-1)(lha[2,i] + minspan <= lha[1,i+1]);

constraint forall(i in 1..nsn)(forall(j in lha[1,i]..lha[2,i])(series[j] >= series[lha[1,i]]));
constraint forall(i in 1..nsn)(forall(j in lha[1,i]..lha[2,i])(series[j] <= series[lha[2,i]]));

constraint forall(i in 1..lha[1,1])(series[i] <= series[1]);
constraint forall(i in lha[2,nsn]..swn)(series[i] >= series[ser_n]);

% constraint forall(i in 1..nsn)(series[lha[2,i]]/series[lha[1,i]] - 1.0 > 0.05);

constraint forall(i in 1..nsn-1)(forall(j in lha[2,i]..lha[1,i+1])(series[j] <= series[lha[2,i]]));
constraint forall(i in 1..nsn-1)(forall(j in lha[2,i]..lha[1,i+1])(series[j] >= series[lha[1,i+1]]));

% constraint forall(i in 1..nsn)(lha[1,i] + minspan  <= lha[2,i]);
% constraint lha[1,1] = 1 \/ lha[
% constraint lha[1,1] = 1 \/ 
% constraint forall(i in 1..lha[1,1])(series[i] <= series[1]);
%     series[i] <= series[1] /\ series[i] >= series[lha[1,1]]
% );
solve :: seq_search([
             int_search([nsn], dom_w_deg, indomain_random),
             int_search(lha, dom_w_deg, indomain_random)
         ])
% int_search(lha, first_fail, indomain_random, complete)
    satisfy;
%     maximize nsn;
%     minimize lha[1,1] + ser_n - lha[2,nsn];
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% array[SWN] of var SERN: i_1;
% array[SWN] of var SERN: i_2;
% array[SWN] of var SERN: i_3;
% array[SWN] of var SERN: i_4;

% var SWN: nsn;


% constraint disjunctive(i_1, [if i <= nsn then i_3[i] - i_2[i] + 1 else 0 endif | i in SWN]);

% constraint forall(i in 1..nsn-1)(i_3[i] <= i_2[i+1] + 3*minspan);
% constraint strictly_increasing([if i <= nsn then i_1[i] else i + ser_n endif | i in SWN]);
% constraint strictly_increasing([if i <= nsn then i_2[i] else i + ser_n endif | i in SWN]);
% constraint strictly_increasing([if i <= nsn then i_3[i] else i + ser_n endif | i in SWN]);
% constraint strictly_increasing([if i <= nsn then i_4[i] else i + ser_n endif | i in SWN]);

% constraint forall(i in nsn+1..swn)(i_1[i] = ser_n /\ i_2[i] = ser_n /\ i_3[i] = ser_n /\ i_4[i] = ser_n);

% constraint forall(i in 1..nsn)(    
%     i_1[i] >=1 /\ i_2[i] >=1 /\ i_3[i] >=1 /\ i_4[i] >=1 
%     /\ i_1[i] <= ser_n /\ i_2[i] <= ser_n /\ i_3[i] <= ser_n /\ i_4[i] <= ser_n
%     /\ i_1[i] + minspan <= i_2[i] /\ i_2[i] + minspan <= i_3[i] /\ i_3[i] + minspan <= i_4[i] 
%     /\ forall(j in i_1[i]..i_3[i])(series[j] >= series[i_2[i]])
%     /\ forall(j in i_2[i]..i_4[i])(series[j] <= series[i_3[i]])
% );

% constraint forall(i in 1..swn)(increasing([i_1[i], i_2[i], i_3[i], i_4[i]]));

% constraint forall(i in 1..nsn-1)(i_4[i]<i_1[i+1]+ minspan);

% array[1..4] of var int: apktr = [i_1, i_2, i_3];

% include "strictly_increasing.mzn";
% constraint strictly_increasing([0] ++ apktr);


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% var int:obj = sum(i in 1..nsn)(idxs[i,4] - idxs[i,1]);
% solve satisfy;
% solve minimize obj;
% output [show(swlen)];
% var int: obj;
% constraint obj = sum(i in 1..nsn)(i_4[i] - i_1[i]); 
% solve minimize obj;
% solve satisfy;