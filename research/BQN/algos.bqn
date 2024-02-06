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

≢⍉dcv

⟨ts,op,hi,lo,cl,vo⟩←<˘⍉dcv
cl

∾˝0‿¯1↓0‿4↓dcv
#⟨<¯2⟩⊏¨dcv
⊑¯1↑¯1↓<˘⍉dcv
#################################################################
###  Technical Indicators 
#################################################################

### EMA 
Ema←{k←2÷1+𝕨⋄{(k×𝕩)+𝕨×1-k}`𝕩} 
ema50←50 Ema cl


ixs←(↕≠cl)
⍉>ixs‿cl
#pcl←⍉>(↕≠cl)‿cl‿ema50
#(↕⊑1↓≢ cl≍ema50
#pcl←⍉(((↕≠)≍⊢) cl)≍<ema50

⟨Gnuplot⟩ ← •Import "Gnuplot.bqn"

plt ← Gnuplot "
  title 'Price and EMA' font ',18'
	terminal wxt size 1300,600
	style line 5 lt rgb 'cyan' lw 3 pt 6
"

plt.Plot (⍉>ixs‿cl)‿"lw 0.5 lc rgb 'black' with lines"
plt.Plot (⍉>ixs‿ema50)‿"lw 0.5 lc rgb 'black' with lines"
# ZigZag like neurotrader


"gnuplot-example-1.txt" •file.Chars plt.Debug @

0.1 {𝕩} cl



#⟨4‿4,0‿∞⟩ ⊑ dcv


#hw←"h"
#hw↩"Hello "‿"World!"
#⥊¨hw

