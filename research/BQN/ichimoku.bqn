
⟨Gnuplot⟩ ← •Import "Gnuplot.bqn"
csv←•Import "bqn-libs/csv.bqn"
str←•Import "bqn-libs/strings.bqn"
⟨JParse⇐Parse,JExport⇐Export⟩←•Import "bqn-libs/json.bqn"
⟨Split , Join,  SplitL, JoinL⟩←•Import "bqn-libs/csv.bqn"
⟨MP, Cholesky,Inverse⟩←•Import "bqn-libs/matrix.bqn"
#1‿1 MP 2‿2⥊4
⟨FmtNs, GLine, WMean, Ema, Var, WVar, WStd, GBars, CumBins, CumBinsPct, HBins, Hist, PHist⟩←•Import "pk-libs.bqn"
ge ← •Import "genetic.bqn"

NSValues ← {𝕩⊸•ns.Get¨ (•ns.Keys 𝕩)} 
Test ← {fn←{Cond‿Act 𝕊 else: Cond◶Else‿Act}´𝕩 ⋄ Fn@}
IfElse ← {cond‿True‿False: cond◶False‿True @}
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
	⟨klines⟩ ⇐ 𝕩
	iparams ⇐ 𝕨⋄
	tenkanN‿kijunN‿senkBN‿cloudN ← iparams
	indicators ⇐ {𝕤
		tenkan ⇐ ÷⟜2 +´⌈‿⌊ {(0⥊˜tenkanN-1)∾𝕎 ˝˘ tenkanN↕𝕩}¨ ⋈˝⍉2‿3⊸⊏˘klines⋄
		kijun ⇐ ÷⟜2 +´⌈‿⌊ {(0⥊˜kijunN-1)∾𝕎 ˝˘ kijunN↕𝕩}¨ ⋈˝⍉2‿3⊸⊏˘klines⋄
		senkouA ⇐ (cloudN⥊0)» ÷⟜2 tenkan + kijun⋄
		senkouB ⇐ (cloudN⥊0)» ÷⟜2 +´⌈‿⌊ {(0⥊˜senkBN-1)∾𝕎 ˝˘ senkBN↕𝕩}¨ ⋈˝⍉2‿3⊸⊏˘klines⋄
	#	tenkan‿kijun‿senkouA‿senkouB
		c5h‿c5l ← ⌈‿⌊ { 𝕎 ´˘ 𝕩 }¨ ((((««)∾˘») (0‿0∾2⊸↕) ))¨ h‿l ← 2‿3 ⊏˘¨ <klines 
		wfh‿wfl ⇐ >‿< {⊑∘𝕎 ˝𝕩}¨ h‿l ⋈¨ c5h‿c5l
		#wfra⇐ ⊑ +´ 1‿¯1 ×¨
	}@
}
#{𝕩.indicators.wfl} {tenkanN⇐20⋄kijunN⇐60⋄senkBN⇐120⋄cloudN⇐30} XIndicators {klines⇐LdJson "ADA"‿"USDT"‿"1d"}
#{𝕩.indicators.wfra} {tenkanN⇐20⋄kijunN⇐60⋄senkBN⇐120⋄cloudN⇐30} XIndicators {klines⇐LdJson "ADA"‿"USDT"‿"1d"}

