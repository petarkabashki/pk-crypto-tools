
⟨Gnuplot⟩ ← •Import "Gnuplot.bqn"
csv←•Import "bqn-libs/csv.bqn"
str←•Import "bqn-libs/strings.bqn"
⟨JParse⇐Parse,JExport⇐Export⟩←•Import "bqn-libs/json.bqn"
⟨Split , Join,  SplitL, JoinL⟩←•Import "bqn-libs/csv.bqn"
# ⟨MP, Cholesky,Inverse⟩←•Import "bqn-libs/matrix.bqn"
#1‿1 MP 2‿2⥊4
⟨FmtNs, GLine, WMean, Ema, Var, WVar, WStd, GBars, CumBins, CumBinsPct, HBins, Hist, PHist, Resample, Round, FmtA⟩←•Import "pk-libs.bqn"
# ge ← •Import "genetic.bqn"

NSValues ← {𝕩⊸•ns.Get¨ (•ns.Keys 𝕩)} 
Test ← {fn←{Cond‿Act 𝕊 else: Cond◶Else‿Act}´𝕩 ⋄ Fn@}
IfElse ← {cond‿True‿False: cond◶False‿True @}
NFmt ← ⟨"¯"⟩‿⟨"-"⟩⊸str.ReplaceAll ∘ •Fmt
TFmt ← {r←𝕩⋄⍉>𝕨 {𝕎¨ 𝕩⊏˘r}¨ (↕≠𝕨)}
binanceDir← "/media/mu6mula/Data/Crypto-Data-Feed/freq-user-data/data/binance/"
FName ← {t‿q‿b←𝕨∾<𝕩⋄binanceDir∾b∾"_"∾q∾"-"∾t∾".json"}
Qcsv ← (⊣•FLines⟜(csv.JoinL NFmt¨)) 
KNorm ← ((1⊸↑˘)∾˘(⋆⁼1⊸↓˘))
LgLoad ← {KNorm ¯1↓˘>JParse •FChars 𝕨‿"USDT" FName 𝕩}


# FmtA ← {"⟨"∾(𝕩)∾"⟩" } 2↓ ( ∾´ (", "⊸∾ •Fmt)¨) 
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

