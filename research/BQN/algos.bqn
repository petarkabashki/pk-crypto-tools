
⟨Gnuplot⟩ ← •Import "Gnuplot.bqn"

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
# https://jonisalonen.com/2013/deriving-welfords-method-for-computing-variance/
Var←{n‿m‿s←1‿0‿0{
  k‿m‿s←𝕩⋄
    newM←m+(𝕨-m)÷k⋄
	  (k+1)‿newM‿(s+(𝕨-newM)×(𝕨-m))
	}´⌽𝕩⋄
	s÷n-1}
 Var 10÷˜1+↕2
Var ⋆⟜1.2 ↕20
⊑2+↕10

### ROlling Variance, tested against Pandas.rolling().var(ddof=1)
# Source: https://jonisalonen.com/2014/efficient-and-accurate-rolling-standard-deviation/
# Another similar algorithm here () https://www.dfki.de/fileadmin/user_upload/import/7051_131008_Memory_and_Processing_Efficient_Formula_for_Moving_Variance_Calculation_in_EEG_and_EMG_Signal_Processing_NEUROTECHNIX_Krell.pdf
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

#-⟜» 
### Bins and Quantiles

### 𝕩-step bin values, right-side ≤ of bins
QBins ← {so←∧𝕩⋄
	sta‿end←0‿¯1⊏so⋄
  ls←sta+(1+↕𝕨)×(end-sta)÷𝕨⋄
	cux←+˝so≤⌜ls⋄
	(cux-1)⊏so
} 
3 QBins ↕12

### Divides values into 𝕨 bins and outputs the right-side (≤) edges
VBins ← {so←∧𝕩⋄
	sta‿end←0‿¯1⊏so⋄
  ls←sta+(1+↕𝕨)×(end-sta)÷𝕨⋄
	tv←-⟜» cux←+˝so≤⌜ls⋄ #number of values to take into every bin
	tv /⊸⊔ so
	#(cux-1)⊏so
}
### Histogram
4 
20 {
nb←>(+´(÷⋈⊢)≠)¨ 𝕨 VBins 𝕩
plt ← Gnuplot "
  title 'Histogram' font ',18'
	terminal wxt size 1300,600
	style line 5 lt rgb 'cyan' lw 3 pt 6
"
plt.Plot nb‿"using 1:2 with boxes fillstyle pattern 5 title ''"
"gnuplot-histogram-1.txt" •file.Chars plt.Debug @
•SH "gnuplot"‿"-persist"‿"gnuplot-histogram-1.txt"
} 2000+ ⋆⟜3 ¯5000+↕10000

 #3 {b←𝕨 Bins 𝕩⋄-⟜»b} ↕12
#3 VBins ↕12# ⋆⟜2 ÷⟜10 ¯50+ ↕101

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

stds ← 14 WStd cl
ixs←(↕≠cl)
⍉>ixs‿cl
emaBo ← 21 Ema cl
boL‿boH ← (<emaBo) +˘ ⟨¯1,1⟩×¨<stds
#≠bol
cl
#⍉>ixs‿emaBo

plt ← Gnuplot "
  title 'Price and EMA' font ',18'
	terminal wxt size 1300,600
	style line 5 lt rgb 'cyan' lw 3 pt 6
"
4↑⍉>ixs‿cl
plt.Plot (⍉>ixs‿cl)‿"lw 0.5 lc rgb 'blue' with lines"
plt.Plot (⍉>ixs‿emaBo)‿"lw 0.5 lc rgb 'black' with lines"
plt.Plot (⍉>ixs‿boL)‿"lw 0.5 lc rgb 'green' with lines"
plt.Plot (⍉>ixs‿boH)‿"lw 0.5 lc rgb 'red' with lines"
# ZigZag like neurotrader


"gnuplot-example-1.txt" •file.Chars plt.Debug @

0.1 {𝕩} cl



#⟨4‿4,0‿∞⟩ ⊑ dcv


#hw←"h"
#hw↩"Hello "‿"World!"
#⥊¨hw
 
