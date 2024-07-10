
⟨Gnuplot⟩ ← •Import "Gnuplot.bqn"
⟨ToTimestamp, FromTimestamp⟩ ← •Import "bqn-libs/datetime.bqn"
⟨JParse⇐Parse,JExport⇐Export⟩←•Import "bqn-libs/json.bqn"
⟨Split , Join,  SplitL, JoinL⟩←•Import "bqn-libs/csv.bqn"
⟨MP, Cholesky,Inverse⟩←•Import "bqn-libs/matrix.bqn"
#1‿1 MP 2‿2⥊4
⟨FmtNs, GLine, WMean, Ema, Var, WVar, WStd, GBars, CumBins, CumBinsPct, HBins, Hist, PHist, Ols⟩←•Import "pk-libs.bqn"



#######################################
### Hurst Exponent
#######################################

HRs ← {Fn x: 
	y ← (-⟜(+´÷≠)) x
	z ← +` y
	rn ← (⌈´-⌊´) z ⋄ 
	# ((+´ ⋆⟜2)÷≠) y
	sn ← √ ((+´ ⋆⟜2)÷≠) y ⋄ 
	rn÷sn 

}
Hurst ← { Fn x:
	p←2⋆⁼≠x
	sr ← 2+↕¯1+ 2⋆⁼≠x
	srs ← 2⊸⋆ sr
	srn←(≠x)÷srs
	HRs¨¨ (srs ×¨↕¨srn) {𝕩↑𝕨↓x}¨¨ srs
	rss ← (+´÷≠)¨ HRs¨¨ (srs ×¨↕¨srn) {𝕩↑𝕨↓x}¨¨ srs
	(2⋆⁼rss)
	¯1⊑(2⋆⁼rss) Ols (2⋆⁼srs)
}

binanceDir← "/media/mu6mula/Data/Crypto-Data-Feed/freq-user-data/data/binance/"
FName ← {t‿q‿b←𝕨∾<𝕩⋄binanceDir∾b∾"_"∾q∾"-"∾t∾".json"}
≠df ← "4h" { ¯1↓˘>JParse •FChars 𝕨‿"USDT" FName 𝕩} "BTC"
#≠x ← 0∾ 1↓ (-⟜1∘÷⟜») ¯1⊏˘ df 

ws‿ww ← 2000‿(2000)
≠c ←ww↑ ws↓ ¯1⊏˘ df 
≠x ← 0∾ 1↓ (-⟜1∘÷⟜») c

3↑ts ← 3⊸↑¨ ToTimestamp¨  ÷⟜1000 ww↑ws↓ ⊏˘df
# •UnixTime¨ ÷⟜1000 5↑ ⊏˘df
# x←1+↕5


hw ← 256
≢hx ← ≍˘Hurst¨ <˘ hw ↕ x

plt ← Gnuplot "
	title 'Ichimoku Cloud' font ',18'
	terminal wxt size 2400,900
	y2tics 0.20 nomirror tc lt 2
	grid
	parametric
	style line 5 lt rgb 'cyan' lw 3 pt 6"

plt.Plot (((hw⊸+∘↕≠)∾˘⊢)hx)‿"lw 1 lc rgb 'blue' with lines"
plt.Plot (((↕≠)∾˘⊢)≍˘⋆⁼c)‿"lw 2 lc rgb 'orange' with lines axes x1y2"

"gnuplot-tmp-1.txt"•file.Chars plt.Debug @
•SH "gnuplot"‿"-persist"‿"gnuplot-tmp-1.txt"
