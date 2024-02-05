csv ← "',/" •Import "./bqn-libs/csv.bqn"  # Easier characters to write

lines ← •FLines "ALGO_USDT-1d.csv"
≢lines
c ← csv.SplitL lines
ch←1↑c
cv←1↓c
#cv← •ParseFloat¨¨  1↓c
cv •ParseFloat¨¨↩

↑10↑cv





