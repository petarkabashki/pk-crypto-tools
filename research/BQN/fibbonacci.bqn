
⟨Gnuplot⟩ ← •Import "Gnuplot.bqn"

⟨JParse⇐Parse,JExport⇐Export⟩←•Import "bqn-libs/json.bqn"
⟨Split , Join,  SplitL, JoinL⟩←•Import "bqn-libs/csv.bqn"
⟨MP, Cholesky,Inverse⟩←•Import "bqn-libs/matrix.bqn"
#1‿1 MP 2‿2⥊4
⟨FmtNs, GLine, WMean, Ema, Var, WVar, WStd, GBars, CumBins, CumBinsPct, HBins, Hist, PHist⟩←•Import "pk-libs.bqn"

csv ← "',/" •Import "./bqn-libs/csv.bqn"  # Easier characters to write
csvdir ← "/media/grenada/Data/Crypto-Historical-Data/data-csv/binance/"

LdCsv ← { 
	base‿quote←𝕨⋄
	timeframe←𝕩⋄
	>•ParseFloat¨¨ 1↓ csv.SplitL •FLines csvdir ∾base∾"_"∾quote∾"-"∾timeframe∾".csv"⋄
}
#10↑⟨"BTC","USDT"⟩ LoadCandles "1d"

jsondir←"/media/mu6mula/Data/Crypto-Data-Feed/freq-user-data/data/binance/"
LdJson ←{ 
	>JParse •FChars jsondir∾(⊑𝕩)∾"_"∾(1⊑𝕩)∾"-"∾(𝕨)∾".json"
}
#  "1d" LdJson "BTC"‿"USDT" 
#LdJsLc ← {⋆⁼ ¯2⊏˘ 𝕨 LdJson 𝕩‿"USDT"}


#LnOhlc← {⋆⁼ ¯1↓˘1↓˘ 𝕨 LdJson 𝕩‿"USDT"} 
# lohlc← "1d" LnOhlc "AVAX"



#################################################################
### Directional Change / ZigZag Algorithm 
#################################################################
IfElse ← {cond‿True‿False: cond◶False‿True @}
TestConds ← {fn←{Cond‿Act 𝕊 else: Cond◶Else‿Act}´𝕩 ⋄ Fn@}

ohlc← ¯1000↑ "4h" LdJson "BTC"‿"USDT"
cl← ⋆⁼ ¯2⊸⊏˘ ohlc
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
pks ← 0.10 Peaks cl 
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

0
