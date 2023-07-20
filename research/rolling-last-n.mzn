% Define input data
int: n;              % Number of rows
array[int] of int: idxs;  % Array of indices (between 1 and n)
int: n_idxs = length(idxs);
int: m;              % Number of columns (m most recent items)

% Define the result array
array[1..n,1..m] of var 0..n: result;

% set of int: idxs_set = {x | x in idxs};
include "globals.mzn";

% array[1..n] of var 0..n_idxs: ia_last_idx;
% constraint forall(i in 1..n)(
% %     ia_last_idx[i] = max([if idxs[j] >= i then 0 else j endif | j in 1..n_idxs] ++ [0])
%     forall(j in 1..ia_last_idx[i])(idxs[j] < i)
%     /\ forall(j in ia_last_idx[i]+1..n_idxs)(idxs[j] >= i)
    
%     forall(j in 1..ia_last_idx[i])(
%         i
%     )
% );

constraint forall(i in 1..n) (
    let { 0..n_idxs: ilast = max([if idxs[j] >= i then 0 else j endif | j in 1..n_idxs] ++ [0]) } in
    forall(j in 1..m)(
        result[i,m-j+1] = if ilast - j + 1 >= 1 then idxs[ilast - j + 1] else 0 endif 
    )
%     /\ forall(j in 
);

solve satisfy;


