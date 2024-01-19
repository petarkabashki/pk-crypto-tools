


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



⍝ ---------------------------------------
⍝ --- Load candlesticks
⍝ ---
fldb←'/media/grenada/Data/Accounting/pk-crypto-tax-calculator/data-csv/binance/'
k←kload⊢fldb,'ALGO','_USDT-4h.csv'
]display 10↑ kl← ¯1↓[2] 1↓[2] k


]display  (({|⍵[;2]-0,1↓⍵[;4]}⍪[0.5] {|-/⍵[;3 2]}))  10↑kl

]display  {⍵[;2 3]-[1]0,1↓⍵[;4]}  10↑kl




10↑ lk← ⍟ (⊂2 3 4 5)⌷[2] k ⍝ take log of ohlc
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
⍝ --- Technical Indicators
⍝ ------------------------------------------------------------
⍝ --- True range
tr←{⌈/|(-/⍵[;2 3]),⍵[;2 3]-[1]0,1↓⍵[;4]}  

⍝ ATR
]display  14(⊣{n←⍺⋄⌽⊃{(n÷⍨⍺+(n-1)×⊃⍵),⍵}/⍵}(⌽(⊂⊣⍴(+/⊣↑⊢)÷⊣),(⊣↓⊢))) tr kl

]display 30↑  14(⊣{n←⍺⋄⌽⊃{(n÷⍨⍺+(n-1)×⊃⍵),⍵}/⍵}(⌽(⊂⊣⍴(+/⊣↑⊢)÷⊣),(⊣↓⊢))) tr kl


]display 14{n←⍺⋄⌽⊃{(n÷⍨⍺+(n-1)×⊃⍵),⍵}/⊢ ⌽⊢((n↑⊢),(n↓⊢)) ⍵} 50↑ tr kl


⍝ --- EMA
ema← {k←2÷1+⍺⋄⌽⊃{((k×⍺)+(1-k)×⊃⍵),⍵}/⊢ ⌽⊢((⊂1↑⊢),(1↓⊢)) ⍵}
⍝ --- EMA like in pandas_ta
ema← ((( ⊢,1∘-)(2÷1+⊣)) {am←⍺⋄⌽⊃{(am +.× (⍺, ⊃⍵)),⍵}/ ⌽ (⊂⍵[1]),1↓⍵} (⊣((⊣⍴((+/↑)÷⊣)),↓)⊢))

]display 4  ((( 1∘-,⊢)(2÷1+⊣)) {am←⍺⋄⌽{(am +.× (⍺, ⊃⍵)),⍵}/ ⌽⍵} ((⊂1↑⊢),(1↓⊢))) ⍳20 


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




