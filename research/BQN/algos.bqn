
#################################################################
###  Statistical Functions
#################################################################

### Rolling Mean, tested against Pandas .rolling().mean()
WMean← {+`(𝕩-(-𝕨)↓(𝕨⥊0)∾𝕩)÷𝕨}
2 WMean 1+↕100
1+↕100
¯4↑3 WMean ⋆⟜1.2 ↕20

### EMA 
Ema←{k←2÷1+𝕨⋄{(k×𝕩)+𝕨×1-k}`𝕩} 
50 Ema ↕1e1

### Variance Welford's method, tested against Numpy np.var([])
Var←{n‿m‿s←1‿0‿0{
  k‿m‿s←𝕩⋄
    newM←m+(𝕨-m)÷k⋄
	  (k+1)‿newM‿(s+(𝕨-newM)×(𝕨-m))
	}´⌽𝕩⋄
	s÷n-1}
 Var 10÷˜1+↕2
Var ⋆⟜1.2 ↕20
⊑2+↕10

### Rolling Variance
⋆⟜1.2 ↕20
⊑⊸» 1+↕10
(»+⊢) 1+↕10


#2 {v←Var 𝕨↑𝕩⋄
# m1←⊑⊸» 𝕨 WMean 𝕩⋄
# x0←(𝕨⥊0)»𝕩⋄
# s1←(𝕩-x0)⋄
# s2←(𝕩×(𝕨-1)÷𝕨) + (x0×(𝕨+1)÷𝕨) -2×m0⋄
# (𝕨-1)÷˜(v×𝕨-1)`+𝕨↓s1×s2⋄
 #s2⋄
#} ⋆⟜1.2 ↕20

### ROlling Variance, tested against Pandas.rolling().var(ddof=1)
WVar ← {v←Var 𝕨↑𝕩⋄
 mm←(»+⊢) 𝕨 WMean 𝕩⋄
 x0←(𝕨⥊0)»𝕩⋄
 z←(𝕩-x0)×(𝕩+x0-mm)⋄
 (0⥊˜𝕨-1)∾ (𝕨-1)÷˜ +`(v×𝕨)∾𝕨↓z⋄
} 
3 WVar ⋆⟜1.2 ↕20
### Rolling Std, Tested against Pandas.rolling(w).std(ddof=1)
WStd ← √∘WVar

¯4↑3 WStd ⋆⟜1.2 ↕20

 #Var←{n‿m‿s←1‿0‿0{k‿m‿s←𝕩⋄oldM←m⋄m↩m+(𝕨-m)÷k⋄s↩s+(𝕨-m)×(𝕨-oldM)⋄(k+1)‿m‿s}´⌽𝕩⋄s÷n-1}
 #Var (⊢÷≠)↕30

csv ← "',/" •Import "./bqn-libs/csv.bqn"  # Easier characters to write

lines ← •FLines "ALGO_USDT-1d.csv"
≢lines
c ← csv.SplitL lines
ch←1↑c
cv←1↓c
#cv← •ParseFloat¨¨  1↓c
cv •ParseFloat¨¨↩

↑10↑cv
dcv←>cv
4↑dcv
((↕≠)∾˘⊢)dcv
≢⍉dcv

⟨ts,op,hi,lo,cl,vo⟩←<˘⍉dcv
cl
≢dcv
≠dcv
≢0‿¯1↓0‿1↓dcv
∾˝0‿¯1↓0‿4↓dcv
#⟨<¯2⟩⊏¨dcv
⊑¯1↑¯1↓<˘⍉dcv
#################################################################
###  Technical Indicators 
#################################################################


ixs←(↕≠cl)
⍉>ixs‿cl
ema50 ← 21 Ema cl
cl
std ←  2 WVar cl
#pcl←⍉>(↕≠cl)‿cl‿ema50
#(↕⊑1↓≢ cl≍ema50
#pcl←⍉(((↕≠)≍⊢) cl)≍<ema50

⟨Gnuplot⟩ ← •Import "Gnuplot.bqn"

plt ← Gnuplot "
  title 'Price and EMA' font ',18'
	terminal wxt size 1300,600
	style line 5 lt rgb 'cyan' lw 3 pt 6
"
4↑⍉>ixs‿cl
plt.Plot (⍉>ixs‿cl)‿"lw 0.5 lc rgb 'blue' with lines"
plt.Plot (⍉>ixs‿ema50)‿"lw 0.5 lc rgb 'red' with lines"
# ZigZag like neurotrader


"gnuplot-example-1.txt" •file.Chars plt.Debug @

0.1 {𝕩} cl



#⟨4‿4,0‿∞⟩ ⊑ dcv


#hw←"h"
#hw↩"Hello "‿"World!"
#⥊¨hw

