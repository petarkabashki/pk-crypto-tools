
⟨Gnuplot⟩ ← •Import "Gnuplot.bqn"
csv←•Import "bqn-libs/csv.bqn"
str←•Import "bqn-libs/strings.bqn"
⟨JParse⇐Parse,JExport⇐Export⟩←•Import "bqn-libs/json.bqn"
⟨Split , Join,  SplitL, JoinL⟩←•Import "bqn-libs/csv.bqn"
⟨MP, Cholesky,Inverse⟩←•Import "bqn-libs/matrix.bqn"
#1‿1 MP 2‿2⥊4
⟨FmtNs, GLine, WMean, Ema, Var, WVar, WStd, GBars, CumBins, CumBinsPct, HBins, Hist, PHist⟩←•Import "pk-libs.bqn"


NFmt ← ⟨"¯"⟩‿⟨"-"⟩⊸str.ReplaceAll ∘ •Fmt
TFmt ← {r←𝕩⋄⍉>𝕨 {𝕎¨ 𝕩⊏˘r}¨ (↕≠𝕨)}
jsondir← "/media/mu6mula/Data/Crypto-Data-Feed/freq-user-data/data/binance/"
LdJson ←{ 
	>JParse •FChars jsondir∾(⊑𝕩)∾"_"∾(1⊑𝕩)∾"-"∾(2⊑𝕩)∾".json"
}
LdJsLc ← {⋆⁼ ¯2⊏˘ 𝕨 LdJson 𝕩‿"USDT"}
Qcsv ← (⊣•FLines⟜(csv.JoinL NFmt¨)) 

#3↑ lohlcv ← (⊑˘ ∾˘ (⋆⁼1‿2‿3‿4⊸⊏˘)) LdJson "AVAX"‿"USDT"‿"8h" 
#10↑ 2‿3⊸⊏˘ ohlcv
#10↑ klines ← LdJson (<⊸∾⟜("USDT"‿"1d")) "ETH"
#10↑¨ ((((««)∾˘») (0‿0∾2⊸↕) ))¨ 2‿3 ⊏˘¨ <klines 
#h‿l ← 2‿3 ⊏˘¨ <klines 
#10↑ ∾˘´ c5h‿c5l ← ⌈‿⌊ { 𝕎 ´˘ 𝕩 }¨ ((((««)∾˘») (0‿0∾2⊸↕) ))¨ h‿l


#################################################################
### Ichimoku Cloud 
#################################################################
XIndicators ← {
	klines ← 𝕩
	tenkanN‿kijunN‿senkBN‿cloudN←𝕨⋄
#	tenkanN‿kijunN‿senkBN‿cloudN←20‿60‿120‿30
	tenkan ⇐ ÷⟜2 +´⌈‿⌊ {(0⥊˜tenkanN-1)∾𝕎 ˝˘ tenkanN↕𝕩}¨ ⋈˝⍉2‿3⊸⊏˘klines⋄
	kijun ⇐ ÷⟜2 +´⌈‿⌊ {(0⥊˜kijunN-1)∾𝕎 ˝˘ kijunN↕𝕩}¨ ⋈˝⍉2‿3⊸⊏˘klines⋄
	senkouA ⇐ (cloudN⥊0)» ÷⟜2 tenkan + kijun⋄
	senkouB ⇐ (cloudN⥊0)» ÷⟜2 +´⌈‿⌊ {(0⥊˜senkBN-1)∾𝕎 ˝˘ senkBN↕𝕩}¨ ⋈˝⍉2‿3⊸⊏˘klines⋄
#	tenkan‿kijun‿senkouA‿senkouB
	c5h‿c5l ← ⌈‿⌊ { 𝕎 ´˘ 𝕩 }¨ ((((««)∾˘») (0‿0∾2⊸↕) ))¨ h‿l ← 2‿3 ⊏˘¨ <klines 
	wfra⇐ ⊑ +´ 1‿¯1 ×¨ wfh‿wfl ← >‿< {𝕎 ˝𝕩}¨ h‿l ⋈¨ c5h‿c5l
}

