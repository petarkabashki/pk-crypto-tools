########################################################
### Genetic Algo
#- Deals n numbers in interval with precision
RDeal ⇐ ((⊣•rand.Range ¯1⊸⊑)×((-´∘⌽2↑⊢)÷2⊸⊑))
#10 RDeal ⟨0,10,100⟩
#- Deals n elements from an array
ADeal ⇐ ((⊣ •rand.Range ≠∘⊢)⊏⊢)
#40 ADeal 10×↕5
#- Example deal multiple params
#(5⊸RDeal)‿(7⊸ADeal) {𝕎𝕩}¨ ⟨0,10,100⟩‿(5+↕10)
### Generates random parameters, Floating Point
GenRan ⇐	<˘∘⍉∘>((⊣ •rand.Range (2⊸⊑⊢))×((2⊸⊑÷˜⟜(1⊸⊑-⊑))⊢))¨ 
#3 GenRan ⟨1,1,1⟩‿⟨0,1,100⟩
 #•Fmt  1.123412341234
### Mutation
Mutate ⇐ {
	r←1+•rand.Range ¯1+≠⊑𝕩
	(r↑¨𝕩) ∾¨ r↓¨(•rand.Deal ≠𝕩) ⊏ 𝕩
}
Genetic ⇐ {
	pardefs ← 𝕩
	niter‿ntop‿nper‿Obj‿opar ← 𝕨
	#•Show opar
#{𝕩 Obj opar}¨ 
nper GenRan pardefs
	(>{𝕩⋈𝕩 Obj opar}¨ nper GenRan pardefs) {
		ntop ↑ ((⍒1⊸⊏˘)⊸⊏) 𝕩∾ >{𝕩⋈𝕩 Obj opar}¨  (⊏˘𝕩) (¬∘∊˜/⊢) (nper GenRan pardefs)∾(Mutate ⊏˘𝕩)
		
	}´ ↕niter
 }