XStra2 ← { 
	⟨klines,indicators,iparams⟩ ← 𝕩
	⟨tenkan,kijun,senkouA,senkouB⟩ ← indicators
	skipN ← 𝕨
	ixs ← ↕≠klines
	senkouUp‿senkouDn ← ⌈‿⌊ {𝕎 ´ 𝕩}¨ < senkouA‿senkouB
	close←¯2⊏˘klines⋄ # lnclose ← ⋆⁼ close
	xinsig ⇐ (skipN < ixs) ∧ (tenkan > kijun) ∧ (close > senkouUp) ∧ (close > tenkan)
#	xoutsig ←  (close < senkouUp)   #∨ (tenkan < kijun)
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

XStra ← {𝕤
	⟨klines,indicators,iparams⟩ ⇐ 𝕩
#	⟨klines,indicators,iparams⟩ ← {tenkanN⇐20⋄kijunN⇐60⋄senkBN⇐120⋄cloudN⇐30} XIndicators {klines⇐LdJson "ADA"‿"USDT"‿"1d"}
	⟨tenkan,kijun,senkouA,senkouB,wfl⟩ ← indicators
	lows ← 3⊑˘klines
	ts‿open‿high‿low‿close‿vlume ← <˘⍉klines
	iwfl←/wfl
	lwfrT ← (∾˘⟜(⊏⟜low)) iwfl
	dwfl←(-⟜»)/wfl∾1⋄
	wfrlow← ((dwfl)/(0∾iwfl))⊏low
	enterSigs← (tenkan>kijun)∧(close>senkoua⌈senkoub⌈kijun⌈tenkan)
	exitSigs ← (close<senkoua⌈senkoub)∨(tenkan<kijun)
	#+´wfrlows > close
	skipN←⌈´NSValues iparams⋄
	entprice←0⋄nin←0⋄nex←0⋄
  inpos‿pnl←res ⇐ {𝕤
			inpos‿pnl ⇐ <˘⍉ (skipN‿2⥊0) ∾ > (<0‿0) {𝕤
					inpos‿pnl ← 𝕨 ⋄ close‿entersig‿exitsig‿sl ← 𝕩
					{
							((¬inpos) ∧ entersig ∧ (nex> iparams.tenkanN) ) ? ({𝕤
															 entprice↩close⋄nin↩0⋄#wfsl↩wfrlow ⋄ #⋄ pnl↩0 ⋄
															 #•Show "Enter entprice: "∾(Nfmt entprice)∾"  price: "∾ (NFmt close)∾"  pnl: "∾(NFmt pnl)
															 #•Show "Entering..."
															 1‿0
							}@);
#							(inpos ∧ ¬exitsig) ? ({𝕤
#															 #•Show "Carry on entprice: "∾(Nfmt entprice)∾"  price: "∾ (NFmt close)∾"  pnl: "∾(NFmt pnl)
#									#wfsl⌈↩wfrlow
#									{𝕤⋄inpos‿0}@
#							}@)
							(inpos) ? ({𝕤
									(exitsig∨(1∨(close>entprice)∧(close<sl))) ? ({𝕤
											 #inpos↩0 #⋄ pnl↩ ⋆⁼ close ÷ entprice⋄                                   
											 pnl ← (⋆⁼ close÷entprice)
											 nex↩0⋄
											 #•Show "Exit entprice: "∾(Nfmt entprice)∾"  price: "∾ (NFmt close)∾"  pnl: "∾(NFmt pnl)
											 #entprice↩0
											 0‿pnl
									}@);
									{𝕤⋄
											nin 1⊸+↩
											inpos‿0
									}@
							}@);
							{𝕤⋄
									nex 1⊸+↩
									inpos‿0
							}@
					}
				}` <˘ skipN↓ ⊢ close∾˘enterSigs∾˘exitSigs∾˘0‿0»wfrlow
			cumpnl ⇐ +` pnl
		}@
		+´inpos
}
		
⟨klines,indicators,res⟩←XStra {tenkanN⇐50⋄kijunN⇐100⋄senkBN⇐240⋄cloudN⇐60} XIndicators {klines⇐LdJson "INJ"‿"USDT"‿"1d"}
#ws‿pwl ← 1000‿∞
PlotSingle ← { 𝕤
	⟨klines,indicators,res⟩← 𝕩⋄ 	ws‿pwl ← 𝕨⋄
	⟨tenkan,kijun,senkoua,senkoub,wfl,wfh⟩ ← indicators
	ts‿open‿high‿low‿close‿volume ←<˘⍉ klines
	wl← pwl⌊ (≠klines) - ws
	Ww←(wl⊸↑ws⊸↓) ⋄ Wi ← (({∧´ (≥⟜ws)‿((ws+wl)⊸≥) {𝕎 𝕩}¨ 𝕩} (<⊑˘))⊸/)

	iwfl←/wfl
	lwfrT ← (∾˘⟜(⊏⟜low)) iwfl
	dwfl←(-⟜»)/wfl∾1⋄
	wfrlow← ((dwfl)/(0∾iwfl))⊏low


	xin ← /posin ← ((¬»)∧⊢) res.inpos
	xout ← /posout ← (»∧¬) res.inpos
	ymin ← ⌊´Ww low⋄ymax← ⌈´Ww high
	#close←¯2⊏˘klines⋄ # lnclose ← ⋆⁼ close
		ixs ← ↕≠klines⋄
		plt ← Gnuplot "
			title 'Ichimoku Cloud' font ',18'
			terminal wxt size 2400,900
			y2tics 0.20 nomirror tc lt 2
			y2range [-1:10]
			xrange ["∾(NFmt ws)∾":"∾(NFmt ws+wl-1)∾"]
			yrange ["∾(NFmt ymin)∾":"∾(NFmt ymax)∾"]
			grid
			parametric
			style line 5 lt rgb 'cyan' lw 3 pt 6"
		plt.Plot (Ww ⍉>ixs‿senkouA‿senkouB)‿" with filledcurves fs solid 0.1"
		plt.Plot (Ww ⍉>ixs‿close)‿"lw 2 lc rgb 'black' with lines"
#		#plt.Plot (⍉>ixs‿high)‿"lw 1 lc rgb 'orange' with lines"
		#plt.Plot (⍉>ixs‿low)‿"lw 1 lc rgb 'green' with lines"
		plt.Plot (Ww ⍉>ixs‿tenkan)‿"lw 1 lc rgb '#5555CC' with lines"
		plt.Plot (Ww ⍉>ixs‿kijun)‿"lw 1 lc rgb 'red' with lines"
		plt.Plot (Ww ⍉>ixs‿senkouA)‿"lw 1 lc rgb 'gray' with lines"
		plt.Plot (Ww ⍉>ixs‿senkouB)‿"lw 1 lc rgb 'gray' with lines"
		plt.Plot (Wi ⍉>ixs‿res.cumpnl)‿"lw 5 lc rgb 'orange' with steps axes x1y2"
		plt.Plot (Wi lwfrT)‿"lw 5 lc rgb 'gray' with points"
		#plt.Plot (Ww ⍉>ixs‿wfrlow)‿"lw 1 lc rgb 'black' with lines"
		plt.Plot ((xin)(⊣∾˘⊏)close)‿"lw 5 lc rgb 'black' with points"
		plt.Plot ((xout)(⊣∾˘⊏)close)‿"lw 5 lc rgb 'blue' with points"
		"gnuplot-ichimoku-1.txt" •file.Chars plt.Debug @
		•SH "gnuplot"‿"-persist"‿"gnuplot-ichimoku-1.txt"
}

0‿∞ PlotSingle XStra {tenkanN⇐15⋄kijunN⇐35⋄senkBN⇐120⋄cloudN⇐30}⊸XIndicators {klines⇐𝕩}LdJson "REN"‿"USDT"‿"8h"

XStats ⇐ {
		⟨inpos,pnl,cumpnl⟩ ← 𝕩
		xin ← /posin ← ((¬»)∧⊢) inpos
		xout ← /posout ← (»∧¬) inpos
		ret⇐¯1⊑0∾cumpnl
		ntrades⇐≠xout⋄nwins⇐+´0<xout⊏pnl⋄nlosses⇐ntrades-nwins⋄winratio⇐nwins÷ntrades⋄
		wins←(0⊸<⊸/)xout⊏pnl⋄losses←(0⊸≥⊸/)xout⊏pnl⋄avgwin⇐(+´÷≠)wins⋄avgloss⇐(+´÷≠)losses⋄
		bottompnl⇐⌊´cumpnl
		maxpnl←⌈`cumpnl
		ddn←-maxpnl-cumpnl
		maxddn⇐⌊´ddn
		vol⇐√Var pnl
		sharpe⇐ret÷vol
		toppnl⇐⌈´maxpnl
}

########################################
### Test TOP 100 coins 
(≠⊸∾) top100 ← •FLines "/media/mu6mula/Data/Crypto-Data-Feed/top100-1d.csv"
(≠⊸∾) binance1d ← •FLines "/media/mu6mula/Data/Crypto-Data-Feed/binance-1d.csv"


#assets ← 5↑ top100
#tfr ← "8h"
XStatsRep ← { 𝕤
	tfr ← 𝕨
	assets ← 𝕩
#{XStra {tenkanN⇐20⋄kijunN⇐60⋄senkBN⇐120⋄cloudN⇐30}⊸XIndicators {klines⇐LdJson 𝕩} 𝕩‿"USDT"‿tfr}¨ assets
  res← ({𝕩.res} XStra⟜({tenkanN⇐20⋄kijunN⇐60⋄senkBN⇐120⋄cloudN⇐30}⊸XIndicators  {•Show𝕩⋄klines⇐LdJson 𝕩‿"USDT"‿tfr}))¨ assets

 #{klines⇐𝕩⋄indicators ⇐ (20‿60‿120‿30⊸XIndicators 𝕩)}¨ klines
	stats ← XStats¨ res
	((<"")∾assets) ∾˘((0⊸⊏˘⊑)∾(>(1⊸⊏˘)¨)) {k←•ns.Keys 𝕩⋄ k≍˘𝕩⊸•ns.Get¨ k}¨ stats
}

	SaveStatsRep ← {tfr←𝕨⋄("binance-"∾tfr∾"-Ichimoku.csv") •FLines csv.JoinL ((0⊸⊏)∾(⊢‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt⊸TFmt 1⊸↓)) 𝕩}
"4h" (⊣ SaveStatsRep XStatsRep) binance1d
Obj ← {+´ 1⊑˘ 1↓ "1d" XStatsRep binance1d

#1↓ tres

#+´¯1⊑˘tres
#"top100-Ichimoku.csv" •FLines csv.JoinL ("ASSET"‿"PNL")∾  ⊢‿NFmt TFmt tres 
#tres

#"BTC"‿"USDT" PlotIchimoku "1d"
###
