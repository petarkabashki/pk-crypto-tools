% Author: Roberto Castaneda Lozano -- rcas@sics.se
%
% Simple model of a double auction.
% The problem is to find a match between all bid and ask orders in an order book
% so that the total traded quantity is maximized. Each order is represented by
% its quantity, minimum quantity, limit price and position in its side of the
% order book.
% This is a single-step simplification of the model presented in "Testing
% Continuous Double Auctions with a Constraint-based Oracle", Roberto CastaÃ±eda
% Lozano, Christian Schulte, Lars Wahlberg. 2010.
% 
% Blog post explaining: https://hsimonis.wordpress.com/testing-example-minizinc/
%
% Input data

% Number of bid orders
int: n;
% Number of ask orders
int: m;

% Bid orders

% Quantity
array[1..n] of int: qb;
% Minimum acceptable quantity
array[1..n] of int: mqb;
% Limit price
array[1..n] of int: lpb;

% Ask orders

% Quantity
array[1..m] of int: qa;
% Minimum acceptable quantity
array[1..m] of int: mqa;
% Limit price
array[1..m] of int: lpa;

set of int: B = 1..n;
set of int: A = 1..m;

% Decision variables

% Traded quantity between each pair of bid and ask orders
array [B, A] of var 0..min(max(qb),max(qa)): tq :: is_output;

% Auxiliary variables

% Total traded quantity for each bid order
array [B] of var 0..max(qb): tqb :: is_output =
[sum (a in A) (tq[b, a]) | b in B];

% Total traded quantity for each ask order
array [A] of var 0..max(qa): tqa :: is_output =
[sum (b in B) (tq[b, a]) | a in A];

% Total traded quantity
var int: total_tq :: is_output = sum (b in B) (tqb[b]);

% Constraints

% Limit price
constraint forall (b in B, a in A) (
lpb[b] < lpa[a] -> tq[b,a] = 0
);

% Maximum quantity
constraint forall (b in B) (
tqb[b] <= qb[b]
);
constraint forall (a in A) (
tqa[a] <= qa[a]
);

% Minimum acceptable quantity constraint
forall (b in B) (
tqb[b] >= mqb[b] \/ tqb[b] = 0
);
constraint forall (a in A) (
tqa[a] >= mqa[a] \/ tqa[a] = 0
);

% Order priority
constraint forall (bi in B, bj in B where bi < bj) (
tqb[bi] < qb[bi] /\ mqb[bi] = 0 -> tqb[bj] = 0
);

constraint forall (ai in A, aj in A where ai < aj) (
tqa[ai] < qa[ai] /\ mqa[ai] = 0 -> tqa[aj] = 0
);

% Disclaimer: naive search strategy 🙂
solve
:: int_search([tq[b, a] | b in B, a in A], first_fail, indomain_max, complete)
maximize total_tq;