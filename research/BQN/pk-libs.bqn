# Comma-separated values (.csv)
⟨
  FmtNs, GLine, WMean , Ema, Var, WVar, WStd, GBars, CumBins, CumBinsPct, HBins, Hist, PHist, Resample, Round
⟩⇐


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

GBars ← {
	plt ← Gnuplot "
		title '"∾𝕨∾"' font ',18'
		terminal wxt size 1300,600
		style line 5 lt rgb 'cyan' lw 3 pt 6"
	plt.Plot 𝕩‿"using 1:2 with boxes fillstyle pattern 5 title ''"
	"gnuplot-histogram-1.txt" •file.Chars plt.Debug @
	•SH "gnuplot"‿"-persist"‿"gnuplot-histogram-1.txt"
} 
### Cumulative Bins aka Cumulative Probability Density
CumBins ← {
	so←∧𝕩⋄
	sta‿end←0‿¯1⊏so⋄
  ls←sta+((1e¯3÷𝕨)+1+↕𝕨)×(end-sta)÷𝕨⋄
	cux←+˝so≤⌜ls⋄
	cux ≍ ls
} 
#⌽˘⍉50 CumBins 1000÷˜1+↕100

### Cumulative Distribution Diagram
#"Cumulative Counts" GBars ⌽˘⍉50 CumBins 1000÷˜ ⋆⟜1.8 1+↕100
 CumBinsPct ← (((⊢÷⟨¯1⟩⊸⊑)0⊸⊏)≍1⊸⊏)∘CumBins 
#⍉500 CumBinsPct 1+↕100
#"Cumulative Percentage" GBars ⌽˘⍉50 CumBinsPct ⋆⟜2.5 1+↕100
### Bins aka Distribution Histogram
HBins ← {
	so←∧𝕩⋄
	sta‿end←0‿¯1⊏so⋄
  ls←sta+((1e¯3÷𝕨)+1+↕𝕨)×(end-sta)÷𝕨⋄
	cux←+˝so≤⌜ls⋄
	tv←-⟜» cux⋄ #number of values to take into every bin
	tv /⊸⊔ so⋄
}

#20 HBins ⋆⟜2 ↕10
### Histogram
Hist ← "Histogram" GBars (>(+´(÷⋈⊢)≠)¨)∘HBins 
#100 Hist  ⋆⟜2 ↕10
	
### Histogram in %
#30 (⍉∘>∘((0⊸⊏)≍((⊢÷+´)1⊸⊏))∘⍉∘>(+´(÷⋈⊢)≠)¨)∘HBins 2000+ ⋆⟜3 ¯5000+↕10000

PHist ← "Histogram" GBars (⍉∘>∘((0⊸⊏)≍((⊢÷+´)1⊸⊏))∘⍉∘>(+´(÷⋈⊢)≠)¨)∘HBins 
#30 PHist 2000+ ⋆⟜3 ¯5000+↕10000

GLine← {
	plt ← Gnuplot "
		title 'Line plot' font ',18'
		terminal wxt size 1300,600
		style line 5 lt rgb 'cyan' lw 5 pt 6"
	plt.Plot (((↕≠)∾˘⊢)𝕩)‿"lw 1 lc rgb 'blue' with lines"
	"gnuplot-tmp-1.txt"•file.Chars plt.Debug @
	•SH "gnuplot"‿"-persist"‿"gnuplot-tmp-1.txt"
}

### Format a namespace into a table of key/values
FmtNs ← {k←•ns.Keys 𝕩⋄⍉k≍𝕩 •ns.Get¨k}

### Resample / Downsample OHLC 
Resample ← { > {⊑‿⊑‿(⌈´)‿(⌊´)‿(¯1⊸⊑) {𝕎 𝕩}¨ <˘ ⍉ 𝕩}¨ <˘ 𝕨 {r‿c←≢𝕩⋄((⌊r÷𝕨)‿𝕨‿c)⥊𝕩} 𝕩}
# 3 Resample "8h" LgLoad "ADA"

### Round 𝕩 to 𝕨 decimal places
Round ← ((10⊸⋆⊣) ((⌊0.5⊸+∘×)÷⊣) ⊢)
# 3 Round 0.16666666
