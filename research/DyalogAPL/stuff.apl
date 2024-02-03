


⍝ -------------------------------------------
⍝ --- Statistical and utility functions

kload ← { (d h) ← ⎕CSV ⍵ '' (2 2 2 2 2 2) 1 ⋄ d}
sort←((⊂⍋)⌷⊢) 
⍝ --- Mean, variance, standard deviation, nth moment 
mean←(+/÷≢)
⍝ var←((+/⍤×⍨mean-⊢)÷(¯1+≢)) 
var←((+/⍤×⍨(+/÷≢)-⊢)÷(¯1+≢))
std←0.5*⍨ var
mom← {((≢) +/⍤ ÷⍨ ∘ (⍺*⍨⊢)⊢-(+/÷≢))⍵}
qtl← ((((⌈⊣×(≢⊢))⌷⊢)∘((⊂⍋)⌷⊢))) ⍝ quantlie : 0.3 qtl array 
⍝ --- Summary statistics
⍝ --- split first column for plotting
pspl←{(⊂↓∘⍉(1↓[2]⊢)⍵), ⊂,1↑[2]⍵}


⍝ ---------------------------------------
⍝ --- Load candlesticks
⍝ ---
fldb←'/media/grenada/Data/Accounting/pk-crypto-tax-calculator/data-csv/binance/'
k←kload⊢fldb,'ALGO','_USDT-4h.csv'
]display 10↑ kl← ¯1↓[2] 1↓[2] k
10↑ lk← ⍟ (⊂2 3 4 5)⌷[2] k ⍝ take log of ohlc


]display  (({|⍵[;2]-0,1↓⍵[;4]}⍪[0.5] {|-/⍵[;3 2]}))  10↑kl

]display  {⍵[;2 3]-[1]0,1↓⍵[;4]}  10↑kl




⍝ --- direction and change of direction 
dr← ((1,∘×1∘↓-¯1∘↓)∘,¯1↑[2]⊢)  ⍝ direction
cdr ← (1,1∘↓≠¯1∘↓)  ⍝ change of direction: cdr dr lk
⍝ --- number of running periods in the same direction
]display 10↑ ((⊃,/)∘(+\¨)∘(cdr⊂⊢)dr) lk 
⍝ --- take the positive ones
]display 10↑ ((/⍨∘(0∘<))⍨) ⊢ ((⊃,/)∘(+\¨)∘(cdr⊂⊢)dr) lk 
⍝ --- take the negative ones
]display 20↑ ((/⍨∘(0∘>))⍨) ⊢ ((⊃,/)∘(+\¨)∘(cdr⊂⊢)dr) lk 

⍝ --- quantiles for number of negative periods
]display  (st stt)←0.9 500⋄pct←(st+ (1-st)÷⌽⍳stt)⋄⍉↑(⊂pct),⊂ pct qtl¨ ⊂ | ((/⍨∘(0∘>))⍨) ⊢ ((⊃,/)∘(+\¨)∘(cdr⊂⊢)dr) lk 

⍝ --- negative periods
nk←|((/⍨∘(0∘>))⍨) ⊢ ((⊃,/)∘(+\¨)∘(cdr⊂⊢)dr) lk 
]display  r← ({⍺ (≢⍵)}⌸) nk
⍝ --- percentages for number of consecutive falling candles 
⍝ ]display ((⊂∘⍋∘,1↑[2]⊢)⌷⊢) r[;,1], r[;2] ÷ +/r[;2]
⍝ ]display   {⍵[;,1],((⊢÷(+/⊢))(,¯1↑[2]⊢))⍵} r
]display   {⍵[;1],6 4⍕((+⍀)∘(⊢÷(+⌿⊢)))((¯1↑[2]⊢))⍵} r

⍝ ]display 10↑ (+\¨∘(cdr⊂⊢)dr) lk 

⍝ --- number of days in the same direction

⍝ ------------------------------------------------------------
⍝ ------------------------------------------------------------
⍝ --- Python Interface - unstable with large arrays

]load /media/grenada/Data/work/DyalogAPL/pynapl/pynapl/Py
py←⎕NEW Py.Py(('PyPath' '/home/grenada/miniconda3/envs/py310/bin/python'))

py.Exec 'import pandas as pd'
py.Exec 'import numpy as np'
py.Exec 'from datetime import datetime, date'
py.Exec 'import pandas_ta as ta'

