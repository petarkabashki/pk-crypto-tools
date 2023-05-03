
array[int] of int: kl_open;
array[int] of int: kl_high;
array[int] of int: kl_low;
array[int] of int: kl_close;

int: kl_n;
set of int: KLN = 1..kl_n;
set of int: KLN0 = 0..kl_n;
int: pktr_n;
set of int: PKTR = 1..pktr_n;

array[PKTR] of var KLN0: apktr;

var PKTR: npktr;

constraint apktr[npktr] = 1;
constraint apktr[pktr_n] = kl_n;
constraint forall(j in 1..npktr-1)(apktr[j] = 0);

include "increasing.mzn";
constraint increasing(apktr);

constraint forall(i in npktr..pktr_n-1)(
    let { var KLN: idn = if kl_close[apktr[i]]>kl_close[apktr[i+1]] then i+1 else i endif, 
          var KLN: iup = if idn = i then i+1 else i endif} in
          forall(j in apktr[i]+1..apktr[i+1]-1)(kl_close[j] >= kl_close[apktr[idn]] /\ kl_close[j] <= kl_close[apktr[iup]] )
);

constraint forall(i in npktr..pktr_n-2)(
    kl_close[apktr[i]] >= kl_close[apktr[i+1]] /\ kl_close[apktr[i+1]] <= kl_close[apktr[i+2]]
    \/ kl_close[apktr[i]] <= kl_close[apktr[i+1]] /\ kl_close[apktr[i+1]] >= kl_close[apktr[i+2]]
    );

include "alldifferent.mzn";
constraint all_different_except_0(apktr);

solve maximize npktr;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
