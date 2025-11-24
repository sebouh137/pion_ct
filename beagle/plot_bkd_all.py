import matplotlib.pyplot as plt, numpy as np, pandas as pd
import mplhep as hep
hep.style.use("CMS")

fig,axs=plt.subplots(4,4, sharex='col', figsize=(20,20))
Q2s=[5.0,6.5,7.5, 8.5]
targets="1H 2H 12C 63Cu".split()


for i in range(4):
    for j in range(4):

        plt.sca(axs[j][i])
        Aname=targets[i]
        Q2=Q2s[j]
        if Aname=="1H":
            mA=0.9383
        elif Aname=="2H":
            mA=1.875612945
        elif Aname=="12C":
            mA=11.178
        elif Aname=="63Cu":
            mA=58.602
        
        plt.title(f"{Aname}, $Q^2$={Q2:.1f} GeV$^2$")

        if j == 3:
            plt.xlabel("$M_{miss}$ [GeV]")
        plt.ylabel("events")

        plt.axvline(mA, ls='-', color='k',alpha=0.5)
        plt.axvline(mA+0.1350, ls='-',color='k', lw=1, alpha=0.5)

        
        try:
            df=pd.read_csv(f"parsed/{targets[i]}_{Q2s[j]}.csv")
        except :
            continue


        y1,x,_=plt.hist(df.miss_mass, range=(mA-.2, mA+1.6), bins=60, label='all $\pi^+$ events')
        y2,x,_=plt.hist(df.query("secondary_pips+secondary_pims+secondary_pizs>0").miss_mass, range=(mA-.2, mA+1.6), bins=60, label='dihadron events')

        c1=np.cumsum(y1)
        c2=np.cumsum(y2)
        acceptable_contamination=0.05
        cut=9999
        for k in range(len(c1)):
            if c1[k]>200 and c2[k]/c1[k]>acceptable_contamination:
                cut=x[k]
                break
        plt.axvline(cut, ls='--', color='k', lw=1, alpha=0.5)
        
        print(Aname,Q2, sum(y2)/sum(y1), cut, c1[k-1]/sum(y1))
        if i == 0 and j == 0:
            plt.legend()

plt.subplots_adjust(hspace=0)
plt.tight_layout()
plt.savefig("backgrounds.pdf")