⍝ ------------------------------------------------------------
⍝ ------------------------------------------------------------
⍝ --- Technical Indicators
⍝ ------------------------------------------------------------


⍝ 14   {⍵[;2 3], ¯1⌽⍵[;4]}  20↑lk
⍝ ]display   ⍉|↑{(⊂-/⍵[;,1 2]), (⊂-/⍵[;1 3]), (⊂-/⍵[;2 3])} {⍵[;2 3], ¯1⌽⍵[;4]}  20↑lk
⍝ ]display   ((⊂1 2) (⊂1 3) (⊂2 3)) (⊣⌷⊢)¨ ⊂{⍵[;2 3], ¯1⌽⍵[;4]}  20↑lk
⍝ --- True range
⍝ tr←{⌈/|(-/⍵[;2 3]),⍵[;2 3]-[1]0,1↓⍵[;4]} 
⍝ --- ATR
⍝ ]display  14(⊣{n←⍺⋄⌽⊃{(n÷⍨⍺+(n-1)×⊃⍵),⍵}/⍵}(⌽(⊂⊣⍴(+/⊣↑⊢)÷⊣),(⊣↓⊢))) tr kl

⍝ ------------------------------------------------------------
⍝ --- EMA
⍝ 
ema← {k←2÷1+⍺⋄⌽⊃{((k×⍺)+(1-k)×⊃⍵),⍵}/⊢ ⌽⊢((⊂1↑⊢),(1↓⊢)) ⍵}
⍝ --- EMAs like in pandas_ta
ema← ((( ⊢,1∘-)(2÷1+⊣)) {am←⍺⋄⌽⊃{(am +.× (⍺, ⊃⍵)),⍵}/ ⌽ (⊂⍵[1]),1↓⍵} (⊣((⊣⍴((+/↑)÷⊣)),↓)⊢))
rma← ((( ⊢,1∘-)(1÷⊣)) {am←⍺⋄⌽⊃{(am +.× (⍺, ⊃⍵)),⍵}/ ⌽ (⊂⍵[1]),1↓⍵} (⊣((⊣⍴((+/↑)÷⊣)),↓)⊢))

⍝ ------------------------------------------------------------
⍝ --- Average True range as in https://school.stockcharts.com/doku.php?id=technical_indicators:average_true_range_atr
⍝ 
tr ←  {((⊃1 1↑⊢),(⌈/ 1∘↓)) ⍉|↑ ((⊂1 2) (⊂1 3) (⊂2 3)) (-/⊣⌷[2]⊢)¨ ⊂{⍵[;2 3], ¯1⌽⍵[;4]} ⍵}  
atr ← (rma∘tr)


⍝ --- call pandas_ta ema on a vector
⍝ 'ta.ema(pd.Series(⎕),⎕).tail(80)' py.Eval (⍳100) 21


⍝ ]display 30↑  14(⊣{n←⍺⋄⌽⊃{(n÷⍨⍺+(n-1)×⊃⍵),⍵}/⍵}(⌽(⊂⊣⍴(+/⊣↑⊢)÷⊣),(⊣↓⊢))) tr kl


⍝ ]display 14{n←⍺⋄⌽⊃{(n÷⍨⍺+(n-1)×⊃⍵),⍵}/⊢ ⌽⊢((n↑⊢),(n↓⊢)) ⍵} 50↑ tr kl



⍝ ]display 4  ((( 1∘-,⊢)(2÷1+⊣)) {am←⍺⋄⌽{(am +.× (⍺, ⊃⍵)),⍵}/ ⌽⍵} ((⊂1↑⊢),(1↓⊢))) ⍳20 



⍝ ------------------------------------------------------------
⍝ ------------------------------------------------------------
⍝ --- Check if EMAs act as support
⍝ ------------------------------------------------------------

⍝ ]display ¯10↑¨ dband← 26 14 (¯1 0 1)({(1,⊢)¨⊃⍺[3]} {⍺(⊃+.×)¨⊂⍵}  {⍺[1] ema ⍵[;4]} (,⍥⊂) {⍺[2] atr ⍵} ) lk 
⍝ ]plot pspl 400↑ (⍳≢k),(lk[;4 3 2],⍉↑dband)  

