
⟨MP, lup⟩←•Import "bqn-libs/matrix.bqn"
#a←3‿3⥊ 2×1+↕20
a←3‿3 •rand.Range 100
#b←4×2+↕3
b←3 •rand.Range 300
p‿l‿u ← lup.Decompose a
#•Show (-´⊸⋈) (p⊸⊏˘  ⊢ l MP u)‿a
x← p‿l‿u lup.Solve b 
≢x
((1e¯10<⟜|¨-´)⋈⊢) (a MP x)‿b
