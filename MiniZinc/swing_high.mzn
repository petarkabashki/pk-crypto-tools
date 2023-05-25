
array[int] of int: kl_close;

int: kl_n;
set of int: KLN = 1..kl_n;
int: inow;
var int: i_1;
var int: i_2;
var int: i_3;

array[1..4] of var int: apktr = [i_1, i_2, i_3, inow];

include "strictly_increasing.mzn";
constraint strictly_increasing([0] ++ apktr);

include "globals.mzn";

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


constraint forall(k in apktr) (k >= 1 /\ k <= kl_n);
constraint forall(i in 1..3)(apktr[i+1] - apktr[i] > 3 * 7 * 2);
include "strictly_increasing.mzn";
constraint strictly_increasing([0,i_1,i_2,i_3,inow]);
include "all_different.mzn";
% constraint forall(i in ipeak_1+1..itrough_0-1)(kl_close[i] < kl_close[ipeak_1]); % kl_close[i] >= kl_close[itrough_0]); % /\ );
% constraint forall(i in itrough_0+1..ipeak_0-1)(kl_close[i] >= kl_close[itrough_0]  ); %  /\ kl_close[i] <= kl_close[ipeak_0]
% constraint forall(i in ipeak_0+1..inow)(kl_close[i] < kl_close[ipeak_0]);
% constraint kl_close[i_3] >= kl_close[i_1];
constraint forall(i in i_2..inow)(kl_close[i] <= kl_close[i_3]);
constraint forall(i in i_1..i_3)(kl_close[i] >= kl_close[i_2]);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
var int: obj;
constraint obj = inow - i_1; 


solve minimize obj;