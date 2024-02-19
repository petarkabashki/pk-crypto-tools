
⟨Gnuplot⟩ ← •Import "Gnuplot.bqn"

⟨JParse⇐Parse⟩←•Import "bqn-libs/json.bqn"
⟨WMean, Ema, Var, WVar, WStd, GBars, CumBins, CumBinsPct, HBins, Hist, PHist⟩←•Import "pk-libs.bqn"

csv ← "',/" •Import "./bqn-libs/csv.bqn"  # Easier characters to write
csvdir ← "/media/grenada/Data/Crypto-Historical-Data/data-csv/binance/"

LdCsv ← { 
	base‿quote←𝕨⋄
	timeframe←𝕩⋄
	>•ParseFloat¨¨ 1↓ csv.SplitL •FLines csvdir ∾base∾"_"∾quote∾"-"∾timeframe∾".csv"⋄
}
#10↑⟨"BTC","USDT"⟩ LoadCandles "1d"

jsondir←"/media/grenada/Data/Crypto-Data-Feed/freq-user-data/data/binance/"
LdJson ←{ 
	>JParse •FChars jsondir∾(⊑𝕩)∾"_"∾(1⊑𝕩)∾"-"∾(𝕨)∾".json"
}

#################################################################
### Calman Filter 
###############################################################
3↑tkls← "8h" LdJson "AVAX"‿"USDT"
3↑ lcl← ⋆⁼ 1↓˘ ¯1↓˘ tkls
cl←¯1⊏˘lcl
errmea←0.1
### GH-Filter aka Kalman Filter
GHF←{
	dt‿g‿h←𝕨
	(<(2⥊⊑cl)∾0){
		z←𝕩
		p_pred‿x_est‿dx←𝕨
		# prediction step
		x_pred←x_est + dx×dt
		# update step
		resid←z-x_pred
		x_pred‿(x_pred + g×resid÷dt)‿(dx+h×resid÷dt)
	} ` 𝕩 
} 
XPos ← {
	cl‿klm←𝕩⋄abv←cl>klm⋄crup←∧⟜(¬»)abv⋄crdn←∧⟜(¬1⊸»)¬abv⋄
	ixpos←crup (>∘{m←⌊´≠¨𝕩⋄m↑¨𝕩}∘⋈○/) crdn
	clpos←ixpos ⊏ cl
	dr← 0>  -˝(⊢⊏⟜klm) (⊢≍-⟜2) (⊏ixpos)	
	pnl ← dr× --˝ clpos
	cumpnl ← +`pnl
	pnl≍cumpnl
	ixpos‿clpos‿(pnl≍cumpnl)
}
#wixpos←sks↓˘ske↓˘ixpos ⋄ wclpos←sks↓˘ske↓˘clpos⋄ wpnls←sks↓˘ske↓˘pnls
GLine← {
	ws‿ww←𝕨
	plt ← Gnuplot "
		title 'Line plot' font ',18'
		terminal wxt size 1300,600
		style line 5 lt rgb 'cyan' lw 5 pt 6"
	plt.Plot (ww↑ws↓((↕≠)∾˘⊢)𝕩)‿"lw 1 lc rgb 'blue' with lines"
	"gnuplot-tmp-1.txt"•file.Chars plt.Debug @
	•SH "gnuplot"‿"-persist"‿"gnuplot-tmp-1.txt"
}
Btest ← {
	ghpars‿wsw←𝕨⋄ws‿ww←wsw⋄cl←𝕩⋄
	klm←> (1⊸⊏˘>)¨  (<ghpars) (GHF)¨ <cl
	ixpos‿clpos‿pnls ← XPos cl‿klm
	ts←↕≠tkls
	sks‿ske← ws‿ww{ws‿ww←𝕨⋄((-+´(ws+ww)<1⊸⊏𝕩))‿(+´ws>⊏𝕩)} ixpos
	wixpos‿wclpos‿wpnls←(ske⊸↓˘ sks⊸↓˘)¨ixpos‿clpos‿pnls
	plt ← Gnuplot "
		title 'G-H Filter' font ',18'
		terminal wxt size 1300,600
		y2tics nomirror tc lt 2
		style line 5 lt rgb 'cyan' lw 5 pt 6
		style fill empty"
	xs←plt.Debug @
	plt.Plot (ww↑ws↓ts∾˘cl)‿"lw 1 lc rgb 'blue' with lines"
	plt.Plot (ww↑ws↓ts∾˘klm)‿"lw 1.5 with lines"
	plt.Plot (⍉>¯1⊸⊏¨wixpos‿wpnls)‿"lc rgb 'red' lw 1.5 with lines axes x1y2"
	"gnuplot-tmp-1.txt"•file.Chars plt.Debug @
	•SH "gnuplot"‿"-persist"‿"gnuplot-tmp-1.txt"
	klm‿ixpos‿clpos‿pnls‿wixpos‿wclpos‿wpnls
} 

klm‿ixpos‿clpos‿pnls‿wixpos‿wclpos‿wpnls←(0.001‿0.00001‿0.000007)‿(0‿(≠cl))  Btest cl
¯10↑¨wpnls
ys2tics 20 nomirror tc lt 2

















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
	⌽¯1⊑(0‿1‿0‿(⊑𝕩)‿(≍0‿0)) {
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
 