⍝ --- caluclates on which side of the band the price is
cbs← { (×⍺-⊃⍵[2])×(⍺>⊃⍵[3])∨(⍺<⊃⍵[1])}
⍝ ]]display  ¯50↑ bs← (lk[;4]) cbs dband
cbin←((0,(1∘↓))(0≠¯1∘⌽)∧(0∘=))
⍝ signed 
sbin← {pr←¯1⌽⍵⋄0,1↓pr×(⍵=0)∧(pr≠0)}  
sbout← {pr←¯1⌽⍵⋄0,1↓⍵×(⍵≠0)∧(pr=0)}
⍝ --- makes a list of in-outs
cdbinout← ((¯1∘↓)((0∘≠⊢⍤/⊢)⊣) (((0∘≠)⊢⍤/⊢),)¨(0≠⊣)⊂⊢)
⍝ --- counts of in and out  in specific order
stinout← {{⍺ (¯1+≢⍵)}⌸ (4 2 ⍴1 1 1 ¯1 ¯1 ¯1 ¯1 1)⍪ ↑ ((0∘≠)⊢⍤/⊢)¨ ¯1↓ ⍵}
⍝ --- add fractions
cfsta← (,∘((⊢÷+/)(2⌷[2]⊢)))⍨ 
⍝ --- add fractions per in-band type +/-1
fperstats← (⊢,⊃∘(,/(↓2 2⍴⍳4)((⊢÷+/)(⊂⊣)⌷(2⌷[2]⊢))¨⊂))

⍝ 3↑ dbin cdbinout dbout
⍝ leave only in and out markers
⍝ 3↑ ((0∘≠)⊢⍤/⊢)¨ dbinout

]display stinout (sbin cdbinout sbout) bs
]display stinout dbinout

⍝ --- calculates it all, cum stats for in/out of band
⍝ ]display dst← 26 14 (¯1 0 1)((cfsta ∘ stinout (sbin cdbinout sbout)) {⍵[;4]} cbs {(1,⊢)¨⊃⍺[3]} {⍺(⊃+.×)¨⊂⍵}  {⍺[1] ema ⍵[;4]} (,⍥⊂) {⍺[2] atr ⍵} ) lk 

emastats ← ((stinout (sbin cdbinout sbout)) {⍵[;4]} cbs {(1,⊢)¨⊃⍺[3]} {⍺(⊃+.×)¨⊂⍵}  {⍺[1] ema ⍵[;4]} (,⍥⊂) {⍺[2] atr ⍵} )  

⍝ --------------------------------------
⍝ --- Stats for emas with different lengths
⍝ 
⍝ --- Calculate stats for all moving averages from 5 to 205
desta ← {⍵ 14 (¯1 0 1) emastats lk }¨ (5×⍳40)
⍝ --- Add fractions
festa ← ↑fperstats¨ desta
⍝ ((¯1∘↑⍤⍸0∘≠)↑⊢)
⍝ -- Plot bounce-back ratio for up/down moves into the band
]plot pspl ((5∘×∘⍳≢),⊢) festa[;1 3;2]

⍝ -- Plot number of winning cases
]plot pspl ((5∘+∘⍳≢),⊢) festa[;1 3;2]

⍝ ------------------------------------------------------------
⍝ ------------------------------------------------------------
⍝ --- fixing ema 33, chosing different band widths * atr
⍝ ------------------------------------------------------------

⍝ --- FIBS
]display fibs← 0,,(⍳5){⍺∘.+⍵} .272 .414 .5 .618 .786 1
⍝ --- make bands
]display abands ← (-,0,⊢)¨ ,0 1 2{⍺∘.+⍵} .272 .414 .5 .618 .786 1
⍝ calculate stats
desta ← {33 14 ⍵ emastats lk }¨ abands
festa ← ↑fperstats¨ desta
]plot pspl ((⍳≢),⊢) festa[;1 3;3]
⍝ -- Plot number of winning cases
]plot pspl ((⍳≢),⊢) festa[;1 3;2]

⍝ ------------------------------------------------------------
⍝ ------------------------------------------------------------
⍝ --- Rolling window stats
⍝ ------------------------------------------------------------
⍝ --- cut into windows
cwnd ← {n←⌊(≢⍵)÷⍺[1]⋄ixs←(⍺[1])(⊢+∘⍳⊣)¨⊢⍺[1]×¯1+⍳n⋄ixs ((⊂⊣)⌷⊢)¨ ⊂⍵}
]display 13 0.5 cwnd 10×⍳100

 33 14 (¯1 0 1) ((stinout (sbin cdbinout sbout)) {⍵[;4]} cbs {(1,⊢)¨⊃⍺[3]} {⍺(⊃+.×)¨⊂⍵}  {⍺[1] ema ⍵[;4]} (,⍥⊂) {⍺[2] atr ⍵} )  lk


