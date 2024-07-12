
⟨lup,mp,solve,inverse⟩ ← •Import "bqn-libs/matrix.bqn"
⟨FmtNs, GLine, WMean, Ema, Var, WVar, WStd, GBars, CumBins, CumBinsPct, HBins, Hist, PHist, Ols, Eye⟩←•Import "pk-libs.bqn"
⟨JParse⇐Parse,JExport⇐Export⟩←•Import "bqn-libs/json.bqn"
⟨Min1,_powell,_nelderMead⟩ ← •Import "bqn-libs/min.bqn"

⟨Gnuplot⟩ ← •Import "Gnuplot.bqn"

### Generates random parameters, Floating Point :𝕩=(start,end,n-granularity)
RGen ← {st‿ed‿se←𝕩⋄ st+(ed-st) × ((𝕨 •rand.Range (1⊸+))⊸÷) se} 
# RGen ⟨0,10,20⟩
# 5 RGen ⟨0.1,0.9,8⟩

#⟨Cos⟩ ← •math
binanceDir← "/media/mu6mula/Data/Crypto-Data-Feed/freq-user-data/data/binance/"
FName ← {t‿q‿b←𝕨∾<𝕩⋄binanceDir∾b∾"_"∾q∾"-"∾t∾".json"}
≠df ← "1d" { ¯1↓˘>JParse •FChars 𝕨‿"USDT" FName 𝕩} "BTC"

ws‿ww ← 100‿285
≠t← ↕n← ≠ p ← ww↑ws↓ ¯1⊏˘df
# GLine p


# ×⟜(1⊸⌽) ⊣ 1+↕3

FitABC ← {Fn p‿t:
    ⟨tc,m,w⟩ ← ⟨0.9×≠t,0.4,8⟩
    yi ← ⋆⁼ p ⋄ fi ← ⋆⟜m  dti ← 1E¯8 + | (tc - t) ⋄ sfi ← +´ fi
    sgi‿shi ← ⊣ +´¨ gi‿hi ← (<fi) × •math.Cos‿•math.Sin {𝕎 𝕩}¨<wphase ← w × phase ← ⋆⁼ dti
    sfi2‿sgi2‿shi2 ← +´¨ fi2‿gi2‿hi2 ← ⋆⟜2 fi‿gi‿hi
    sfigi‿sgihi‿sfihi ← +´¨ figi‿gihi‿fihi ← ×⟜(1⊸⌽) fi‿gi‿hi
    # m ← 3‿3⥊⟨m,sfi,sgi,sfi,sfi2,sfigi,sgi,sfigi,sgi2⟩
    mat ← 4‿4⥊⟨n,sfi,sgi,shi, sfi,sfi2,sfigi,sfihi, sgi,sfigi,sgi2,sgihi, shi,sfihi,sgihi,shi2⟩
    # my ← +´¨ 1‿fi‿gi‿hi × <yi
    a‿b‿c1‿c2 ← (mat+ 1E¯8 × Eye 4) Solve +´¨ 1‿fi‿gi‿hi × < yi
    # (+´¨ 1‿fi‿gi‿hi × <p) MP Inverse m + 1E¯8 × Eye 4
}
# FitABC p

Lppls ← { tc‿m‿w‿a‿b‿c1‿c2 𝕊 t:
# •Show "--------------"
# •Show t
    fi ← ⋆⟜m dti ← 1E¯8 + tc - t
    wphase ← w × phase ← ⋆⁼ dti
    a - fi × ( b + (c1 × •math.Cos wphase) + (c2 × •math.Sin wphase) )
}

LpplsSse ← {𝕊 tc‿m‿w‿a‿b‿c1‿c2 :
    +´ ⋆⟜2 ⊣ p - tc‿m‿w‿a‿b‿c1‿c2 Lppls t
}

a‿b‿c1‿c2 ← FitABC p‿t

MinTcMW ← { Fn tc‿m‿w : tc‿m‿w‿a‿b‿c1‿c2 LpplsSse t‿p}
# (↕≠)⊸⋈ p
#  {𝕏 _nelderMead m0‿w0} (ObjMW ((¯1+≠p)‿a‿b‿c1‿c2))⟜((↕≠)⊸⋈ p)

### Find optimal m‿w

m0 ← RGen ⟨0.1,0.9,8⟩
w0 ← RGen ⟨6,13,7⟩
tc0 ← ¯1+≠t

ObjMW ← {𝕊 m‿w : LpplsSse tc0‿m‿w‿a‿b‿c1‿c2}
m‿w ← ⊑ ObjMW _nelderMead m0‿w0

ObjTc ← { Fn ⟨tc⟩: LpplsSse tc‿m‿w‿a‿b‿c1‿c2}
⟨tc⟩ ← ⊑ ObjTc _nelderMead ⊢ ⟨n⟩


ObjTMW ← {𝕊 tc‿m‿w : LpplsSse tc‿m‿w‿a‿b‿c1‿c2}
tc‿m‿w ← ⊑ ObjMW _nelderMead tc0‿m0‿w0

# minMW ← { F←𝕏⋄ {F _nelderMead 𝕩}}  {𝕏⟜((↕≠)⊸⋈ p) } (ObjMW ((¯1+≠p)‿a‿b‿c1‿c2))
# minTc ← { F←𝕏⋄ {F _nelderMead 𝕩}}  {𝕏⟜((↕≠)⊸⋈ p) } (ObjTc m‿w‿a‿b‿c1‿c2)
# m‿w ← ⊑((⍋ ¯1⊸⊏˘)⊏⊏˘) >MinMW¨ <˘⍉>20⊸RGen¨ ⟨0.1,0.9,80⟩‿⟨6,13,7⟩
# tc ← ⊑((⍋ ¯1⊸⊏˘)⊏⊏˘)>MinTc¨ ≍¨ 20 •rand.Range ≠p
ll ← tc‿m‿w‿a‿b‿c1‿c2 Lppls t
GLine ll
GLine p
l ← p≍˘ll


GLines ← {
    plt ← Gnuplot "
        title 'LPPLS Algorithm' font ',18'
        terminal wxt size 1800,900
        style line 1 lt rgb 'black' lw 1"
    # plt.Plot (⍉>pix‿pcpix)‿" lw 2 lc rgb 'red' pt 7 ps 3"
    {plt.Plot (((↕≠)∾˘⊢)𝕩)‿"lw 1 lc rgb 'black' with lines"}¨ 𝕩
    "gnuplot-lppls-1.txt" •file.Chars plt.Debug @
    •SH "gnuplot"‿"-persist"‿"gnuplot-lppls-1.txt"
} 
GLines <˘⍉l

GLine ((¯1+≠p)‿m‿w‿a‿b‿c1‿c2) Lppls ↕≠p


Obj ← { Fn tc‿m‿w:
    dti ← (tc - taui) + 1E¯8
    wphase ← w × phase ← ⋆⁼ dti
    fi ← dti⋆m
    yi - ah - (bh × fi) - (c1h × fi × •math.Cos wphase) - (c2h × fi × •math.Sin wphase)
}



