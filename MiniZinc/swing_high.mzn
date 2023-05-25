
array[int] of int: kl_close;

int: kl_n;
set of int: KLN = 1..kl_n;
int: inow;
var int: ipeak_0;
var int: ipeak_1;
var int: itrough_0;

array[1..4] of var int: apktr = [ipeak_1, itrough_0, ipeak_0, inow];

constraint forall(k in apktr) (k >= 1 /\ k <= kl_n);
constraint forall(i in 1..3)(apktr[i+1] - apktr[i] > 3 * 7 * 2);
include "increasing.mzn";
constraint increasing([ipeak_1, itrough_0, ipeak_0]);
include "all_different.mzn";
constraint all_different([ipeak_1, itrough_0, ipeak_0]);
constraint forall(i in itrough_0..ipeak_0)(kl_close[i] >= kl_close[itrough_0] /\ kl_close[i] <= kl_close[ipeak_0]);
constraint forall(i in ipeak_1..itrough_0)(kl_close[i] >= kl_close[itrough_0] /\ kl_close[i] <= kl_close[ipeak_1]);
constraint forall(i in ipeak_0..inow)(kl_close[i] <= kl_close[ipeak_0]);
constraint kl_close[ipeak_0] >= kl_close[ipeak_1];

var int: obj;
constraint obj = inow - ipeak_1;


solve minimize obj;