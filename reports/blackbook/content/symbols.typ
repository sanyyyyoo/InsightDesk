// Delete everything below the CONTENT marker (or leave it empty) and this
// page is skipped automatically.
//
// One symbol per line:   / symbol: meaning
// The template lines the symbols up in a column and adds the dash for you.
// Write symbols in maths mode, e.g. $V_"pp"$ for V with subscript pp.
//
// College rule: list Greek symbols first, then English letters (lower case
// before upper case), each group in alphabetical order.
// --- SETUP ---


// --- CONTENT ---
= List of Symbols

/ $delta$: Rise in reports per window that the CUSUM looks for (1)
/ $kappa$: Inter-annotator agreement (Fleiss' or Cohen's kappa)
/ $lambda_(u,t)$: Expected (baseline) complaint rate of case $u$ in window $t$
/ $sigma(A, B)$: Similarity of two cases (best pair of members)
/ $a, b$: Prior count and prior windows of the baseline rate (0.5, 7)
/ $c_(u,t)$: Number of counted complaints of case $u$ in window $t$
/ $e(x)$: Unit-length MiniLM embedding of complaint $x$
/ $h$: CUSUM alarm level (2)
/ $k_(u,t)$: CUSUM reference value
/ $m$: Minimum count for a vague-complaint alarm (2)
/ $n_C$: Number of counted reports in case $C$
/ $p$: Significance level of the Poisson tail test (0.001)
/ $s(x, y)$: Cosine similarity of two complaints
/ $t_"high"$: Upper threshold of the decision band (0.8306)
/ $t_"low"$: Lower threshold of the decision band (0.40 short text, 0.26 long text)
/ $v_(p,t)$: Number of vague complaints of product $p$ in window $t$
/ $C$: A problem case
/ $C^*$: Best candidate case of a complaint
/ $E_C$: Set of exemplars of case $C$ (at most 5)
/ $L$: Length of the baseline window (28 windows, 7 days)
/ $S(x, C)$: Score of complaint $x$ against case $C$
/ $S^*$: Score of the best candidate case
/ $S_(u,t)$: CUSUM statistic of case $u$ after window $t$
