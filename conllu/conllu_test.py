from io import open
from conllu import parse, parse_incr, parse_tree_incr
from conllu_models import print_tree_b
from nltk.parse import DependencyGraph

data_file = open("../data_test/UD_English/test.conllu", "r", encoding="utf-8")
for tokentree in parse_tree_incr(data_file):

    tokentree.print_tree()
    t = print_tree_b(tokentree)
    print(t)

# data = """
# 1	Al	Al	PROPN	NNP	Number=Sing	0	root	_	SpaceAfter=No
# 2	-	-	PUNCT	HYPH	_	1	punct	_	SpaceAfter=No
# 3	Zaman	Zaman	PROPN	NNP	Number=Sing	1	flat	_	_
# 4	:	:	PUNCT	:	_	1	punct	_	_
# 5	American	american	ADJ	JJ	Degree=Pos	6	amod	_	_
# 6	forces	force	NOUN	NNS	Number=Plur	7	nsubj	_	_
# 7	killed	kill	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	1	parataxis	_	_
# 8	Shaikh	Shaikh	PROPN	NNP	Number=Sing	7	obj	_	_
# 9	Abdullah	Abdullah	PROPN	NNP	Number=Sing	8	flat	_	_
# 10	al	al	PROPN	NNP	Number=Sing	8	flat	_	SpaceAfter=No
# 11	-	-	PUNCT	HYPH	_	8	punct	_	SpaceAfter=No
# 12	Ani	Ani	PROPN	NNP	Number=Sing	8	flat	_	SpaceAfter=No
# 13	,	,	PUNCT	,	_	8	punct	_	_
# 14	the	the	DET	DT	Definite=Def|PronType=Art	15	det	_	_
# 15	preacher	preacher	NOUN	NN	Number=Sing	8	appos	_	_
# 16	at	at	ADP	IN	_	18	case	_	_
# 17	the	the	DET	DT	Definite=Def|PronType=Art	18	det	_	_
# 18	mosque	mosque	NOUN	NN	Number=Sing	7	obl	_	_
# 19	in	in	ADP	IN	_	21	case	_	_
# 20	the	the	DET	DT	Definite=Def|PronType=Art	21	det	_	_
# 21	town	town	NOUN	NN	Number=Sing	18	nmod	_	_
# 22	of	of	ADP	IN	_	23	case	_	_
# 23	Qaim	Qaim	PROPN	NNP	Number=Sing	21	nmod	_	SpaceAfter=No
# 24	,	,	PUNCT	,	_	21	punct	_	_
# 25	near	near	ADP	IN	_	28	case	_	_
# 26	the	the	DET	DT	Definite=Def|PronType=Art	28	det	_	_
# 27	Syrian	syrian	ADJ	JJ	Degree=Pos	28	amod	_	_
# 28	border	border	NOUN	NN	Number=Sing	21	nmod	_	SpaceAfter=No
# 29	.	.	PUNCT	.	_	1	punct	_	_
# """
#
# d = DependencyGraph(data)
# pass