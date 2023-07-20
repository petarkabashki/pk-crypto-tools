
array[int] of int: markers;

int: n = length(markers);
% int: n_markers = length(markers);

array[1..n] of var int: prev;
constraint prev = [if  i > 1 /\ markers[i] == markers[i-1] then prev[i - 1] + markers[i] else 0 endif | i in 1..n];


array[1..n] of var int: next;
constraint next = [if  i < n /\ markers[i] == markers[i+1] then next[i + 1] + markers[i] else 0 endif | i in 1..n];

solve satisfy;
% Use this editor as a MiniZinc scratch book


% Print the result
% output ["\(result[i])" | i in 1..n];