%%mzn_model going_up 

array[int] of int: kl_signal;

int: kl_n;
set of int: KLN = 1..kl_n;
set of int: KLN0 = 0..kl_n;
int: pktr_n = 6;
set of int: PKTR = 1..pktr_n;

array[PKTR] of var KLN: apktr;

predicate sig_increasing(array[KLN] of int: klsig, array[PKTR] of var KLN: apktr, int:start, int: end) =
    forall(i in apktr[start]+1..apktr[end]-1)(klsig[i] >= klsig[apktr[start]] /\ klsig[i] <= klsig[apktr[end]]);

predicate sig_decreasing(array[KLN] of int: klsig, array[PKTR] of var KLN: apktr, int:start, int: end) =
    forall(i in apktr[start]+1..apktr[end]-1)(klsig[i] <= klsig[apktr[start]] /\ klsig[i] >= klsig[apktr[end]]);

include "strictly_increasing.mzn";
constraint strictly_increasing(apktr);

% constraint forall(i in 1..pktr_n div 2 )(
%         sig_decreasing(kl_signal, apktr, i*2 - 1, i*2)
%     );

% constraint forall(i in 1..pktr_n div 2 -1 )(
%         sig_increasing(kl_signal, apktr, i*2 , i*2 + 1)
%     );

constraint forall(i in 1..pktr_n-1)(apktr[i+1]-apktr[i] > 2);

include "alldifferent.mzn";
constraint all_different_except_0(apktr);

constraint sig_decreasing(kl_signal, apktr, 1,2);
constraint sig_increasing(kl_signal, apktr, 2,3);
constraint sig_decreasing(kl_signal, apktr, 3,4);
constraint sig_increasing(kl_signal, apktr, 4,5);
constraint sig_decreasing(kl_signal, apktr, 5,6);


% constraint sig_increasing(kl_signal, apktr, 1,2);
% constraint exists([true | i in 1..apktr[1]-1 where sig_increasing(kl_signal, apktr, i, 1)]);
% constraint kl_signal[apktr[2]] < kl_signal[apktr[4]];
% constraint kl_signal[apktr[3]] > kl_signal[apktr[5]];

solve minimize apktr[pktr_n-1] - apktr[1+1];
% solve satisfy;