#≢klines
#≢ wfra ← {𝕩.wfra} 20‿60‿120‿30 XIndicators klines
#(wfra > 0 ) / 3↑˘klines
#20‿60‿120‿30 XIndicators lohlcv ←  LdJson "AVAX"‿"USDT"‿"8h" 

XStra ← { 
	skipN ← 𝕨
	⟨klines,indicators⟩ ← 𝕩
	⟨tenkan,kijun,senkouA,senkouB⟩ ← indicators
	ixs ← ↕≠klines
	senkouUp‿senkouDn ← ⌈‿⌊ {𝕎 ´ 𝕩}¨ < senkouA‿senkouB
	close←¯2⊏˘klines⋄ # lnclose ← ⋆⁼ close
	xinsig ⇐ (skipN < ixs) ∧ (tenkan > kijun) ∧ (close > senkouUp) ∧ (close > tenkan)
	xenter ⇐ (⊢∧(¬»)) xinsig

	xexit ←  (close < senkouUp)   #∨ (tenkan < kijun)
	posinx⇐ /xenter
	poslens⇐1↓(((+´∘¬∨`)))¨ (+`xenter) ⊔ xexit
	posoutx⇐ ((≠klines)-1)⌊posinx+poslens
	xio ⇐ (posinx≍posoutx) 
	cio ⇐ xio ⊏ close 
	pnl⇐--˝ ⋆⁼cio
	cumpnl⇐+`pnl
}

XStats ⇐ {
		⟨pnl,cumpnl⟩ ← 𝕩
		ret⇐¯1⊑0∾cumpnl
		ntrades⇐≠pnl⋄nwins⇐+´pnl>0⋄nlosses⇐ntrades-nwins⋄winratio⇐nwins÷ntrades⋄
		wins←(0⊸<⊸/)pnl⋄losses←(0⊸≥⊸/)pnl⋄avgwin⇐(+´÷≠)wins⋄avgloss⇐(+´÷≠)losses⋄
		bottompnl⇐⌊´cumpnl
		maxpnl←⌈`cumpnl
		ddn←-maxpnl-cumpnl
		maxddn⇐⌊´ddn
		vol⇐√Var pnl
		sharpe⇐ret÷vol
		toppnl⇐⌈´maxpnl
 	#stats⇐>⟨"#Trades:"‿ntrades, "#Wins:"‿nwins⟩
 	#•Show cumpnl
	#XRun ⇐ {XStats XPositions XExits XEntries 𝕨 XIndicators Xload 𝕩}
}

#{"[0:100] " ∾ (NFmt 𝕩)∾",t lw 1 lc rgb 'black' axes x1y1"}¨ ↕5
#≍⟨⟩
		
⟨klines,indicators,res⟩←{⟨klines,indicators⟩⇐𝕩⋄res⇐120⊸XStra 𝕩} {klines⇐𝕩⋄indicators ⇐ (20‿60‿120‿30⊸XIndicators 𝕩)} LdJson "ETH"‿"USDT"‿"1d"
ws‿pwl ← 500‿200
#wl← pwl⌊ (≠klines) - ws
#Ww←(wl⊸↑ws⊸↓) ⋄ Wi ← (({∧´ (≥⟜ws)‿((ws+wl)⊸≥) {𝕎 𝕩}¨ 𝕩} (<⊑˘))⊸/)
#PlotSingle ← { 𝕤
#	⟨klines,indicators,res⟩← 𝕩⋄ 	ws‿pwl ← 𝕨⋄
	⟨tenkan,kijun,senkoua,senkoub,wfra⟩ ← indicators
	#(0⊏res.xio)≍(0⊏res.cio)
	ts‿open‿high‿low‿close‿volume ←<˘⍉ klines
	wl← pwl⌊ (≠klines) - ws
	Ww←(wl⊸↑ws⊸↓) ⋄ Wi ← (({∧´ (≥⟜ws)‿((ws+wl)⊸≥) {𝕎 𝕩}¨ 𝕩} (<⊑˘))⊸/)
	posCloud ← senkouA > senkouB
	ymin ← ⌊´Ww low⋄ymax← ⌈´Ww high
	#close←¯2⊏˘klines⋄ # lnclose ← ⋆⁼ close
		ixs ← ↕≠klines⋄
		plt ← Gnuplot "
			title 'Ichimoku Cloud' font ',18'
			terminal wxt size 2400,900
			y2tics 0.20 nomirror tc lt 2
			xrange ["∾(NFmt ws)∾":"∾(NFmt ws+wl-1)∾"]
			yrange ["∾(NFmt ymin)∾":"∾(NFmt ymax)∾"]
			y2range [-1:10]
			grid
			parametric
			style line 5 lt rgb 'cyan' lw 3 pt 6"
		plt.Plot (Ww ⍉>ixs‿senkouA‿senkouB)‿" with filledcurves fs solid 0.1"
		#plt.Plot (Wi (posCloud/⍉>ixs‿senkouA‿senkouB))‿"lc rgb 'green' with filledcurves fs solid 0.1"
		#plt.Plot (Wi ((¬posCloud)/⍉>ixs‿senkouA‿senkouB))‿"lc rgb 'red' with filledcurves fs solid 0.1"
		plt.Plot (Ww ⍉>ixs‿close)‿"lw 2 lc rgb 'black' with lines"
#		#plt.Plot (⍉>ixs‿high)‿"lw 1 lc rgb 'orange' with lines"
#		#plt.Plot (⍉>ixs‿low)‿"lw 1 lc rgb 'green' with lines"
		plt.Plot (Ww ⍉>ixs‿tenkan)‿"lw 1 lc rgb '#5555CC' with lines"
		plt.Plot (Ww ⍉>ixs‿kijun)‿"lw 1 lc rgb 'red' with lines"
		plt.Plot (Ww ⍉>ixs‿senkouA)‿"lw 1 lc rgb 'gray' with lines"
		plt.Plot (Ww ⍉>ixs‿senkouB)‿"lw 1 lc rgb 'gray' with lines"
		plt.Plot (Wi ⍉>res.posoutx‿res.cumpnl)‿"lw 5 lc rgb 'orange' with steps axes x1y2"
		plt.Plot (Wi ⍉ (0⊏res.xio)≍(0⊏res.cio))‿"lw 5 lc rgb 'black' with points"
		plt.Plot (Wi (0<res.pnl)/ ⍉(1⊏res.xio)≍(1⊏res.cio))‿"lw 4 lc rgb 'green' with points"
		plt.Plot (Wi (0≥res.pnl)/ ⍉(1⊏res.xio)≍(1⊏res.cio))‿"lw 4 lc rgb 'red' with points"
		{plt.Plot "" ∾ (NFmt 𝕩)∾",t lw 2 lc rgb 'black' axes x1y1"}¨ (Wi (0⊏res.xio))
		{plt.Plot (NFmt 𝕩)∾",t lw 2 lc rgb 'green'"}¨ Wi (0<res.pnl)/ ⍉(1⊏res.xio)≍(1⊏res.cio)
		{plt.Plot (NFmt 𝕩)∾",t lw 2 lc rgb 'red'"}¨ (Wi (0≥res.pnl)/ ⍉(1⊏res.xio)≍(1⊏res.cio))
#		plt.Plot (Wi (0<wfra)/(⍉>ixs‿high))‿"lw 3 lc rgb 'gray' with points"
#		plt.Plot (Wi (0>wfra)/(⍉>ixs‿low))‿"lw 3 lc rgb 'gray' with points"
		#plt.Plot ((0≥wfra)/ ⍉(1⊏res.xio)≍(1⊏res.cio))‿"lw 4 lc rgb 'red' with points"
		#plt.Plot (⟨⟩)‿"[0:1] 703,t lw 1 lc rgb 'blue'"
		"gnuplot-ichimoku-1.txt" •file.Chars plt.Debug @
		•SH "gnuplot"‿"-persist"‿"gnuplot-ichimoku-1.txt"
}
1000‿700 PlotSingle {⟨klines,indicators⟩⇐𝕩⋄res⇐120⊸XStra 𝕩} {klines⇐𝕩⋄indicators ⇐ (20‿60‿120‿30⊸XIndicators 𝕩)} LdJson "ADA"‿"USDT"‿"1d"


########################################
### Test TOP 100 coins 

top100←⟨"1000SATS","AAVE","ADA","ALGO","APT","ARB","ASTR","ATOM","AVAX","AXL","AXS","BCH","BLUR","BNB","BONK","BTC","CAKE","CFX","CHZ","DOGE","DOT","DYM","EGLD","ENJ","ENS","EOS","ETC","ETH","FIL","FLOW","FTM","GALA","GNO","GRT","HBAR","ICP","ILV","IMX","INJ","IOTA","JUP","KAVA","KLAY","KSM","LDO","LINK","LRC","LTC","LUNA","LUNC","MANA","MANTA","MATIC","MINA","MKR","NEAR","NEO","OP","ORDI","OSMO","PENDLE","PYTH","QNT","RNDR","ROSE","RUNE","SAND","SEI","SHIB","SNX","SOL","STX","SUI","THETA","TIA","TRX","UNI","USDC","VET","WOO","XLM","XRP","XTZ","ZIL"⟩
binance1d ← ⟨"1000SATS","1INCH","AAVE","ACA","ACE","ACH","ACM","ADA","ADX","AERGO","AEUR","AEVO","AGIX","AGLD","AI","AKRO","ALCX","ALGO","ALICE","ALPACA","ALPHA","ALPINE","ALT","AMB","AMP","ANKR","APE","API3","APT","ARB","ARDR","ARKM","ARK","ARPA","AR","ASR","ASTR","AST","ATA","ATM","ATOM","AUCTION","AUDIO","AVA","AVAX","AXL","AXS","BADGER","BAKE","BAL","BAND","BAR","BAT","BB","BCH","BEAMX","BEL","BETA","BICO","BIFI","BLUR","BLZ","BNB","BNT","BNX","BOME","BOND","BONK","BSW","BTC","BTTC","BURGER","C98","CAKE","CELO","CELR","CFX","CHESS","CHR","CHZ","CITY","CKB","CLV","COMBO","COMP","COS","COTI","CREAM","CRV","CTK","CTSI","CTXC","CVC","CVP","CVX","CYBER","DAR","DASH","DATA","DCR","DEGO","DENT","DEXE","DF","DGB","DIA","DOCK","DODO","DOGE","DOT","DUSK","DYDX","DYM","EDU","EGLD","ELF","ENA","ENJ","ENS","EOS","EPX","ERN","ETC","ETHFI","ETH","EUR","FARM","FDUSD","FET","FIDA","FIL","FIO","FIRO","FIS","FLM","FLOKI","FLOW","FLUX","FORTH","FOR","FRONT","FTM","FTT","FUN","FXS","GALA","GAL","GAS","GFT","GHST","GLMR","GLM","GMT","GMX","GNO","GNS","GRT","GTC","HARD","HBAR","HFT","HIFI","HIGH","HIVE","HOOK","HOT","ICP","ICX","IDEX","ID","ILV","IMX","INJ","IOST","IOTA","IOTX","IQ","IRIS","JASMY","JOE","JST","JTO","JUP","JUV","KAVA","KDA","KEY","KLAY","KMD","KNC","KP3R","KSM","LAZIO","LDO","LEVER","LINA","LINK","LIT","LOKA","LOOM","LPT","LQTY","LRC","LSK","LTC","LTO","LUNA","LUNC","MAGIC","MANA","MANTA","MASK","MATIC","MAV","MBL","MBOX","MDT","MDX","MEME","METIS","MINA","MKR","MLN","MOVR","MTL","NEAR","NEO","NEXO","NFP","NKN","NMR","NOT","NTRN","NULS","OAX","OCEAN","OGN","OG","OMG","OMNI","OM","ONE","ONG","ONT","OOKI","OP","ORDI","ORN","OSMO","OXT","PAXG","PDA","PENDLE","PEOPLE","PEPE","PERP","PHA","PHB","PIVX","PIXEL","POLS","POLYX","POND","PORTAL","PORTO","POWR","PROM","PROS","PSG","PUNDIX","PYR","PYTH","QI","QKC","QNT","QTUM","QUICK","RAD","RARE","RAY","RDNT","REEF","REI","REN","REQ","REZ","RIF","RLC","RNDR","RONIN","ROSE","RPL","RSR","RUNE","RVN","SAGA","SAND","SANTOS","SCRT","SC","SEI","SFP","SHIB","SKL","SLP","SNT","SNX","SOL","SPELL","SSV","STEEM","STG","STMX","STORJ","STPT","STRAX","STRK","STX","SUI","SUN","SUPER","SUSHI","SXP","SYN","SYS","TAO","TFUEL","THETA","TIA","TKO","TLM","TNSR","TRB","TROY","TRU","TRX","T","TUSD","TWT","UFT","UMA","UNFI","UNI","USDC","USDP","USTC","UTK","VANRY","VET","VGX","VIB","VIC","VIDT","VITE","VOXEL","VTHO","WAN","WAVES","WAXP","WBETH","WBTC","WIF","WING","WIN","WLD","WNXM","WOO","WRX","W","XAI","XEC","XEM","XLM","XNO","XRP","XTZ","XVG","XVS","YFI","YGG","ZEC","ZEN","ZIL","ZRX"⟩

#{klines⇐𝕩⋄indicators ⇐ (20‿60‿120‿30⊸XIndicators 𝕩)} 
#+´1↓(»-⊢) ≠¨ <˘ LdJson (<⊸∾⟜("USDT"⊸⋈⟜tfr)) "AEVO"
#≠¨{ 
#	{klines⇐𝕩⋄indicators ⇐ (20‿60‿120‿30⊸XIndicators 𝕩)} LdJson (<⊸∾⟜("usdt"⊸⋈⟜tfr) ) 𝕩
#	•Show 𝕩
#}¨ binance1d

BTest100 ← { 𝕤
	tfr ← 𝕨
	fassets ← 𝕩
#	tfr ← "1d"
#	fassets ← binance1d
	fklines ← LdJson¨ (<⊸∾⟜("USDT"⊸⋈⟜tfr))¨ fassets 
	filter ← 120<≠¨fklines
	#(¬filter) / fassets
	assets‿klines ← filter⊸/¨ fassets‿fklines


  res← {𝕩.res}¨ {⟨klines,indicators⟩⇐𝕩⋄res⇐120⊸XStra 𝕩}¨ {klines⇐𝕩⋄indicators ⇐ (20‿60‿120‿30⊸XIndicators 𝕩)}¨ klines
	stats ← XStats¨ res
	((<"")∾assets) ∾˘((0⊸⊏˘⊑)∾(>(1⊸⊏˘)¨)) {k←•ns.Keys 𝕩⋄ k≍˘𝕩⊸•ns.Get¨ k}¨ stats
}
#tfr ← "4h"
#tres ← tfr BTest100 binance1d

#("binance-"∾tfr∾"-Ichimoku.csv") •FLines csv.JoinL ((0⊸⊏)∾(⊢‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt⊸TFmt 1⊸↓))tres
#1↓ tres

#+´¯1⊑˘tres
#"top100-Ichimoku.csv" •FLines csv.JoinL ("ASSET"‿"PNL")∾  ⊢‿NFmt TFmt tres 
#tres

#"BTC"‿"USDT" PlotIchimoku "1d"
###