⍝ -------------------------------------------------------------
⍝ -------------------------------------------------------------
⍝  Multiple bands, matrix form throughout
⍝ -------------------------------------------------------------
⍝ -------------------------------------------------------------
⍝ 
⍝ Fibs
⍝ ]display fibs← 0,,(⍳5){⍺∘.+⍵} .272 .414 .5 .618 .786 1
]display fibs← 0 .272 0.5 .618 1 1.618 2 2.618 3 3.618 4 5 6
⍝ fib levels -/0/+
]display blevels ← ((⌽0,-),⊢)1↓fibs
⍝ ]display blevels ← ((⌽0,-),⊢) ⊢ 0 .272 0.5 .618 1 1.618 2 2.618 3 
⍝ Calculates bands from fibs and aNx2 matrix
muladd ← (↑(1⌷[2]⊢)+⊣×2⌷[2]⊢)
⍝ Calculates ema and atr
cematr ← (⍉∘↑{⍺[1] ema ⍵[;4]} (,⍥⊂) {⍺[2] atr ⍵})
sbin← {pr←¯1⌽⍵⋄0,1↓pr×(⍵=0)∧(pr≠0)}  
sbout← {pr←¯1⌽⍵⋄0,1↓⍵×(⍵≠0)∧(pr=0)}
⍝ example lines and plot
filines← 33 14 blevels ( (3⌷⊣) muladd cematr) ⊢ 200↑lk
]plot pspl ((⍳≢),⊢) (200↑lk),filines

cbs← {(×⍺-⍵[;2])×(⍺<⍵[;1])∨⍺>⍵[;3]}
cbinout←( ((0∘≠⊢⍤/⊢)⊣) (((0∘≠)⊢⍤/⊢),)¨ (0≠⊣)⊂⊢)
⍝ --- add fractions per in-band type +/-1
fperstats← (⊢,⊃∘(,/(↓2 2⍴⍳4)((⊢÷+/)(⊂⊣)⌷(2⌷[2]⊢))¨⊂))
stinout← {{⍺ (¯1+≢⍵)}⌸ (4 2 ⍴1 1 1 ¯1 ¯1 ¯1 ¯1 1)⍪ ↑ ((0∘≠)⊢⍤/⊢)¨ ¯1↓ ⍵}

⍝ in/out markers in matrix form
]display 33 14 (¯1 0 1) (fperstats ∘stinout∘ {⍵[;1] cbinout ⍵[;2]}∘ (sbin (⍉∘↑,⍥⊂) sbout ) {⍵[;4]} cbs {⍺[3]} muladd cematr )  1000↑ lk

emastats ← (fperstats ∘stinout∘ {⍵[;1] cbinout ⍵[;2]}∘ (sbin (⍉∘↑,⍥⊂) sbout ) {⍵[;4]} cbs {⍺[3]} muladd cematr ) 
]display 33 14 (¯1 0 1) emastats  5000↑ lk
⍝ plot some of it, price + bands
]plot pspl ((⍳≢),⊢) 200↑ ⊢ 26 14 (¯1 0 1) ( ⊢,{⍺[3]} muladd cematr )  1000↑ lk

⍝ cbands← (⊢, (⍉⍤↑(⊂1⌷[2]⊢)+¨ ((⌽∘-⊣),0,⊣)×¨(⊂2⌷[2]⊢)))

]display (((⌽0,-),⊢)1↓fibs)


⍝ --- Calculate stats for all moving averages from 5 to 205
desta ← {⍵ 14 (¯1 0 1) emastats 10000↑lk }¨ (5×⍳40)
desta←↑desta
]plot pspl ((⍳≢),⊢) desta[;1 3;2]
]plot pspl ((⍳≢),⊢) desta[;1 3;3]

