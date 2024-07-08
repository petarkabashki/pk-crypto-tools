
⟨Gnuplot⟩ ← •Import "Gnuplot.bqn"
csv←•Import "bqn-libs/csv.bqn"
str←•Import "bqn-libs/strings.bqn"
⟨JParse⇐Parse,JExport⇐Export⟩←•Import "bqn-libs/json.bqn"
⟨Split , Join,  SplitL, JoinL⟩←•Import "bqn-libs/csv.bqn"
⟨MP, Cholesky,Inverse⟩←•Import "bqn-libs/matrix.bqn"
#1‿1 MP 2‿2⥊4
⟨FmtNs, GLine, WMean, Ema, Var, WVar, WStd, GBars, CumBins, CumBinsPct, HBins, Hist, PHist, Resample⟩←•Import "pk-libs.bqn"
# ge ← •Import "genetic.bqn"

NSValues ← {𝕩⊸•ns.Get¨ (•ns.Keys 𝕩)} 
Test ← {fn←{Cond‿Act 𝕊 else: Cond◶Else‿Act}´𝕩 ⋄ Fn@}
IfElse ← {cond‿True‿False: cond◶False‿True @}
NFmt ← ⟨"¯"⟩‿⟨"-"⟩⊸str.ReplaceAll ∘ •Fmt
TFmt ← {r←𝕩⋄⍉>𝕨 {𝕎¨ 𝕩⊏˘r}¨ (↕≠𝕨)}
binanceDir← "/media/mu6mula/Data/Crypto-Data-Feed/freq-user-data/data/binance/"
Qcsv ← (⊣•FLines⟜(csv.JoinL NFmt¨)) 
FName ← {t‿q‿b←𝕨∾<𝕩⋄binanceDir∾b∾"_"∾q∾"-"∾t∾".json"}
KNorm ← ((1⊸↑˘)∾˘(⋆⁼1⊸↓˘))
LgLoad ← {KNorm ¯1↓˘>JParse •FChars 𝕨‿"USDT" FName 𝕩}

#5↑ ((1⊸↑˘)∾˘(⋆⁼1⊸↓˘)) ¯1↓˘ >JParse •FChars binanceDir ∾ "BTC_USDT-1d.json"

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
  #  tenkan‿kijun‿senkouA‿senkouB
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
#  xoutsig ←  (close < senkouUp)   #∨ (tenkan < kijun)
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
# ⟨klines,indicators,iparams⟩ ← {tenkanN⇐20⋄kijunN⇐60⋄senkBN⇐120⋄cloudN⇐30}⊸XIndicators {klines⇐𝕩} "8h" LgLoad "ADA"
#  ⟨klines,indicators,iparams⟩ ← {tenkanN⇐20⋄kijunN⇐60⋄senkBN⇐120⋄cloudN⇐30} XIndicators {klines⇐LdJson "ADA"‿"USDT"‿"1d"}
  ⟨tenkan,kijun,senkouA,senkouB,wfl⟩ ← indicators
  ts‿open‿high‿low‿close ← <˘⍉klines
klines  
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
              ((¬inpos) ∧ entersig ∧ (1∨nex> iparams.tenkanN) ) ? ({𝕤
					entprice↩close⋄nin↩0⋄#wfsl↩wfrlow ⋄ #⋄ pnl↩0 ⋄
					#•Show "Enter entprice: "∾(Nfmt entprice)∾"  price: "∾ (NFmt close)∾"  pnl: "∾(NFmt pnl)
					#•Show "Entering..."
					1‿0
              }@);
