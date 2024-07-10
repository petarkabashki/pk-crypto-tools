
⟨Gnuplot⟩ ← •Import "Gnuplot.bqn"
⟨ToTimestamp, FromTimestamp⟩ ← •Import "bqn-libs/datetime.bqn"
⟨JParse⇐Parse,JExport⇐Export⟩←•Import "bqn-libs/json.bqn"
⟨Split , Join,  SplitL, JoinL⟩←•Import "bqn-libs/csv.bqn"
⟨MP, Cholesky,Inverse⟩←•Import "bqn-libs/matrix.bqn"
#1‿1 MP 2‿2⥊4
⟨FmtNs, GLine, WMean, Ema, Var, WVar, WStd, GBars, CumBins, CumBinsPct, HBins, Hist, PHist, Ols⟩←•Import "pk-libs.bqn"

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
LdJsLc ← {⋆⁼ ¯2⊏˘ 𝕨 LdJson 𝕩‿"USDT"}
errmea←0.1


#######################################
### OLS
#######################################

df← •ParseFloat¨ 1↓˘ 1↓ >csv.SplitL •FLines "duncan.csv"
y ← ⊏˘ df
x ← ⍉≍1⊏˘ df
# Ols ← {xp←⍉x←1∾˘𝕩⋄((Inverse xp MP x) MP xp) MP 𝕨}
# ((Inverse ⍉⊸MP x) MP (⍉x)) MP y
y Ols x 


### Partition 𝕩 into 𝕨 parts
Partn ← { i0 Fn y: (⌊i0×↕⊸÷≠y)⊔y } 

3 { i0 Fn y: (⌊i0×↕⊸÷≠y)⊔y } ↕10

#######################################
### Todos:
#-V Parameter sweeps, continuous and discrete
#-V Parameter deals, continuous and discrete
#- Julia Sigma Points
#- Merwe Scaled Sigma Points
#- Unscented Kalman Filter
#- UKF linear for macro
#- UKF Fib Levels
#- Markov Chains & UKF
#- RL

#######################################
### Parameter Sweeping and Dealing (random selection)

#- Divides interval in n parts
#RSweep ← ((↕1⊸+)×÷)⊸×⟜(-´⌽)
RSweep← {s‿e←𝕩⋄d←(e-s)÷𝕨⋄s+d×↕1+𝕨}
10 RSweep ⟨5,10⟩
ISweep ← (⌊1e¯8⊸+)RSweep
#10 ISweep ⟨0,10⟩


#- Covariance
 Cov← {n←≠⊑𝕩⋄n÷˜+´×´(⊢-n÷˜+´)¨𝕩} 
 #Cov {a‿v←4‿3⋄(a+𝕩×v)⋈(≠𝕩)⥊v} ↕10

#- Cholesky Decomposition
#(cholesky.Decompose⊸⋈) (MP⟜⍉) > {(⌽(-𝕩)↑1+↕)¨1+↕𝕩} 2
#cholesky.Decompose >⟨⟨10, 5, 2⟩,⟨5, 3, 2⟩,⟨2, 2, 3⟩⟩
#- Merwe Scaled Sigma Points
Merwe_Sigmas ← {
	n‿a‿b‿k ← 𝕩
	l←((×˜a)×(n+k))-n 
	c←0.5÷n+l
	wm‿wc⇐(0‿(1+b-×˜a) + 2⥊l÷l+n) ∾¨ <wco←(n×2)⥊c
	Points⇐{
		x‿cov←𝕩
		x ((<⊣)(⊣∾+¨)⊢)  <˘∾´1‿¯1×<⍉cholesky.Decompose cov×n+l
	}
} 
(Merwe_Sigmas 2‿0.1‿2‿1).Points ⟨3‿4,(>⟨1‿0,2‿1⟩)⟩