⍝ --------------------------------------
⍝ --- Windowed statistics
(2×168) {n←⌊⍵÷⍺⋄⍺×¯1+⍳n} ≢lk
desta← {45 14 (¯.786 0 .786) emastats ⊢ ⍵[2]↑⍵[1]↓lk }¨  ⊢ 168 {n←⌊⍵÷⍺⋄⍺,⍨¨⍺×¯1+⍳n} ≢lk
desta←↑desta
]plot pspl ((⍳≢),⊢) desta[;1 3;2]
]plot pspl ((⍳≢),⊢) desta[;1 3;3]

⍝ --- for different bands 

⍝ --- FIBS
]display fibs← 0,,(⍳5){⍺∘.+⍵} .272 .414 .5 .618 .786 1
⍝ --- make bands
]display abands ← (-,0,⊢)¨ ,0 1 2{⍺∘.+⍵} .272 .414 .5 .618 .786 1
⍝ calculate stats
desta ← {100 14 ⍵ emastats lk }¨ abands
festa ← ↑fperstats¨ desta
]plot pspl ((⍳≢),⊢) festa[;1 3;3]
⍝ -- Plot number of winning cases
]plot pspl ((⍳≢),⊢) festa[;1 3;2]


⍝ -------------------------------------
⍝ -------------------------------------
⍝ ------ Detailed analysis


⍝ -------------------------------------
⍝ positions of in and out bounces
cioidxs←(⍉⍤↑⍤(⍸¨⍤|↓[1]))
⍝ in/out markers with positions
]display  10↑ dioxs ← 50 14 (¯1 0 1) ((⊢ {⍺[⍵[;,1];1],⍺[⍵[;,2];2],⍵} (¯1↓cioidxs))⍤(sbin (⍉∘↑,⍥⊂) sbout) {⍵[;4]} cbs {⍺[3]} muladd cematr )  lk
⍝ Grouped by IN/OUT marker
]display  ↑{⍵[1], ≢⊃⍵[2]}¨ ↓⊢ dgioxs←((4 2⍴1 1 ¯1 ¯1 1 ¯1 ¯1 1)⍪dioxs[;1 2]) {⍺ (1↓⍵)}⌸((4 2⍴0)⍪dioxs[;3 4])
⍝ show in/out markers order
]display dgioxs[;1]

⍝ number of bounce-backs vs continuations
]display  {⍺(≢⍵)}⌸{⍵[;1]×⍵[;2]} dioxs


⍝ ]display  ↑{⍵[1], ≢⊃⍵[2]}¨ ↓⊢ dgioxs←((4 2⍴1 1 ¯1 ¯1 1 ¯1 ¯1 1)⍪dioxs[;1 2]) {⍺ (1↓⍵)}⌸((4 2⍴0)⍪dioxs[;3 4])


⍝ grouped by in/out, ordered groups
]display  50 14 (¯1 0 1) ( {((↓4 2⍴1 1 ¯1 ¯1 1 ¯1 ¯1 1)⍪⍵[;1]) {⍺ (1↓⍵)}⌸((4 2⍴0)⍪⍵[;2 3])}∘ ({⍵[;1] cbinout ⍵[;2]}, (¯1↓cioidxs))∘(sbin (⍉∘↑,⍥⊂) sbout) {⍵[;4]} cbs {⍺[3]} muladd cematr )  500↑ lk

⍝ In/out indexes
]display 10↑ dioidxs ←  50 14 (¯1 0 1) ( (¯1↓cioidxs)⍤(sbin (⍉∘↑,⍥⊂) sbout) {⍵[;4]} cbs {⍺[3]} muladd cematr )  lk


iogr ←  50 14 (¯1 0 1) ( {((↓4 2⍴1 1 ¯1 ¯1 1 ¯1 ¯1 1)⍪⍵[;1]) {⍺ (1↓⍵)}⌸((4 2⍴0)⍪⍵[;2 3])}∘ ({⍵[;1] cbinout ⍵[;2]}, (¯1↓cioidxs))∘(sbin (⍉∘↑,⍥⊂) sbout) {⍵[;4]} cbs {⍺[3]} muladd cematr )  lk




⍝ -------------------------------------------------------------
⍝ -------------------------------------------------------------
⍝  Directional Change / ZigZag Algorythm
⍝ -------------------------------------------------------------
⍝ -------------------------------------------------------------
⍝ 
⍝ 

]plot pspl ((⍳≢),⊢) lk