#              (inpos ∧ ¬exitsig) ? ({𝕤
#                               #•Show "Carry on entprice: "∾(Nfmt entprice)∾"  price: "∾ (NFmt close)∾"  pnl: "∾(NFmt pnl)
#                  #wfsl⌈↩wfrlow
#                  {𝕤⋄inpos‿0}@
#              }@)
              (inpos) ? ({𝕤
                  #(exitsig∨(0∧(close>entprice)∧(close<sl))) ? ({𝕤
                  (exitsig) ? ({𝕤
                       #inpos↩0 #⋄ pnl↩ ⋆⁼ close ÷ entprice⋄                   
                       pnl ← (close-entprice)
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
    
#⟨klines,indicators,res⟩←XStra {tenkanN⇐50⋄kijunN⇐100⋄senkBN⇐240⋄cloudN⇐60} XIndicators {klines⇐LdJson "INJ"‿"USDT"‿"1d"}
#ws‿pwl ← 1000‿∞
PlotSingle ← { 𝕤
  ⟨klines,indicators,res⟩← 𝕩⋄   ws‿pwl ← 𝕨⋄
  ⟨tenkan,kijun,senkoua,senkoub,wfl,wfh⟩ ← indicators
  ts‿open‿high‿low‿close ←<˘⍉ klines
  wl← pwl⌊ (≠klines) - ws
  Ww←(wl⊸↑ws⊸↓) ⋄ Wi ← (({∧´ (≥⟜ws)‿((ws+wl)⊸≥) {𝕎 𝕩}¨ 𝕩} (<⊑˘))⊸/)

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
#    #plt.Plot (⍉>ixs‿high)‿"lw 1 lc rgb 'orange' with lines"
    #plt.Plot (⍉>ixs‿low)‿"lw 1 lc rgb 'green' with lines"
    plt.Plot (Ww ⍉>ixs‿tenkan)‿"lw 1 lc rgb '#5555CC' with lines"
    plt.Plot (Ww ⍉>ixs‿kijun)‿"lw 1 lc rgb 'red' with lines"
    plt.Plot (Ww ⍉>ixs‿senkouA)‿"lw 1 lc rgb 'gray' with lines"
    plt.Plot (Ww ⍉>ixs‿senkouB)‿"lw 1 lc rgb 'gray' with lines"
    plt.Plot (Wi ⍉>ixs‿res.cumpnl)‿"lw 5 lc rgb 'orange' with steps axes x1y2"
    #plt.Plot (Wi lwfrT)‿"lw 5 lc rgb 'gray' with points"
    #plt.Plot (Ww ⍉>ixs‿wfrlow)‿"lw 1 lc rgb 'black' with lines"
    plt.Plot ((xin)(⊣∾˘⊏)close)‿"lw 5 lc rgb 'black' with points"
    plt.Plot ((xout)(⊣∾˘⊏)close)‿"lw 5 lc rgb 'blue' with points"
    "gnuplot-ichimoku-1.txt" •file.Chars plt.Debug @
    •SH "gnuplot"‿"-persist"‿"gnuplot-ichimoku-1.txt"
}
#0‿∞ PlotSingle XStra {tenkanN⇐30⋄kijunN⇐45⋄senkBN⇐45⋄cloudN⇐60}⊸XIndicators {klines⇐𝕩} "8h" LgLoad "ALGO"

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

ToPars← {resampleN‿tenkanN‿kijunN‿senkbn‿cloudn⇐𝕩}

########################################
### Test TOP 100 coins 
(≠⊸∾) top100 ← •FLines "/media/mu6mula/Data/Crypto-Data-Feed/top100-1d.csv"
(≠⊸∾) binance1d ← •FLines "/media/mu6mula/Data/Crypto-Data-Feed/binance-1d.csv"

tframe ← "8h"
SaveStatsRep ← {tframe←𝕨⋄("binance-"∾tframe∾"-Ichimoku.csv") •FLines csv.JoinL ((0⊸⊏)∾(⊢‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt⊸TFmt 1⊸↓)) 𝕩}
########################################
### Generate report on top100 coins
RollStra ← {tframe 𝕊 aparams:
  params ← {tenkanN‿kijunN‿senkBN‿cloudN⇐𝕩} aparams
  •Show tframe SaveStatsRep rep ⇐ ((<"")∾assets) ∾˘((0⊸⊏˘⊑)∾(>(1⊸⊏˘)¨)) {k←•ns.Keys 𝕩⋄ k≍˘𝕩⊸•ns.Get¨ k}¨ stats ← XStats¨ •ns.Get⟜"res"¨ restra← XStra¨params⊸XIndicators¨{klines⇐𝕩}¨ ⊑klines‿assets‿fileNames /˜¨↩ <nrowsFilter← 200⊸< ≠¨ klines ← (KNorm ((¯1⊸↓˘>)JParse⟜•FChars))¨ 1⊸⊑ assets‿fileNames /˜¨↩<filterFX←•file.Exists¨ fileNames←{t‿q←tframe‿"USDT"⋄binanceDir∾𝕩∾"_"∾q∾"-"∾t∾".json"}¨ assets←top100
}
# "8h" RollStra 25‿35‿100‿65 

########################################
### Optimize single asset params via Genetic Algo and Grid Search

3↑ klines ← "1h" LgLoad "REN"
Obj ← {𝕤⋄ 
  xparams←ToPars 𝕨⋄ 
  {𝕩.ret‿𝕩} XStats {𝕩.res} XStra xparams⊸XIndicators {klines⇐𝕩} xparams.resampleN Resample 𝕩
}
# Obj2 ← { 𝕊 aparams:
#   params ← {resampleN‿tenkanN‿kijunN‿senkBN‿cloudN⇐𝕩} aparams
#   +´ {𝕩.ret}¨ stats ← XStats¨ •ns.Get⟜"res"¨ restra← XStra¨(params)⊸XIndicators¨{klines⇐𝕩}¨ ⊑klines‿assets‿fileNames /˜¨↩ <nrowsFilter← 200⊸< ≠¨ klines ← (KNorm ((¯1⊸↓˘>)JParse⟜•FChars))¨ 1⊸⊑ assets‿fileNames /˜¨↩<filterFX←•file.Exists¨ fileNames←{t‿q←tframe‿"USDT"⋄binanceDir∾𝕩∾"_"∾q∾"-"∾t∾".json"}¨ assets ← top100
# }
# 1‿30‿80‿115‿125 Obj klines
# iparams ← {tenkanN⇐30⋄kijunN⇐60⋄sen{𝕤 kBN⇐120⋄cloudN⇐30}
IGntr←{ 𝕊 start‿end‿step: {𝕊: step×1+•rand.Range ⌊step ÷˜end-start } }
# Parameters with random generator functions
pardefs ← ⍉>⟨"resampleN"‿(IGntr 1‿12‿1),"tenkanN"‿(IGntr 5‿150‿5),"kijunn"‿(IGntr 5‿150‿5),"senkbn"‿(IGntr 15‿150‿5),"cloudn"‿(IGntr 5‿150‿5) ⟩ 
### Generate Random Params
GenRan ← {𝕊: (1⊏pardefs) {𝕎𝕩}¨ @}
Mutate ← { 𝕊 xparams: 
  ix←•rand.Range ≠⊏pardefs
  nval←{𝕏@} (1‿(ix) ⊑ pardefs) 
  (ix↑xparams)  ∾ nval ∾ (ix+1)↓xparams
}
#0‿∞ PlotSingle XStra ({tenkann‿kijunn‿senkbn‿cloudn⇐𝕩} 10‿15‿65‿125)⊸XIndicators {klines⇐𝕩} "8h" LgLoad "ALGO"
### Run Genetic Algorithm for parameter optimization

50‿10‿10 {𝕤
  niter‿ntop‿nper ← 𝕨
  klines ← 𝕩
  (>(<∾(Obj⟜klines ToPars))¨ GenRan¨ ↕nper) {
    pars ← ⊏˘𝕩
    ntop↑(∊⊏˘)⊸/ ((⍒ 1⊸⊏˘)⊸⊏) 𝕩∾>(<∾(Obj⟜klines ToPars))¨ (Mutate¨ (•rand.Range nper) ⊏ pars) ∾ GenRan¨ ↕nper
  }´ ↕niter
} klines

# 10↑↕5
# 0‿∞ PlotSingle XStra {tenkanN⇐30⋄kijunN⇐45⋄senkBN⇐45⋄cloudN⇐60}⊸XIndicators {klines⇐𝕩} "4h" LgLoad "RAY"
5000‿∞ PlotSingle XStra {tenkanN‿kijunN‿senkBN‿cloudN⇐ ⟨ 70, 75, 25, 75 ⟩}⊸XIndicators {klines⇐𝕩} "4h" LgLoad "ALGO"

