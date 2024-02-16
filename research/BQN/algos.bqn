
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


csv ← "',/" •Import "./bqn-libs/csv.bqn"  # Easier characters to write
cldir ← "/media/grenada/Data/Crypto-Historical-Data/data-csv/binance/"

LoadCandles ← { 
	base‿quote←𝕨⋄
	timeframe←𝕩⋄
	>•ParseFloat¨¨ 1↓ csv.SplitL •FLines cldir ∾base∾"_"∾quote∾"-"∾timeframe∾".csv"⋄
}
#10↑⟨"BTC","USDT"⟩ LoadCandles "1d"


#################################################################
### Ichimoku Cloud 
#################################################################
Ichimoku ← {
	con‿ban‿bn←𝕨⋄
	col ← ÷⟜2 +´⌈‿⌊ {(0⥊˜con-1)∾𝕎 ˝˘ con↕𝕩}¨ ⋈˝⍉2‿3⊸⊏˘𝕩⋄
	bal ← ÷⟜2 +´⌈‿⌊ {(0⥊˜ban-1)∾𝕎 ˝˘ ban↕𝕩}¨ ⋈˝⍉2‿3⊸⊏˘𝕩⋄
	lesA ← (ban⥊0)» ÷⟜2 col + bal⋄
	lesB ← (ban⥊0)» ÷⟜2 +´⌈‿⌊ {(0⥊˜bn-1)∾𝕎 ˝˘ bn↕𝕩}¨ ⋈˝⍉2‿3⊸⊏˘𝕩⋄
	col‿bal‿lesA‿lesB
}

PlotIchimoku ← {
	base‿quote←𝕨⋄
	timeframe←𝕩⋄
	
	dcv ←500↑base‿quote LoadCandles timeframe⋄
	cl←¯2⊏˘dcv⋄
	col‿bal‿lesA‿lesB ← 30‿60‿120 Ichimoku dcv⋄
	ixs ← ↕≠dcv⋄
	plt ← Gnuplot "
		title 'Ichimoku Cloud' font ',18'
		terminal wxt size 1800,900
		style line 5 lt rgb 'cyan' lw 3 pt 6"
	plt.Plot (⍉>ixs‿lesA‿lesB)‿" with filledcurves fs solid 0.1"
	plt.Plot (⍉>ixs‿cl)‿"lw 1 lc rgb 'black' with lines"
	plt.Plot (⍉>ixs‿col)‿"lw 1 lc rgb '#5555CC' with lines"
	plt.Plot (⍉>ixs‿bal)‿"lw 1 lc rgb 'red' with lines"
	plt.Plot (⍉>ixs‿lesA)‿"lw 1 lc rgb 'gray' with lines"
	plt.Plot (⍉>ixs‿lesB)‿"lw 1 lc rgb 'gray' with lines"
	"gnuplot-ichimoku-1.txt" •file.Chars plt.Debug @
	•SH "gnuplot"‿"-persist"‿"gnuplot-ichimoku-1.txt"
}
#"BTC"‿"USDT" PlotIchimoku "1d"
###

#################################################################
### Directional Change / ZigZag Algorithm 
#################################################################
IfElse ← {cond‿True‿False: cond◶False‿True @}
TestConds ← {fn←{Cond‿Act 𝕊 else: Cond◶Else‿Act}´𝕩 ⋄ Fn@}
cl← ⋆⁼ ¯2⊸⊏˘ "BTC"‿"USDT" LoadCandles "1d"
Peaks ← {
	qdc←𝕨⋄
	1↓⌽¯1⊑(0‿1‿0‿(⊑𝕩)‿(≍0‿0)) {
		ix‿dir‿xi‿xp‿evx←𝕩
		p←𝕨
		nacc← TestConds ⟨
			(0<dir×p-xp)‿		{𝕤⋄dir‿ix‿p‿evx}		# Continues in the same direction as before, update xi & xp
			{qdc≥dir×-p-xp}‿	{𝕤⋄dir‿xi‿xp‿evx}		# Opposite direction, below threshold, keep previous xi & xp
											{𝕤⋄(-dir)‿ix‿p‿((xi‿dir)∾evx)} # Opposite direction, above threshold, change direction
		⟩
		(ix+1)∾nacc
	}´ ⌽𝕩⋄
}
pks ← 0.20 Peaks cl 
pix←0⊑˘pks
pcpix←pix⊸⊏cl
0.15>|-˝pcpix≍»pcpix
ixs←↕≠cl
plt ← Gnuplot "
	title 'ZigZag Algorithm' font ',18'
	terminal wxt size 1800,900
	style line 1 lt rgb 'black' lw 1"
plt.Plot (⍉>pix‿pcpix)‿" lw 2 lc rgb 'red' pt 7 ps 3"
plt.Plot (⍉>ixs‿cl)‿"lw 1 lc rgb 'black' with lines"
"gnuplot-zigzag-1.txt" •file.Chars plt.Debug @
•SH "gnuplot"‿"-persist"‿"gnuplot-zigzag-1.txt"
18541.28 ÷ 18325.11 -1 






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
 
