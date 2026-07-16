# LOCKED pre-registered test. Mechanism fixed from design phase. One run.
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
T,EARLY,B_CRIT,K,COLLAPSE = 200,50,12.0,0.6,36.0

print("LOCKED PRE-REGISTRATION:")
print("  MC:      static AUC in band <= 0.75   (fate NOT set by params => irreducible)")
print("  P_main:  dynamic AUC - static AUC in band >= +0.10")
print("  P_ctrl:  static AUC off-band >= 0.85")
print("="*66)

def simulate(U,D0,lam,rng):
    b=0.0; tr=np.empty(T)
    for t in range(T):
        Deff=D0/(1.0+np.exp(K*(b-B_CRIT)))
        arr=rng.poisson(lam); res=min(b+arr, rng.binomial(int(np.ceil(U)),Deff))
        b=max(0.0,b+arr-res); tr[t]=b/max(U*Deff,1e-6)
    return (b>COLLAPSE), tr

rng=np.random.default_rng(11)
N=5000
U=rng.uniform(1.5,4.0,N); D0=rng.uniform(0.4,0.95,N)*rng.uniform(0.4,0.95,N)
m=U*D0; lam=m*(1+rng.uniform(-0.30,0.30,N))
band=np.abs(m-lam)/lam<0.15

fate=np.empty(N,dtype=int); tv_mean=np.empty(N); tv_slope=np.empty(N)
for i in range(N):
    c,tr=simulate(U[i],D0[i],lam[i],rng)
    fate[i]=int(c); e=tr[:EARLY]; tv_mean[i]=e.mean(); tv_slope[i]=e[-1]-e[0]

def auc(feat_cols, mask):
    X=np.column_stack(feat_cols)[mask]; y=fate[mask]
    if y.mean() in (0,1): return float('nan')
    idx=np.random.default_rng(3).permutation(len(y)); k=int(.7*len(y))
    tr,te=idx[:k],idx[k:]
    M=LogisticRegression(max_iter=800).fit(X[tr],y[tr])
    return roc_auc_score(y[te],M.predict_proba(X[te])[:,1])

Xstat=[m,lam]; Xdyn=[tv_mean,tv_slope]
print(f"nodes={N}  collapse_rate={fate.mean():.2f}  band_n={band.sum()}  offband_n={(~band).sum()}")
s_band=auc(Xstat,band); d_band=auc(Xdyn,band); b_band=auc(Xstat+Xdyn,band)
s_off =auc(Xstat,~band); d_off=auc(Xdyn,~band)
print("\nIN CRITICAL BAND (near tipping point):")
print(f"   static (params)    AUC = {s_band:.3f}")
print(f"   dynamic (trajectory)AUC = {d_band:.3f}")
print(f"   gain dynamic-static     = {d_band-s_band:+.3f}")
print("\nOFF BAND (far from tipping point):")
print(f"   static (params)    AUC = {s_off:.3f}")
print(f"   dynamic (trajectory)AUC = {d_off:.3f}")
print("\nVERDICTS vs pre-registration:")
print(f"   MC     (static_band<=0.75): {'PASS' if s_band<=0.75 else 'FAIL'}  [{s_band:.3f}]")
print(f"   P_main (gain>=+0.10):       {'PASS' if (d_band-s_band)>=0.10 else 'FAIL'}  [{d_band-s_band:+.3f}]")
print(f"   P_ctrl (static_off>=0.85):  {'PASS' if s_off>=0.85 else 'FAIL'}  [{s_off:.3f}]")
