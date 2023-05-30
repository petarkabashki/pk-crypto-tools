
int: n=5;
set of int: N = 1..n;

array[N] of var N: a;

constraint forall(i in n..1)(a[i]=i);
solve satisfy;