#- Discrete white noise in 2-dim, check inconsistency with FilterPy
Q_dwn_2⇐ {sq←×˜𝕨⋄𝕩× 2‿2⥊(0.25×˜sq)∾(2⥊0.5×sq×𝕨)∾sq }
Q_dwn_4← {𝕩×(𝕨⋆<˘⌽⌽˘(↕+2⊸⥊⥊↕) 4) ÷ ⟨36,12,6,6⟩‿⟨12,4,2,2⟩‿⟨6,2,2,1⟩‿⟨6,2,1,1⟩ }
#Q_dwn_2 1‿0.02
#- Makes a new matrix double the size, placing the argument matrix in diagonal
MkTri← (2‿2⥊0)⊸(∾˘´∘(∾¨⌽⊸⋈)⋈) 
#MkTri 1 Q_dwn_2 0.02

Diag ← {𝕩⌾(0‿0⊸⍉)0⌜˜𝕩}
###- Unscented Kalman Filter
UKF←{
	dt‿std_x‿std_r‿⟨a‿b‿k⟩ ← 𝕩
	f←4‿4 ⥊ 1‿dt‿0‿0‿0‿1‿0‿0‿0‿0‿1‿dt‿0‿0‿0
	Fx←f⊸MP⋄Hx←0‿2⊸⊏⋄sigmaF⇐Merwe_Sigmas 4‿0.1‿2‿1
	q← MkTri 1 Q_dwn_2 0.02⋄r←Diag 2⥊std_r⋆2
	x_ini←4⥊0⋄p_ini←Diag 4⥊1
	UT← {
			x← +´sigmaF.wm × 𝕩
			p← 𝕨+ +´sigmaF.wc × (×⌜˜)¨ 𝕩 - <x
			x‿p
	}
	Filter⇐{
		(<x_ini‿p_ini){
			px‿pp← 0‿1⊏𝕨	
			sigmas← sigmaF.Points px‿pp
			y_si← Fx¨ sigmas
			x‿p ← q UT y_si
			z← Hx¨ y_si
			z_mu‿z_p← r UT z 
			si←Inverse z_p
			p_xz← +´sigma_F.wc×(y_si-¨<x) (×⌜)¨ (z-¨<z_mu)
			k← p_xz MP si
			z_resi←𝕩-z_mu
			ux← x+k MP z_resi
			up← p-k MP z_p MP ⍉k
			ux‿up
		}`𝕩
	}
} 

#- Test with data from the book
#zs←<˘1↓˘ >•ParseFloat¨¨ 1↓ csv.SplitL •FLines "sym.csv"
#{𝕩.Filter 10↑zs}UKF 1‿0.03‿0.3‿⟨0.1‿2‿1⟩

###- Linear Kalman Filter
LKF←{
	dt‿q_var‿r_var ← 𝕨
	f←(2‿2 ⥊ 1‿dt‿0‿1)⋄h←(≍1‿0)⋄
	q← 1 Q_dwn_2 q_var⋄
	r←Diag 1⥊r_var
	x_ini←(⊑𝕩)‿0⋄p_ini←Diag 2⥊1

	#x_ini←(⍉≍10‿4.5) 
	#p_ini←Diag 500‿49
	(<x_ini‿p_ini){
		⟨px,pp⟩← 0‿1⊏𝕨	
		x_pred← f MP px
		p_pred← (f MP pp MP ⍉f) + q
		s← (h MP p_pred MP ⍉h) + r
		k← p_pred MP (⍉h) MP Inverse s
		y← 𝕩 - h MP x_pred # residual
		ux← x_pred + k MP y
		up← p_pred - k MP h MP p_pred
		⟨ux,up⟩
	}`𝕩
} 
###- Test against the book implementation
#zs‿track ← <˘1↓⍉>•ParseFloat¨¨  1↓ csv.SplitL •FLines "nofpy.csv"
#xps←>{𝕩.Filter zs} LKF 1‿0.01‿10
#- Strategy Stats
XStats ⇐ {
		pnl‿cumpnl⇐𝕩
		ret⇐¯1⊑0∾cumpnl
		ntrades⇐≠pnl⋄nwins⇐+´pnl>0⋄nlosses⇐ntrades-nwins⋄winratio⇐nwins÷ntrades⋄
		wins⇐(0⊸<⊸/)pnl⋄losses⇐(0⊸≥⊸/)pnl⋄avgwin⇐(+´÷≠)wins⋄avgloss⇐(+´÷≠)losses⋄
		maxpnl⇐⌈`cumpnl
		ddn⇐-maxpnl-cumpnl
		maxddn⇐⌊´ddn
		vol⇐√Var pnl
		sharpe⇐ret÷vol
		toppnl⇐⌈´maxpnl
 	#stats⇐>⟨"#Trades:"‿ntrades, "#Wins:"‿nwins⟩
 	#•Show cumpnl
	#XRun ⇐ {XStats XPositions XExits XEntries 𝕨 XIndicators Xload 𝕩}
}
WPos← { ws‿ww←𝕨⋄we←ws+ww⋄
	ixin‿ixout‿pin‿pout‿pnl‿cumpnl← 𝕩

	wpmask←(ixout<we)∧(ixin>ws)
	wixin‿wixout‿wpin‿wpout←{(+´¬ixin≥ws)↓(-+´ixout>we)↓𝕩}¨ ixin‿ixout‿pin‿pout
	wcumpnl←+`wpnl←(¯0.002)+ -wpin-wpout
	wixin‿wixout‿wpin‿wpout‿wpnl‿wcumpnl
}


XRun ← {
	vthr‿tpthr ← 𝕨
	pos‿isig‿osig‿pent←<˘⍉>(<0‿0‿0‿0){
		in_pos‿sig_in‿sig_out‿p_in←𝕨
		o‿h‿l‿c‿k1‿v1←𝕩
		xin←(¬in_pos)∧ (v1>vthr) ∧ (c>k1) ∧ (l<k1)
		xout←in_pos∧ ((c<k1) ∨ (c>tpthr))
		#o‿h‿l‿c‿⟨k1,v1⟩‿⟨k2,v2⟩‿⟨k3,v3⟩←𝕩
		#xin←(¬in_pos)∧ (v2>0.01) ∧ (v3>0.01) ∧(k1>k2)∧(k2>k3) 
		#xout←in_pos∧ ((k1<k2)∨(k2<k3)) #∨(¯0.1>c-p_in)) (0.3<c-k1)∨
		xin_pos←(xin∧¬in_pos)∨(in_pos∧¬xout)
		xp_in←(xin×c)+(p_in×in_pos)
		xin_pos‿xin‿xout‿(xp_in)
	}`<˘𝕩
	ixin‿ixout←<˘(/isig) {𝕨≍𝕩∾((≠𝕨)>≠𝕩)⥊¯1+≠𝕩} / (¯1⊸↓ ∾ ¯1⊸⊑⟜pos) osig
	c←3⊑˘𝕩 # close price
	cumpnl←+`pnl←--´pin‿pout←<˘(>ixin‿ixout) ⊏ c
	ixin‿ixout‿pin‿pout‿pnl‿cumpnl
}
#3↑odata←0.001‿0.01‿10 XInd "1d"‿"SOL"
#3↑⍉>pos←0.01 XRun <˘odata
#FmtNs XStats ¯2↑pos
LnOhlc← {⋆⁼ ¯1↓˘1↓˘ 𝕨 LdJson 𝕩‿"USDT"} 
lohlc← "1d" LnOhlc "AVAX"
#¯1↑ ↕5
### Objective function
⊑1↑⟨⟩
Obj ← {
	kpar←(0⊑𝕨)∾0∾(1⊑𝕨)⋄
	rpar←¯2↑𝕨
	ohlc ← 𝕩
	odata← ohlc∾˘>⊏˘>kpar LKF ¯1⊏˘ ohlc
	pos← rpar XRun odata
	#odata‿pos
	⊑1↑⊑¯1‿¯1⊏pos
}
#0.001‿0.01‿10‿0.01 Obj lohlc
########################################################
### Genetic Algo
#- Deals n numbers in interval with precision
RDeal ← ((⊣•rand.Range ¯1⊸⊑)×((-´∘⌽2↑⊢)÷2⊸⊑))
#10 RDeal ⟨0,10,100⟩
#- Deals n elements from an array
ADeal ← ((⊣ •rand.Range ≠∘⊢)⊏⊢)
#40 ADeal 10×↕5
#- Example deal multiple params
#(5⊸RDeal)‿(7⊸ADeal) {𝕎𝕩}¨ ⟨0,10,100⟩‿(5+↕10)
### Generates random parameters, Floating Point
GenRan ←	<˘∘⍉∘>((⊣ •rand.Range (2⊸⊑⊢))×((2⊸⊑÷˜⟜(1⊸⊑-⊑))⊢))¨ 
#3 GenRan ⟨1,1,1⟩‿⟨0,1,100⟩
 #•Fmt  1.123412341234
### Mutation
Mutate ← {
	r←1+•rand.Range ¯1+≠⊑𝕩
	(r↑¨𝕩) ∾¨ r↓¨(•rand.Deal ≠𝕩) ⊏ 𝕩
}
Genetic ← {
	pardefs ← 𝕩
	niter‿ntop‿nper‿Obj‿opar ← 𝕨
	#•Show opar
#{𝕩 Obj opar}¨ 
nper GenRan pardefs
	(>{𝕩⋈𝕩 Obj opar}¨ nper GenRan pardefs) {
		ntop ↑ ((⍒1⊸⊏˘)⊸⊏) 𝕩∾ >{𝕩⋈𝕩 Obj opar}¨  (⊏˘𝕩) (¬∘∊˜/⊢) (nper GenRan pardefs)∾(Mutate ⊏˘𝕩)
		
	}´ ↕niter
 }
#{"strat-params.csv" •FLines •Fmt¨ <˘𝕩⋄𝕩} 100‿20‿20‿Obj‿lohlc Genetic ⟨1,1,1⟩‿⟨0.001,0.001,1⟩‿⟨1,1,1⟩‿⟨0,2,100⟩
{"strat-params.csv" •FLines •Repr¨  <˘𝕩⋄𝕩} "pars"‿"CumPnl"⊸∾ 100‿20‿50‿Obj‿lohlc Genetic ⟨0,0.002,100⟩‿⟨0,50,100⟩‿⟨0,0.2,100⟩‿⟨0,20,100⟩
#pars←⟨0.9316,26.32,0,0.94⟩
#pars Obj lohlc

ObjS ← {
	kpar←3↑𝕨⋄rpar←¯1⊑𝕨
	odata← 𝕩∾˘>⊏˘>kpar LKF ¯1⊏˘ 𝕩
	pos← rpar XRun odata
	odata‿pos
	#⊑1↑⊑¯1‿¯1⊏pos
}
#odata‿pos ← pars ObjS lohlc
#⍉>pos
#odata‿pos ← "1d"‿"SOL" Obj (<0.001‿0.01‿10)‿0.01
#{st←𝕩.stats⋄FmtNs 𝕩.stats⋄
#5 RSweep ⟨0.1,2.0⟩
#pars← {1‿𝕩‿0.1}¨  ÷10×1+↕5
#>kfs← { ⊑˘⊑˘> 𝕩 LKF ¯1⊏˘ lohlc}¨ pars
#odata←lohlc
#xs←pars (⋈¨) kfs
#ws←0⋄we←(≠odata)⋄ww←we-ws
ws←0⋄we←400⋄ww←we-ws
wodata←ww↑ws↓odata
#wixin‿wixout‿wpin‿wpout‿wpnl‿wcumpnl←ws‿ww WPOS pos
wks← pars ⋈¨ {ww↑ws↓𝕩}¨ kfs
#FmtNs XStats wpnl‿wcumpnl
ixs← ws+↕ww
plt ← Gnuplot "
	title 'Linear Kalman Filter' font ',18'
	terminal wxt size 2300,900
	y2tics nomirror tc lt 2
	style line 5 lt rgb 'cyan' lw 5 pt 6"
plt.Plot (ixs∾˘ 4↑˘wodata)‿"lw 1 with financebars title 'price'"
#plt.Plot (((⊑wixin)‿0)∾wixout∾˘wcumpnl)‿"lc rgb 'red' lw 1.5 with lines axes x1y2"
#plt.Plot (ixs∾˘4⊑˘wodata)‿"lw 2 with lines title 'K'"
{p‿x←𝕩⋄s←"lw 2 with lines title '"∾(•Fmt p)∾"'"⋄plt.Plot (ixs∾˘x)‿s}¨wks
#plt.Plot (⍉>wixin‿wpin)‿"with points pt 9 lw 6 lc rgb '#005500`'"
#plt.Plot (⍉>wixout‿wpout)‿"with points pt 9 lw 6 lc rgb 'red'"
"gnuplot-tmp-1.txt"•file.Chars plt.Debug @
•SH "gnuplot"‿"-persist"‿"gnuplot-tmp-1.txt"


#################################################
#4↑˘wodata
plt ← Gnuplot "
	title 'Linear Kalman Filter' font ',18'
	terminal wxt size 2300,900
	y2tics nomirror tc lt 2
	style line 5 lt rgb 'cyan' lw 5 pt 6"
plt.Plot (ixs∾˘ 4↑˘wodata)‿"lw 1 with financebars title 'price'"
plt.Plot (((⊑wixin)‿0)∾wixout∾˘wcumpnl)‿"lc rgb 'red' lw 1.5 with lines axes x1y2"
{p‿x←𝕩⋄s←"lw 2 with lines title '"∾(•Fmt p)∾"'"⋄plt.Plot (ixs∾˘x)‿s}¨wks
plt.Plot (⍉>wixin‿wpin)‿"with points pt 9 lw 6 lc rgb '#005500`'"
plt.Plot (⍉>wixout‿wpout)‿"with points pt 9 lw 6 lc rgb 'red'"
"gnuplot-tmp-1.txt"•file.Chars plt.Debug @
•SH "gnuplot"‿"-persist"‿"gnuplot-tmp-1.txt"





#{𝕩.Filter 3×↕5}UKF 1‿0.03‿0.3‿0.2‿⟨0.1‿2‿1⟩
#{𝕩.Pred 1‿2}UKF 1‿0.3‿⟨0.1‿2‿1⟩
###- All in one
#Merwe_Sigmas ← {
#	n‿a‿b‿k ← 𝕨
#	x‿cov←𝕩
#	l←((×˜a)×(n+k))-n 
#	c←0.5÷n+l
#	wm‿wc←(0‿(1+b-×˜a) + 2⥊l÷l+n) ∾¨ <wco←(n×2)⥊c
#	x ((<⊣)(⊣∾+¨)⊢)  <˘∾´1‿¯1×<⍉cholesky.Decompose cov×n+l
#} 
#2‿0.1‿2‿1 Merwe_Sigmas ⟨3‿4,(>⟨1‿0,2‿1⟩)⟩

#######################################
### GH-Filter aka Kalman Filter
###
⟨1,0⟩‿⟨2,4⟩
FGH←{
	dt‿g‿h←𝕨
	xpred‿xest‿dx ⇐ <˘⍉> (<(2⥊⊑𝕩)∾0){
		p_pred‿x_est‿dx←𝕨
		x_pred←x_est + dx×dt
		resid←𝕩-x_pred
		x_pred‿(x_pred + g×resid÷dt)‿(dx+h×resid÷dt)
	}`𝕩 
} 
#######################################
### Strategy
###
xStra ← {
	XLoad ⇐ {⋆⁼ ¯2⊏˘ (⊑𝕩) LdJson 1↓𝕩}
	XIndicators⇐{
		lc⇐𝕩
		ghpars⇐𝕨
		xest⇐(𝕨 FGH lc).xest
		abv⇐lc>xest
		crup⇐∧⟜(¬»)abv
		crdn⇐∧⟜(¬1⊸»)¬abv
	} 
	XEntries ⇐ {
		xind⇐𝕩
		#flt←0⊸<(⊢-») / xind.crup
		#flt ← 0.00 > ((2⥊0)⊸»-⊢)xind.xest
		xenter⇐xind.crup
	} 
	#XEntries 1‿0.001‿0.001 XIndicators "1d" LdJsLc "BTC"
	XExits ⇐ {
		xind‿xenter⇐𝕩	
		xexit⇐xind.crdn
	} 
	#xind‿xenter‿xexit ← XExits XEntries 1‿0.001‿0.001 XIndicators lc
	XPositions ⇐ {
		xind‿xenter‿xexit⇐𝕩	
		posinx⇐ /xenter
		poslens⇐1↓(((+´∘¬∨`)))¨ (+`xenter) ⊔ xexit
		posoutx⇐ ((≠xind.lc)-1)⌊posinx+poslens
		cio ⇐ (posinx≍posoutx) ⊏ xind.lc 
		pnl⇐--˝cio
		cumpnl⇐+`pnl
		#wins⇐
		#winrate⇐ (()÷≠) pnl
	} 
	XStats ⇐ {
		pnl‿cumpnl⇐𝕩
		stats⇐{
			ret⇐¯1⊑0∾cumpnl
			ntrades⇐≠pnl⋄nwins⇐+´pnl>0⋄nlosses⇐ntrades-nwins⋄winratio⇐nwins÷ntrades⋄
			wins⇐(0⊸<⊸/)pnl⋄losses⇐(0⊸≥⊸/)pnl⋄avgwin⇐(+´÷≠)wins⋄avgloss⇐(+´÷≠)losses⋄
			maxpnl⇐⌈`cumpnl
			ddn⇐-maxpnl-cumpnl
			maxddn⇐⌊´ddn
			vol⇐√Var pnl
			sharpe⇐ret÷vol
			toppnl⇐⌈´maxpnl
		}
		#stats⇐>⟨"#Trades:"‿ntrades, "#Wins:"‿nwins⟩
		#•Show cumpnl
	}
	XRun ⇐ {XStats XPositions XExits XEntries 𝕨 XIndicators Xload 𝕩}
}

{st←𝕩.stats⋄FmtNs 𝕩.stats⋄
#	plt ← Gnuplot "
#		title 'Line plot' font ',18'
#		terminal wxt size 1300,600
#		style line 5 lt rgb 'cyan' lw 5 pt 6"
#	plt.Plot (((↕≠)∾˘⊢)𝕩.cumpnl)‿"lw 1 lc rgb 'black' with lines"
#	plt.Plot (((↕≠)∾˘⊢)st.maxpnl)‿"lw 1 lc rgb 'blue' with lines"
#	plt.Plot (((↕≠)∾˘⊢)st.ddn)‿"lw 1 lc rgb 'blue' with lines"
#	"gnuplot-tmp-1.txt"•file.Chars plt.Debug @
#	•SH "gnuplot"‿"-persist"‿"gnuplot-tmp-1.txt"
} ⟨0.45,0.06138,0.00598⟩ xStra.XRun "8h"‿"ALGO"‿"USDT"
#xStra.XStats xStra.XPositions xStra.XExits xStra.XEntries⟨0.45,0.06138,0.00598⟩ xStra.XIndicators xStra.Xload "8h"‿"ALGO"‿"USDT"
#GStra ←{
#	#stra← XPositions XExits XEntries 1‿0.001‿0.001 XIndicators lc
#	stra ← 𝕩
#	ymin‿ymax← ⌊‿⌈ {𝕎 ´ 𝕩}¨<stra.xind.lc
#	ts←↕≠stra.xind.lc
#	ws‿ww←0‿(≠stra.xind.lc)
#	•Show stra.xind.ghpars
#	plt ← Gnuplot "
#		title 'G-H Filter:"∾(•Fmt stra.xind.ghpars)∾"' font ',18'
#		terminal wxt size 2200,1300
#		y2tics nomirror tc lt 2
#		style line 5 lt rgb 'cyan' lw 5 pt 6
#		style fill empty"
#	#xs←plt.Debug @
##	plt.Plot (⍉stra.posinx≍⊏stra.cio)‿" with lines"
#	plt.Plot (ww↑ws↓ts∾˘stra.xind.lc)‿"lw 1 lc rgb 'blue' with lines"
#	plt.Plot (ww↑ws↓ts∾˘stra.xind.xest)‿"lw 1.5 with lines"
#	plt.Plot (0‿0∾⍉stra.posoutx≍stra.cumpnl)‿"lc rgb 'red' lw 1.5 with lines axes x1y2"
#	"gnuplot-tmp-1.txt"•file.Chars plt.Debug @
#	•SH "gnuplot"‿"-persist"‿"gnuplot-tmp-1.txt"
#	𝕩
#} 

#GStra XPositions XExits XEntries 1‿0.04‿0.02 XIndicators (⋆⁼ ¯2⊏˘ "8h"⊸LdJson "BTC"‿"USDT") 

##########################################################
### Genetic Algorithm for Parameter Tuning
###########

### Generates random parameters, Floating Point
GenRan ←	<˘∘⍉∘>((⊣ •rand.Range (2⊸⊑⊢))×((2⊸⊑÷˜⟜(1⊸⊑-⊑))⊢))¨ 
3 GenRan ⟨0,10,100⟩‿⟨0,1,100⟩
### Objective function
{𝕏 2.71} ÷

### Optimizes Max Drawdown
Obj← { {𝕩.stats.toppnl} 𝕩 xStra.XRun "8h"‿"ALGO"‿"USDT" }
#Optimizes PNL
#Obj← {stra←XPositions XExits XEntries 𝕩 XIndicators (⋆⁼ ¯2⊏˘ "8h"⊸LdJson "LINK"‿"USDT") ⋄ ¯1⊑(0∾stra.cumpnl)}

#((Obj¨ <˘))
### Calculate Obj on list of params
#>(⋈⟜Obj)¨ 5 GenRan ⟨0,10,100⟩‿⟨0,1,100⟩‿⟨0,1,100⟩
### Mutation
Mutate ← {
	r←1+•rand.Range ¯1+≠⊑𝕩
	(r↑¨𝕩) ∾¨ r↓¨(•rand.Deal ≠𝕩) ⊏ 𝕩
}
Genetic ← {
	pardefs ← 𝕩
	niter‿ntop‿nper ← 𝕨
	(>(⋈⟜Obj)¨ nper GenRan pardefs) {
		ntop ↑ ((⍒1⊸⊏˘)⊸⊏) 𝕩∾ >(⋈⟜Obj)¨  (⊏˘𝕩) (¬∘∊˜/⊢) (nper GenRan pardefs)∾(Mutate ⊏˘𝕩)
		
	}´ ↕niter
 }
{"strat-params.csv" •FLines •Fmt¨ <˘𝕩⋄𝕩} 50‿20‿20 Genetic ⟨0,5,10⟩‿⟨0.0,1,100⟩‿⟨0.0,1,1000⟩
 
3.05‿0.05‿0.22
0.7‿0.01‿0.222
2.25‿0.01‿0.222

#stra←GStra XPositions XExits XEntries 1‿0.03‿0.001 XIndicators (⋆⁼ ¯2⊏˘ "4h"⊸LdJson "BTC"‿"USDT")
#
#stra←XPositions XExits XEntries 1‿0.02‿0.001 XIndicators 500↑ lc
#0‿0∾⍉stra.posoutx≍stra.cumpnl
#stra.posinx

#############################################
### Parameter sweeping

### Nudge a value by percentage in n steps
Nudge ← {p‿n←𝕨⋄𝕩×1+(p÷n)×((↕1⊸+)+∘-⌊∘÷⟜2)n}

dxv←2‿1000 Nudge 3
gv←3‿1000 Nudge 0.6
hv←0.3‿1000 Nudge 0.2
lc←(⋆⁼ ¯2⊏˘ "4h"⊸LdJson "BTC"‿"USDT")

pp←dxv≍({𝕩‿0.6‿0.2}¨ dxv) { ¯1⊑0∾(XPositions XExits XEntries 𝕨 XIndicators 𝕩).cumpnl}¨ <lc
#pp←gv≍({3.05‿𝕩‿0.227}¨ gv) { ¯1⊑0∾(XPositions XExits XEntries 𝕨 XIndicators 𝕩).cumpnl}¨ <lc
#pp←hv≍({3.05‿0.6‿𝕩}¨ hv) { ¯1⊑0∾(XPositions XExits XEntries 𝕨 XIndicators 𝕩).cumpnl}¨ <lc
plt ← Gnuplot "
	title 'Line plot' font ',18'
	terminal wxt size 1300,600
	style line 5 lt rgb 'cyan' lw 5 pt 6"
plt.Plot (⍉pp)‿"lw 1 lc rgb 'blue' with lines"
"gnuplot-tmp-1.txt"•file.Chars plt.Debug @
•SH "gnuplot"‿"-persist"‿"gnuplot-tmp-1.txt"



#############################################
### Cross-asset pnls

# 1d
#top100←⟨"AAVE","ADA","ALGO","AMP","APT","ARB","ASTR","ATOM","AVAX","AXS","BCH","BLUR","BNB","BONK","BTC","CAKE","CFX","CHZ","CRV","DOGE","DOT","DYM","EGLD","ENJ","ENS","EOS","ETC","ETH","FIL","FLOW","FTM","GALA","GNO","GRT","HBAR","ICP","ILV","IMX","INJ","IOTA","JUP","KAVA","KLAY","KSM","LDO","LINK","LRC","LTC","LUNA","LUNC","MANA","MANTA","MATIC","MINA","MKR","NEAR","NEO","OP","ORDI","OSMO","PENDLE","PYR","PYTH","QNT","RAY","REN","RNDR","ROSE","RUNE","SAND","SEI","SHIB","SNX","SOL","STX","SUI","THETA","TIA","TRX","UNI","USDC","VET","WOO","XLM","XMR","XRP","XTZ","ZIL"⟩
top100←⟨"AAVE","ADA","ALGO","APT","ARB","ASTR","ATOM","AVAX","AXS","BCH","BLUR","BNB","BONK","BTC","CAKE","CHZ","DOGE","DOT","DYM","EGLD","ENJ","ETC","ETH","FIL","FTM","GALA","GNO","GRT","HBAR","ILV","IMX","INJ","IOTA","JUP","KLAY","KSM","LDO","LINK","LRC","LTC","LUNA","MANA","MANTA","MATIC","MINA","MKR","NEAR","NEO","OP","ORDI","OSMO","PENDLE","PYTH","RNDR","ROSE","RUNE","SAND","SEI","SHIB","SOL","STX","SUI","THETA","TIA","TRX","UNI","USDC","VET","WOO","XLM","XRP","ZIL"⟩

#######################################################
### Parameter Sweep over the whole portfolio of top 100
###
#pp←(⊢≍{+´1⊏˘((⍋1⊸⊏˘)⊏⊢) ⍉top100≍pnls←(<3‿𝕩‿0.001) { ¯1⊑0∾(XPositions XExits XEntries 𝕨 XIndicators 𝕩).cumpnl}¨ (⋆⁼ ¯2⊏˘ "1d"⊸LdJson)¨ (top100) ⋈¨ <"USDT"}¨) 1.5‿50 Nudge 0.12
#pp←(⊢≍{+´1⊏˘((⍋1⊸⊏˘)⊏⊢) ⍉top100≍pnls←(<𝕩‿0.12‿0.001) { ¯1⊑0∾(XPositions XExits XEntries 𝕨 XIndicators 𝕩).cumpnl}¨ (⋆⁼ ¯2⊏˘ "1d"⊸LdJson)¨ (top100) ⋈¨ <"USDT"}¨) 2‿50 Nudge 3
#pp←(⊢≍{+´1⊏˘((⍋1⊸⊏˘)⊏⊢) ⍉top100≍pnls←(<3‿0.12‿𝕩) { ¯1⊑0∾(XPositions XExits XEntries 𝕨 XIndicators 𝕩).cumpnl}¨ (⋆⁼ ¯2⊏˘ "1d"⊸LdJson)¨ (top100) ⋈¨ <"USDT"}¨) 2‿100 Nudge  0.001

#plt ← Gnuplot "
#	title 'Line plot' font ',18'
#	terminal wxt size 1300,600
#	style line 5 lt rgb 'cyan' lw 5 pt 6"
#plt.Plot (⍉pp)‿"lw 1 lc rgb 'blue' with lines"
#"gnuplot-tmp-1.txt"•file.Chars plt.Debug @
#•SH "gnuplot"‿"-persist"‿"gnuplot-tmp-1.txt"

#######################################################



apnls←((⍋1⊸⊏˘)⊏⊢) ⍉top100≍pnls
+´1⊏˘apnls
3↑klines← "1d" LdJson "XRP"‿"USDT"
3↑ lohlc← ⋆⁼ 1↓˘ ¯1↓˘ klines 
lc←¯1⊏˘lohlc









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
 
