%%minizinc -m bind

% find troughs between peaks

array[int] of int: mser;
int: sern = length(mser);
set of int: SERN = 1..sern;

array[int] of int: mpeaks;
int: pk_max;
set of int: PK_MAX = 0..pk_max;
int: pkn = length(mpeaks);
set of int: PKN = 1..pkn;

array[1..pkn-1] of var PK_MAX: mtroughs; 
constraint forall(i in 1..pkn-1)(
    mtroughs[i] > mpeaks[i] /\ mtroughs[i] < mpeaks[i+1] 
    /\ forall(j in mpeaks[i]+1..mpeaks[i+1]-1)(mser[j] >= mser[mtroughs[i]])
);


%output [show(sern)];


solve satisfy;