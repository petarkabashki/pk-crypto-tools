
array[int] of int: kl_open;
array[int] of int: kl_high;
array[int] of int: kl_low;
array[int] of int: kl_close;

int: kl_n = length(kl_open);

% set of int: UPDN = {1,-1};

% array[1..kl_n] of var UPDN: kl_d;
% array[1..kl_n] of var int: kl_a;
% array[1..kl_n] of var int: kl_b;
% array[1..kl_n] of var int: kl_pk;
% array[1..kl_n] of var int: kl_tr;

% constraint kl_a[1] = kl_close[1];
% constraint kl_b[1] = kl_close[1];
% constraint kl_pk[1] = 1;
% constraint kl_tr[1] = 1;

% set of int: NPEAKS = 1..kl_n ;
% set of int: NPEAKS0 = 0..kl_n div 2;
var 1..kl_n: npeaks;
array[1..kl_n] of var 1..kl_n: apeaks;

% constraint %trace("apeaks0[0] = if \(kl_close[2]) > \(kl_close[1]) then 2 else 1 endif\n",
%     apeaks0[0] = if kl_close[2] > kl_close[1] then 2 else 1 endif;

constraint apeaks[1] = 1;
% include "arg_max.mzn";
% include "arg_min.mzn";
constraint forall(i in 1..npeaks-2)(
%     let {int: j = i*2} in
%       maximum_arg([kl_close[j] | j in apeaks0[i-1]..apeaks0[i+1]], i) %/\
%       minimum_arg([kl_close[j] | j in i..i+2], i)
    apeaks[i] > 0 -> 
        (
            forall(k in apeaks[i]..apeaks[i+1])(
                    kl_close[k] <= kl_close[apeaks[i]] /\
                    kl_close[k] >= kl_close[apeaks[i+1]]
            )
            /\
            forall(k in apeaks[i+1]..apeaks[i+2])(
                    kl_close[k] >= kl_close[apeaks[i+1]] /\
                    kl_close[k] <= kl_close[apeaks[i+2]]
            )
        )
);

constraint sum(i in 1..npeaks-1)(apeaks[i] = 1 \/ apeaks[i] = kl_n) = 2;
% constraint forall(i in 1..(npeaks div 2) - 1)(
%     let {int: j = i*2} in
%     forall(k in apeaks0[j]+1..apeaks0[j+1]-1)(
%         kl_close[k] <= kl_close[apeaks0[j]] /\ kl_close[k] >= kl_close[apeaks0[j+1]]
%     )
% );

% array[NPEAKS0] of var NPEAKS: atroughs;
% constraint apeaks[1] = 1;
% constraint atroughs[1] = 1;

constraint sum(i in 1..npeaks)(apeaks[i] < 1 \/ apeaks[i] > kl_n ) <= npeaks; 
% include "alldifferent.mzn";
% array[int] of var 1..kl_n :fapeaks;

% constraint all_different_except_0([apeaks0[i] | i in 1..npeaks]);
% constraint all_different_except_0(atroughs);

constraint forall(i in npeaks+1..kl_n)(apeaks[i] = kl_n+1);
include "strictly_increasing.mzn";
constraint strictly_increasing(apeaks);
% constraint increasing(atroughs);

% include "global_cardinality";
% constraint forall(i in 1..npeaks-1)(
%     forall(j in apeaks0[i]+1..apeaks0[i+1]-1)(kl_close[j] <= kl_close[i] /\ kl_close[j] <= kl_close[i+1])
%     );

% constraint forall(i in 1..npeaks-1)(
%     forall(j in atroughs[i]+1..atroughs[i+1]-1)(kl_close[j] >= kl_close[i] /\ kl_close[j] >= kl_close[i+1])
%     );

% constraint forall(i in 2..kl_n)(
%     kl_d[i] = 1 ->
%     (kl_close[i] < kl_close[i-1] /\ ) \/
%     () );
    
% constraint kl_d[1] = (kl_close[2] > kl_close[1])*2 - 1;


% constraint forall(i in 2..kl_n)(
%     kl_d[i] = 1 ->
%     (kl_close[i] < kl_close[i-1] /\ ) \/
%     () );
    

% var int: peaksn;
% array[1..kl_n] of var set of 1..kl_n: peaks;
% constraint peaks[1] = 1;

% constraint forall(i in 1..kl_n-1)(
%     forall(j in peaks[i]+1..peaks[i+1]-1)(kl_close[j] < max(peaks[i], peaks[i+1])));

solve satisfy;

% solve minimize npeaks;