⍝ --- ZigZag with running extrema
]display 30↑ lk[;,4], xp← ⊢ 0.1 ({⍵,(|⍵[;2])×¯1⌽⍵[;3]}⍤↑⍤⌽⍤⊃⍤{qdc←⍺⋄ {(dir evdc ex)←⊃⍵⋄nex←dir×⌈/dir×(ex ⍺)⋄qdc<dir×ex-⍺:(⊂(-dir) dir ⍺),⍵ ⋄(⊂dir 0 nex),⍵} / ⍵} ∘(⌽(⊂∘⊂(1,1),(1∘↑⊢)),(1↓⊢))) ⊢ lk[;4]

⍝ --- Plot price and extremas 
]plot pspl ((⍳≢),⊢) 200↑ lk[;,4],xp[;3]


⍝ ---Take number of bars for each extrema
]display {(≢⍵), ¯1↑⍵}¨ {(1++\|⍵[;2])⊆⍵[;4]}  20↑xp
⍝ --- Number of bars, extrema price, previous extrema price
]display 10↑ {⍵,¯1⌽⍵[;2]} ↑{(≢⍵),¯1↑⍵}¨ {(1++\|⍵[;2])⊆⍵[;4]}  xp

⍝ --- --- --- ---
⍝ --- ZigZag as per neurotrader
]display 20↑ xtr← 0.1 ( (↑∘⌽∘⊃)⍤{qdc←⍺⋄⊃{(ax (dir xi xp))←⍵⋄(i p)←⍺⋄0<dir×p-xp:(ax (dir i p))⋄qdc<dir×xp-p:(((⊂dir, i xi xp),ax) ((-dir) i p))⋄⍵} / ⍵}∘{⌽(⊂((⊂⍬), ⊂1,1, 2⌷⊃⍵)),1↓⍵}∘↓) ⊢ ((⍳∘≢),⊢) lk[;,4]
⍝ --- Extrapolate extremas
]display 10↑ xpol←  {⊃,/⍵[;1]+⍵[;3]×¯1+⍳¨⍵[;2]} {z←⌽(1⊖⍵)-⍵⋄d←÷/z⋄¯1↓⍵[;,2],z[;,2],d} ¯2↑[2] xtr
⍝ Plot extremas and price
]plot pspl ((⍳≢),⊢) 200↑ ((≢xpol)↑lk[;,4]),xpol



⍝ ]display  20↑ xp, xtxp← ⊃,/{⍵[;2]+⍵[;4]×¨(¯1+⍳)¨⍵[;1]} {⍵, (⍵[;2]-⍵[;3])÷⍵[;1]} {⍵,¯1⌽⍵[;2]} ↑{(≢⍵),¯1↑⍵}¨ {(1++\|⍵[;2])⊆⍵[;4]}  xp



⍝ --- Plot price and extremas 
]plot pspl ((⍳≢),⊢) 200↑ lk[;,4],xp[;3]

⍝ 
⍝ 
⍝ 
⍝ -------------------------------------------------------------
⍝ -------------------------------------------------------------
⍝  TODOs / 
⍝ -------------------------------------------------------------
⍝ -------------------------------------------------------------
⍝ 
⍝ --- Extract Dailies / 3D / W / 2W from 1h / 4h
⍝ --- Fit fibonnaci levels based on highs and lows, potentially on higher timeframe
⍝ --- Backtest rejections of fibonacci levels
⍝ --- Bottom-outs, n candles to support + wick through
⍝ --- Pullbacks in trends: higher/lower qdc extremas
⍝ --- On 4h - rejection to around previous extrema
⍝ --- Pullbacks to EMAS on strong momentum (diff btn emas)
⍝ --- Implement KAMA filters
⍝ --- Implement HMMs
⍝ --- HMM statistics
⍝ --- Price / EMA statistics (+ATR/STD)
⍝ --- Matrix Profile
⍝ --- Reverse return to model
⍝ --- SL stats
⍝ --- Ichimoku cloud



⍝ -------------------------------------------------------------
⍝ -------------------------------------------------
⍝ --- prepends the SMA for the first n after removing them; calculates the alpha and 1-alpha
4 ((((⊢,1∘-)⍤(2÷1+⊣))),  (+/÷≢)⍤↑,↓) ⊢ 20↑ kl[;4]
⍝ --- prepends the aaverage n-1
4  ((-∘1⊣)((⊣⍴((+/↑)÷⊣)),↓)⊢) ⍳10 

