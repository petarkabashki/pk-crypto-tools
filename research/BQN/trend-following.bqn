⟨Gnuplot⟩ ← •Import "Gnuplot.bqn"

⟨JParse⇐Parse⟩←•Import "bqn-libs/json.bqn"
⟨WMean, Ema, Var, WVar, WStd, GBars, CumBins, CumBinsPct, HBins, Hist, PHist⟩←•Import "pk-libs.bqn"

dfld←"/media/grenada/Data/Crypto-Data-Feed/freq-user-data/data/binance/"
3↑tkls←>JParse •FChars dfld∾"ALGO_USDT-8h.json" 
3↑ lcl← ⋆⁼ 1↓˘ ¯1↓˘ tkls
≢lcl
≠(0⊑˘tkls)
3↑ (1↑˘tkls) ∾˘ lcl
lcl

emaf‿emas←26‿50 {
	ns‿nf←𝕨
	ns‿nf {𝕨⊸Ema 𝕩}¨ <¯1⊏˘lcl
} lcl

⥊¯1↑˘ lcl
#bars 4.0
#style line 5 lt rgb 'cyan' lw 3 pt 6
#plt.Plot (200↑(1↑˘tkls) ∾˘ lcl)‿"with candlesticks"
# Index/TimeStamps
#3↑ts←1↑˘tkls
¯10↑ts←↕≠tkls
ws‿ww←800‿800
plt ← Gnuplot "
	title 'Candlesticks' font ',18'
	terminal wxt size 1300,600
  style line 5 lt rgb 'cyan' lw 5 pt 6
  style fill empty"
#plt.Plot 𝕩‿"using 1:2 with boxes fillstyle pattern 5 title ''"
#plt.Plot (ww↑ws↓ts∾˘lcl)‿"with financebars"
plt.Plot (ww↑ws↓ts∾˘¯1⊏˘lcl)‿"lw 1 lc rgb 'blue' with lines"
plt.Plot (ww↑ws↓ts∾˘emaf)‿"lw 1 lc rgb 'orange' with lines"
plt.Plot (ww↑ws↓ts∾˘emas)‿"lw 1 lc rgb 'green' with lines"
"gnuplot-tmp-1.txt"•file.Chars plt.Debug @
•SH "gnuplot"‿"-persist"‿"gnuplot-tmp-1.txt"

