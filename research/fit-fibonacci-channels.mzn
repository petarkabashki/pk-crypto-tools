array[int] of float: fibs = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1];
int: n_fibs = length(fibs);
set of int: N_FIBS = 1..n_fibs;

array[int] of float: c;

int: n_c = length(c);
set of int: N_C = 1..n_c;

var N_C: x0;
var N_C: x1;
var N_C: x2;

constraint x0 < x1 /\ x1 < x2;

var float: y0; var float: y1; var float: y2; 
constraint y0 = c[x0] /\ y1 = c[x1] /\ y2 = c[x2];

var float: k;
constraint k = (y2 - y0) / (x2 - x0);

array[N_FIBS] of var float : x_0_1_fibs;
constraint x_0_1_fibs = [x0 + fibs[i] * (x1 - x0) | i in N_FIBS];
array[N_FIBS] of var float: y_0_1_fibs;
constraint y_0_1_fibs = [y0 + fibs[i] * (y1 - y0) | i in N_FIBS];

array[N_C, N_FIBS] of var float: fib_levels; % = [[1 | i in N_C] |j in N_FIBS];
constraint forall(i in N_C)(
    forall(j in N_FIBS) (fib_levels[i,j] = (k * i) )
% %     forall(j in N_FIBS) (fib_levels[i,j] = (i - x_0_1_fibs[j]) * k + y_0_1_fibs[j])
);
% array[N_C] of var float: y_lower = [(i - x1) * k + y1 | i in N_C];
% array[N_C] of var float: y_upper = [(i - x0) * k + y0| i in N_C];


% y_upper = (pd.Series(range(wdf.shape[0])) - x0) * k + y0


% y_tran = y - y_upper
% y_tran.index = wdf.index
% yt0, yt1, yt2 = y_tran.iloc[[x0,x1,x2]]
% var N_C: y1; var N_C: y2;


% y_d = y2 - y0
% k = (y2 - y0) / (x2 - x0)

solve satisfy;