4 ( (1∘-,⊢)⍤(2÷1+⊣) {am←⍺⋄{am×⍺ ⍵}\⍵} (+/÷≢)⍤↑,↓) ⊢ 7↑ kl[;4]
4 ( (-∘1 ⍴ (1∘-,⊢)⍤(2÷1+⊣)) {am←⊃⍺⋄{am+.×⍺ ⍵}\⍵} (+/÷≢)⍤↑,↓) ⊢ 10↑ kl[;4]

⍝ Prepends n-times the average of the first n
]display 5 (⊢,⍨⊣⍴((+/↑)÷⊣)) ⊢ 20↑ kl[;4]
]display 5 ((⊢,⍨⊣⍴((+/↑)÷⊣))) ⊢ 20↑ kl[;4]

]display 5↑ lk← ⍟ (⊂2 3 4 5)⌷[2] k

⍴ emas← ⍉↑(14 21 50 100 200) ema¨ ⊂,¯1↑[2]lk

⍝ --- Plot close price and emas
]plot {(⊂↓∘⍉(1↓[2]⊢)⍵), ⊂,1↑[2]⍵} 200↑ 4000↓  100↓ (⍳≢k),lk[;4 3 2],emas[;,1 2 3 4 5] 

⍝ 5↑ {⍵[;2 3 4] -¨ ⊂⍵[;1]} ⊢ ⍟ ¯4 ↑[2] ¯1↓[2] 10↑cnd
⍝ --- take log of ohlc


]display ((((0,⊢)∘(¯1∘↓) (+\(,¯1↑[2]⊢)))),⊢)⊢((1↓[2]⊢)-[1](⊂¨⍤,(1↑[2]⊢))) ⊢ 5↑  ⊢ ⍟ ¯4 ↑[2] ¯1↓[2] cnd


⍝  --- List pairs by exchange
xp←{(~⍵[;2]∊⊂'USDT') ⌿⍵} ⊢ ∪ tr[;3 4]

xp[;1]{⍺, ⊂ ⍵[;2],¨⊂'/USDT'}⌸xp[;1 2]

⍝ get timestamps for start and end of financial year/year+1
(¯1 12∘⎕DT) (,∘(4 6))¨ (1+⊢,⊢) 2022 

⍝ Transactions for particular year
⍴ tr { ((⍺[;1]>⍵[1])∧(⍺[;1]<⍵[2])) ⌿ ⍺ } (¯1 12∘⎕DT) (,∘(4 6))¨ (⊢,(1∘+)) 2022 

⍝ --- Load some candlesticks
cnd←kload⊢'./data-csv/binance/','ALGO','_USDT-1d.csv'

⍝ --- bring them in a parent namespace for charting
⎕CS 'Causeway' ⎕NS '' ⋄⎕CY 'sharpplot'   ⍝ copy all classes in a single namespace called "Causeway"


'InitCauseway' 'View' ⎕CY 'sharpplot'
InitCauseway ⍬   ⍝ initialise current namespace


sp←⎕NEW Causeway.SharpPlot                        ⍝ default size
sp.SetPenWidths(0.8,1.2)
⍝ sp.LineGraphStyle ← Causeway.LineGraphStyles.(TrendLine+OnTopModel)


sp←⎕NEW Causeway.SharpPlot                        ⍝ default size
sp.SetLineStyles(Causeway.LineStyle.(Solid))
sp.DrawLineGraph((⊂ ↓⍉c[;5 3 4 ]),(⊂c[;1]) )
sp.SaveSvg(⊂'sample.svg')

⍝ --------------------------------------------------

⍴¨ (ts o h l c v)←↓⍉ 300↑cnd
⍝ --- up or down
⍴ud←0,(1-2×4≤1∘↓-¯1∘↓) c
⍝ --- top or bottom
⍴  tb←((⊢×) (0, 2=/⊢)) ud


⍝ --- Rolling period high/low
⍴ h_←24 (((¯1+⊣)⍴(1↑⊢)),⊣⌈/⊢) h
⍴ l_←24 (((¯1+⊣)⍴(1↑⊢)),⊣⌊/⊢) l


sp←⎕NEW Causeway.SharpPlot                        ⍝ default size
sp.SetLineStyles(Causeway.LineStyle.(Solid))
sp.DrawLineGraph((⊂c h_ l_),⊂ts)
sp.SaveSvg(⊂'sample.svg')

⍝ 