# (⊢ (⋈¨) 10⊸×) ↕5

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
  enterSigsL← (tenkan>kijun)∧(close>senkoua⌈senkoub⌈kijun)
  enterSigsS← ¯1×(tenkan<kijun)∧(close<senkoua⌊senkoub)
  enterSigs ← enterSigsL + enterSigsS
  exitSigsL ← (close<senkoua⌈senkoub)∨(tenkan<kijun)
  exitSigsS ← (close>senkoua⌊senkoub)∨(tenkan>kijun)
  exitSigs ← exitSigsS ⋈¨ exitSigsL
  #+´wfrlows > close
  skipN←⌈´NSValues iparams⋄
  entprice←0⋄
  inpos‿pnl←res ⇐ {𝕤
      inpos‿pnl ⇐ <˘⍉ (skipN‿2⥊0) ∾ > (<0‿0) {
          inpos‿pnl ← 𝕨 ⋄ close‿entersig‿exitsig‿sl ← 𝕩
          {
              ((inpos=0) ∧ (1=entersig)) ? ({𝕤
					      entprice↩close
                # inpos ↩ entersig
					#•Show "Enter entprice: "∾(Nfmt entprice)∾"  price: "∾ (NFmt close)∾"  pnl: "∾(NFmt pnl)
					#•Show "Entering..."
					      entersig‿0
              }@);
#              (inpos ∧ ¬exitsig) ? ({𝕤
#                               #•Show "Carry on entprice: "∾(Nfmt entprice)∾"  price: "∾ (NFmt close)∾"  pnl: "∾(NFmt pnl)
#                  #wfsl⌈↩wfrlow
#                  {𝕤⋄inpos‿0}@
#              }@)
              (inpos≠0) ? ({𝕤
                  #(exitsig∨(0∧(close>entprice)∧(close<sl))) ? ({𝕤
                  ((÷⟜2 1+inpos) ⊑ exitsig) ? ({𝕤
                       #inpos↩0 #⋄ pnl↩ ⋆⁼ close ÷ entprice⋄                   
                       pnl ← inpos × (close-entprice) - 0.004
                      #  nex↩0⋄
                       #•Show "Exit entprice: "∾(Nfmt entprice)∾"  price: "∾ (NFmt close)∾"  pnl: "∾(NFmt pnl)
                       #entprice↩0
                       0‿pnl
                  }@);
                  {𝕤⋄
                      # nin 1⊸+↩
                      inpos‿0
                  }@
              }@);
              {𝕤⋄
                  # nex 1⊸+↩
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

  xin ← /posin ← ((¬»)∧⊢) |res.inpos
  xout ← /posout ← (»∧¬) |res.inpos
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
# xparams ← {resampleN‿tenkanN‿kijunN‿senkBN‿cloudN⇐ ⟨ 6, 50, 120, 5, 120 ⟩ }
# xparams ← {resampleN‿tenkanN‿kijunN‿senkBN‿cloudN⇐ ⟨ 1, 40, 115, 80, 135 ⟩ }
# ws‿ww←6000‿2000⋄ws‿ww PlotSingle XStra xparams⊸XIndicators {klines⇐𝕩} xparams.resampleN Resample "1h" LgLoad "SOL"

XStats ⇐ {
    ⟨inpos,pnl,cumpnl⟩ ← 𝕩
    minpos ← | inpos
    xin ← /posin ← ((¬»)∧⊢) minpos
    xout ← /posout ← (»∧¬) minpos
    ret⇐2 Round ¯1⊑0∾cumpnl
    ntrades⇐≠xout⋄nwins⇐+´0<xout⊏pnl⋄nlosses⇐ntrades-nwins⋄winratio⇐2 Round nwins÷ntrades⋄
    wins←(0⊸<⊸/)xout⊏pnl⋄losses←(0⊸≥⊸/)xout⊏pnl⋄avgwin⇐2 Round (+´÷≠)wins⋄avgloss⇐2 Round (+´÷≠)losses⋄
    bottompnl⇐2 Round ⌊´cumpnl
    maxpnl←2 Round ⌈`cumpnl
    ddn←2 Round -maxpnl-cumpnl
    maxddn⇐2 Round ⌊´ddn
    vol⇐2 Round √Var pnl
    sharpe⇐2 Round ret÷vol
    toppnl⇐2 Round ⌈´maxpnl
}

# ToPars← {resampleN‿tenkanN‿kijunN‿senkbn‿cloudn⇐𝕩}
ToPars ← {resampleN‿tenkanN‿kijunN‿senkbn‿cloudn⇐𝕩}

########################################
### Test TOP 100 coins 
assets ← 30↑  (¬∊⟜"USDT"‿"USDC"‿"BUSD")⊸/ •Flines "/media/mu6mula/Data/Crypto-Data-Feed/top100MarketCap.txt"

(≠⊸∾) top100 ← •FLines "/media/mu6mula/Data/Crypto-Data-Feed/top100-1d.csv"
(≠⊸∾) binance1d ← •FLines "/media/mu6mula/Data/Crypto-Data-Feed/binance-1d.csv"


# tframe ← "4h"
SaveStatsRep ← {("strat-results/binance-Ichimoku.csv") •FLines csv.JoinL ((0⊸⊏)∾(⊢‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt‿NFmt⊸TFmt 1⊸↓)) 𝕩}
########################################
### Generate report on top100 coins
# ("4h"⊸RollStra)¨  20↑ ⊏˘re
# ("4h"⊸RollStra)¨  20↑ ⊏˘re
RollStra ← {tframe 𝕊 aparams:
  params ← ToPars aparams
  # •Show ⊢ tframe SaveStatsRep 
  # rep ⇐ 
  ((<"")∾assets) ∾˘((0⊸⊏˘⊑)∾(>(1⊸⊏˘)¨)) {k←•ns.Keys 𝕩⋄ k≍˘𝕩⊸•ns.Get¨ k}¨ stats ← XStats¨ •ns.Get⟜"res"¨ restra← XStra¨params⊸XIndicators¨{klines⇐ 𝕩}¨ ⊑klines‿assets‿fileNames /˜¨↩ <nrowsFilter← 200⊸< ≠¨ klines ← ((params.resampleN⊸Resample ) ∘ KNorm ∘((¯1⊸↓˘>)JParse⟜•FChars))¨ 1⊸⊑ assets‿fileNames /˜¨↩<filterFX←•file.Exists¨ fileNames←{t‿q←tframe‿"USDT"⋄binanceDir∾𝕩∾"_"∾q∾"-"∾t∾".json"}¨ assets #←top100
}
# +´ 1↓ 1⊏˘ 
# SaveStatsRep ⊢
(SaveStatsRep ⊢ ((÷⟜(≠assets))+´∘(1⊸↓ 1⊸⊏˘)))  "4h" RollStra ⟨2, 30, 105, 70, 65⟩

# (SaveStatsRep ⊢ (+´∘(1⊸↓ 1⊸⊏˘)))  "1h" RollStra ⟨ 9, 15, 110, 95, 10 ⟩

########################################
### Optimize single asset params via Genetic Algo and Grid Search

Obj ← {𝕤⋄ 
  xparams←ToPars 𝕨⋄ 
  {(⌊2×𝕩.ret)‿𝕩} XStats {𝕩.res} XStra xparams⊸XIndicators {klines⇐𝕩} xparams.resampleN Resample 𝕩
}
# Obj2 ← { 𝕊 aparams:
#   params ← {resampleN‿tenkanN‿kijunN‿senkBN‿cloudN⇐𝕩} aparams
#   +´ {𝕩.ret}¨ stats ← XStats¨ •ns.Get⟜"res"¨ restra← XStra¨(params)⊸XIndicators¨{klines⇐𝕩}¨ ⊑klines‿assets‿fileNames /˜¨↩ <nrowsFilter← 200⊸< ≠¨ klines ← (KNorm ((¯1⊸↓˘>)JParse⟜•FChars))¨ 1⊸⊑ assets‿fileNames /˜¨↩<filterFX←•file.Exists¨ fileNames←{t‿q←tframe‿"USDT"⋄binanceDir∾𝕩∾"_"∾q∾"-"∾t∾".json"}¨ assets ← top100
# }
IGntr←{ 𝕊 start‿end‿step: {𝕊: step×1+•rand.Range ⌊step ÷˜end-start } }
# Parameters with random generator functions
# 
pardefs ← ⍉>⟨"resampleN"‿(IGntr 1‿24‿1),"tenkanN"‿(IGntr 5‿150‿5),"kijunn"‿(IGntr 5‿150‿5),"senkbn"‿(IGntr 15‿150‿5),"cloudn"‿(IGntr 5‿150‿5) ⟩ 
### Generate Random Params
GenRan ← {𝕊: (1⊏pardefs) {𝕎𝕩}¨ @}
Mutate ← { 𝕊 xparams: 
  ix←•rand.Range ≠⊏pardefs
  nval←{𝕏@} (1‿(ix) ⊑ pardefs) 
  (ix↑xparams)  ∾ nval ∾ (ix+1)↓xparams
}
#0‿∞ PlotSingle XStra ({tenkann‿kijunn‿senkbn‿cloudn⇐𝕩} 10‿15‿65‿125)⊸XIndicators {klines⇐𝕩} "8h" LgLoad "ALGO"
### Run Genetic Algorithm for parameter optimization

FmtParG ← (("par"‿"obj" ∾ 2⊸↑˘) ∾˘ ({k←•ns.Keys ⊑ 𝕩⋄ k∾ > (•ns.Get¨⟜(k))¨ ⥊𝕩 }  2⊸↓˘))
# ≠ "1h" LgLoad "REN"
# ⌽ 7↑˘ (1⊸↑˘ ∾˘ 2⊸↓˘) 1↓ re

∾´ reh‿re ← ↑‿↓ {1𝕎𝕩}¨< ((⍒ 1⊸⊏˘)⊸⊏) (1⊸↑˘ ∾˘ 2⊸↓˘) FmtParG 100‿35‿25 {𝕤
  niter‿ntop‿nper ← 𝕨
  klines ← 𝕩
  (>(<∾(Obj⟜klines ToPars))¨ GenRan¨ ↕nper) {
    pars ← ⊏˘ 𝕩
    ntop↑(∊⊏˘)⊸/ ((⍒ 1⊸⊏˘)⊸⊏) 𝕩∾>(<∾(Obj⟜klines ToPars))¨ (Mutate¨ (•rand.Range nper) ⊏ pars) ∾ GenRan¨ ↕nper
  }´ ↕niter
} klines ← "4h" LgLoad "SOL"

rre←((FmtA¨ ⊏˘) ∾˘ 1⊸↓˘)  re
•Show rre
"strat-results/opt-ichimoku.csv" •FLines csv.JoinL •Fmt¨ rre

ro← (⊏˘ ∾˘ ((÷⟜1000∘⌊×⟜1000) ∘ ÷⟜(≠assets)¨ (1⊸⊏˘))) {(1↓˘𝕩)∾˘˜ {"⟨"∾(𝕩)∾"⟩" }¨ 2↓¨ ( ∾´ (", "⊸∾ •Fmt)¨)¨ ⊏˘ 𝕩}  ((⍒ 1⊸⊏˘)⊸⊏) >(⋈⟜((+´ 1⊸↓)(1⊸⊏˘ "4h"⊸RollStra)))¨ 1↓ ⊏˘re
•Show ro
("strat-results/roll-stra-Opt.csv") •FLines csv.JoinL "par"‿"ret" ∾ (1⊸↑˘ ∾˘ (NFmt¨ 1⊸↓˘)) ro
  
# •Parse 1↑˘ro



# 10↑↕5
# 0‿∞ PlotSingle XStra {tenkanN⇐30⋄kijunN⇐45⋄senkBN⇐45⋄cloudN⇐60}⊸XIndicators {klines⇐𝕩} "4h" LgLoad "RAY"
5000‿∞ PlotSingle XStra {tenkanN‿kijunN‿senkBN‿cloudN⇐ ⟨ 70, 75, 25, 75 ⟩}⊸XIndicators {klines⇐𝕩} "4h" LgLoad "ALGO"

