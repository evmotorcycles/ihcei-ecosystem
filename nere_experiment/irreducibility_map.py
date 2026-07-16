# EXPLORATORY MAP (descriptive, NOT a hypothesis test):
# Where in this model family does static (params-only) predictability break down?
# Ground-truth irreducibility measured by the twin test (same params, many runs),
# independent of any predictor. Also report static AUC on a natural population.
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
T,B_CRIT,COLLAPSE = 200,12.0,36.0

def sim(U,D0,lam,K,rng):
    b=0.0
    for _ in range(T):
        Deff=D0/(1.0+np.exp(K*(b-B_CRIT))) if K>0 else D0*0.5
        arr=rng.poisson(lam); res=min(b+arr,rng.binomial(int(np.ceil(U)),Deff))
        b=max(0.0,b+arr-res)
    return b>COLLAPSE

print("EXPLORATORY MAP: irreducibility & static predictability vs tipping sharpness K")
print("  (irreducibility = mean coin-flip-ness of fate at FIXED params; 0.5=max, 0=determined)")
print(f"{'K':>5} {'collapse':>9} {'irreducibility':>15} {'static_AUC':>11}")
for K in [0.0,0.3,0.6,1.0,1.6,2.6]:
    rng=np.random.default_rng(21)
    # (a) ground-truth irreducibility: near-balance nodes, twin test
    nb=120; R=20
    U=rng.uniform(1.5,4.0,nb); D0=rng.uniform(0.4,0.95,nb)*rng.uniform(0.4,0.95,nb)
    m=U*D0; lam=m*(1+rng.uniform(-0.05,0.05,nb))         # near exact balance
    unc=[]
    for i in range(nb):
        r=np.random.default_rng(500+i)
        p=np.mean([sim(U[i],D0[i],lam[i],K,r) for _ in range(R)])
        unc.append(min(p,1-p))
    irr=np.mean(unc)
    # (b) static predictability on a NATURAL population (real param spread)
    N=3000
    U2=rng.uniform(1.5,4.0,N); D02=rng.uniform(0.4,0.95,N)*rng.uniform(0.4,0.95,N)
    m2=U2*D02; lam2=m2*(1+rng.uniform(-0.30,0.30,N))
    r2=np.random.default_rng(77)
    fate=np.array([int(sim(U2[i],D02[i],lam2[i],K,r2)) for i in range(N)])
    if 0<fate.mean()<1:
        X=np.column_stack([m2,lam2]); idx=r2.permutation(N); k=int(.7*N)
        M=LogisticRegression(max_iter=800).fit(X[idx[:k]],fate[idx[:k]])
        auc=roc_auc_score(fate[idx[k:]],M.predict_proba(X[idx[k:]])[:,1])
    else: auc=float('nan')
    print(f"{K:>5.1f} {fate.mean():>9.2f} {irr:>15.3f} {auc:>11.3f}")
print("\nRead: does static_AUC ever fall toward 0.5 as irreducibility rises?")
