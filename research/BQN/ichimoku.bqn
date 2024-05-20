
⟨Gnuplot⟩ ← •Import "Gnuplot.bqn"

⟨JParse⇐Parse,JExport⇐Export⟩←•Import "bqn-libs/json.bqn"
⟨Split , Join,  SplitL, JoinL⟩←•Import "bqn-libs/csv.bqn"
⟨MP, Cholesky,Inverse⟩←•Import "bqn-libs/matrix.bqn"
#1‿1 MP 2‿2⥊4
⟨FmtNs, GLine, WMean, Ema, Var, WVar, WStd, GBars, CumBins, CumBinsPct, HBins, Hist, PHist⟩←•Import "pk-libs.bqn"


jsondir← "/media/mu6mula/Data/Crypto-Data-Feed/freq-user-data/data/binance/"
LdJson ←{ 
	>JParse •FChars jsondir∾(⊑𝕩)∾"_"∾(1⊑𝕩)∾"-"∾(𝕨)∾".json"
}
LdJsLc ← {⋆⁼ ¯2⊏˘ 𝕨 LdJson 𝕩‿"USDT"}

#3↑ ohlcv ← "8h" LdJson "AVAX"‿"USDT"
#10↑ 2‿3⊸⊏˘ ohlcv

#################################################################
### Ichimoku Cloud 
#################################################################
Ichimoku ← {
	tenkanN‿kijunN‿senkBN‿cloudN←𝕨⋄
	tenkan ← ÷⟜2 +´⌈‿⌊ {(0⥊˜tenkanN-1)∾𝕎 ˝˘ tenkanN↕𝕩}¨ ⋈˝⍉2‿3⊸⊏˘𝕩⋄
	kijun ← ÷⟜2 +´⌈‿⌊ {(0⥊˜kijunN-1)∾𝕎 ˝˘ kijunN↕𝕩}¨ ⋈˝⍉2‿3⊸⊏˘𝕩⋄
	senkouA ← (cloudN⥊0)» ÷⟜2 tenkan + kijun⋄
	senkouB ← (cloudN⥊0)» ÷⟜2 +´⌈‿⌊ {(0⥊˜senkBN-1)∾𝕎 ˝˘ senkBN↕𝕩}¨ ⋈˝⍉2‿3⊸⊏˘𝕩⋄
	tenkan‿kijun‿senkouA‿senkouB
}

XStra ← { 
	tenkanN‿kijunN‿senkBN‿cloudN←𝕨⋄
	ohlcv ← 𝕩⋄
#	tenkanN‿kijunN‿senkBN‿cloudN←20‿60‿120‿30 
	tenkan‿kijun‿senkouA‿senkouB ← tenkanN‿kijunN‿senkBN‿cloudN Ichimoku ohlcv
#	tenkan‿kijun‿senkouA‿senkouB ← 20‿60‿120‿30 Ichimoku ohlcv
	senkouUp‿senkouDn ← ⌈‿⌊ {𝕎 ´ 𝕩}¨ < senkouA‿senkouB
#	senkouUp ← senkouA ⌈ senkouB
#	senkouDn ← senkouA ⌊ senkouB


#PlotIchimoku ← {
#	base‿quote←𝕨⋄
#	timeframe←𝕩⋄
	
#	dcv ←500↑base‿quote LoadCandles timeframe⋄
	close←¯2⊏˘ohlcv⋄
	lnclose ← ⋆⁼ close
	xenter ← (close > senkouUp) ∧ (tenkan > kijun) ∧ (close > tenkan)
	xinsig ← (⊢∧(¬»)) xenter
	xexit ← (close < kijun)
	posinx⇐ /xinsig
	poslens⇐1↓(((+´∘¬∨`)))¨ (+`xinsig) ⊔ xexit
	posoutx⇐ ((≠ohlcv)-1)⌊posinx+poslens
	xio ⇐ (posinx≍posoutx) 
	cio ⇐ xio ⊏ close 
	pnl⇐--˝ ⋆⁼ cio
	¯3↑ cumpnl⇐+`pnl
	#⍉xio∾cio∾pnl≍cumpnl
}

#20‿60‿120‿30 XStra ohlcv

########################################
### Test TOP 100 coins 

top100←⟨"1000SATS","AAVE","ADA","ALGO","APT","ARB","ASTR","ATOM","AVAX","AXL","AXS","BCH","BLUR","BNB","BONK","BTC","CAKE","CFX","CHZ","DOGE","DOT","DYM","EGLD","ENJ","ENS","EOS","ETC","ETH","FIL","FLOW","FTM","GALA","GNO","GRT","HBAR","ICP","ILV","IMX","INJ","IOTA","JUP","KAVA","KLAY","KSM","LDO","LINK","LRC","LTC","LUNA","LUNC","MANA","MANTA","MATIC","MINA","MKR","NEAR","NEO","OP","ORDI","OSMO","PENDLE","PYTH","QNT","RNDR","ROSE","RUNE","SAND","SEI","SHIB","SNX","SOL","STX","SUI","THETA","TIA","TRX","UNI","USDC","VET","WOO","XLM","XRP","XTZ","ZIL"⟩
#(∾⟜"/USDT")¨ top100 
# 20‿60‿120‿30⊸XStra¨ "8h"⊸LdJson¨ (⋈⟜"USDT")¨ top100 
res ← top100 ≍˘{⊑¯1↑𝕩.cumpnl}¨ 20‿60‿120‿30⊸XStra¨ "8h"⊸LdJson¨ (⋈⟜"USDT")¨ top100 

( (⍋1⊸⊑˘)⊏⊢) res

3↑ ohlcv ← "8h" LdJson "AVAX"‿"USDT"

#	col‿bal‿lesA‿lesB ← 30‿60‿120 Ichimoku dcv⋄
	ixs ← ↕≠ohlcv⋄
#		multiplot layout 2,1 scale 2,1
	plt ← Gnuplot "
		title 'Ichimoku Cloud' font ',18'
		terminal wxt size 1800,900
		y2range [-1:10]
		y2tics 0.20 nomirror tc lt 2
		grid
		style line 5 lt rgb 'cyan' lw 3 pt 6"
	plt.Plot (⍉>ixs‿senkouA‿senkouB)‿" with filledcurves fs solid 0.1"
	plt.Plot (⍉>ixs‿close)‿"lw 1 lc rgb 'black' with lines"
	plt.Plot (⍉>ixs‿tenkan)‿"lw 1 lc rgb '#5555CC' with lines"
	plt.Plot (⍉>ixs‿kijun)‿"lw 1 lc rgb 'red' with lines"
	plt.Plot (⍉>ixs‿senkouA)‿"lw 1 lc rgb 'gray' with lines"
	plt.Plot (⍉>ixs‿senkouB)‿"lw 1 lc rgb 'gray' with lines"
	plt.Plot (⍉>posoutx‿cumpnl)‿"lw 5 lc rgb 'orange' with lines axes x1y2"
	"gnuplot-ichimoku-1.txt" •file.Chars plt.Debug @
	•SH "gnuplot"‿"-persist"‿"gnuplot-ichimoku-1.txt"
}
#"BTC"‿"USDT" PlotIchimoku "1d"
###
