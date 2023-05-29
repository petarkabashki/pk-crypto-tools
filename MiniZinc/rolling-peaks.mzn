
int: n;
set of int: N = 1..n;
int: lag;

% array[N] of int: lmin;
array[N] of int: ser;

array[N] of var {-1,0,1}: dirx;
constraint dirx[1] = 0;
constraint forall(i in 2..n)(dirx[i] = 1 - 2* (ser[i] <= ser[i-1]) + (ser[i] = ser[i-1]) );

array[N] of var int: cdirx;
constraint cdirx[1] = 0;
constraint forall(i in 2..n)(cdirx[i] = if dirx[i] = 0 then cdirx[i-1] else cdirx[i-1] + dirx[i] endif);


array[N] of var 1..n: durx;
constraint durx[1] = 1;
constraint forall(i in 2..n)(durx[i] = if dirx[i] = 0 then durx[i-1] + 1 else 1 endif );

% constraint cnmax[1] = 0;
% var set of N: peaks = {i | i in lag+1..n-1 where lmax[i+1] < lmax[i] /\ lmax[i-lag] < lmax[i] };

% output ["peaks=\(peaks)"];

solve satisfy;




%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% array[int] of int: kl_open;
% array[int] of int: kl_high;
% array[int] of int: kl_low;
% array[int] of int: kl_close;

% int: kl_n;
% set of int: KLN = 1..kl_n;
% set of int: KLN0 = 0..kl_n;
% int: pktr_n;
% set of int: PKTR = 1..pktr_n;

% array[PKTR] of var KLN0: apktr;

% var PKTR: npktr;

% constraint apktr[npktr] = 1;
% constraint apktr[pktr_n] = kl_n;
% constraint forall(j in 1..npktr-1)(apktr[j] = 0);

% include "increasing.mzn";
% constraint increasing(apktr);

% constraint forall(i in npktr..pktr_n-1)(
%     let { var KLN: idn = if kl_close[apktr[i]]>kl_close[apktr[i+1]] then i+1 else i endif, 
%           var KLN: iup = if idn = i then i+1 else i endif} in
%           forall(j in apktr[i]+1..apktr[i+1]-1)(kl_close[j] >= kl_close[apktr[idn]] /\ kl_close[j] <= kl_close[apktr[iup]] )
% );

% constraint forall(i in npktr..pktr_n-2)(
%     kl_close[apktr[i]] >= kl_close[apktr[i+1]] /\ kl_close[apktr[i+1]] <= kl_close[apktr[i+2]]
%     \/ kl_close[apktr[i]] <= kl_close[apktr[i+1]] /\ kl_close[apktr[i+1]] >= kl_close[apktr[i+2]]
%     );

% include "alldifferent.mzn";
% constraint all_different_except_0(apktr);

% solve maximize npktr;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
