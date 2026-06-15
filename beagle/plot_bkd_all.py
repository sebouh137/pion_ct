import matplotlib.pyplot as plt, numpy as np, pandas as pd
import mplhep as hep
hep.style.use("CMS")

fig,axs=plt.subplots(4,4, sharex='col', figsize=(20,20))
Q2s=[5.0,6.5,7.5, 8.5]
targets="1H 2H 12C 63Cu".split()

acceptable_contaminations=0.05,0.10,0.20

outfiles={}
for a in acceptable_contaminations:
    outfiles[a]=open(f"cuts_table_{a*100:.0f}pct.tex", "w")
    print("target & $Q^2$ [GeV$^2$] & $M_{\rm mass}$ cut [GeV] & \\% remaining \\\\\n\\hline", file=outfiles[a]) 

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
            import glob
            fname=f"parsed/{targets[i]}_{Q2s[j]}_*.csv"
            
            df=pd.concat([pd.read_csv(f) for f in glob.glob(fname)])
        except :
            continue


        y1,x,_=plt.hist(df.miss_mass, range=(mA-.2, mA+1.6), bins=60, label='single-pion events')
        y2,x,_=plt.hist(df.query("secondary_pips+secondary_pims+secondary_pizs>0").miss_mass, range=(mA-.2, mA+1.6), bins=60, label='dihadron events')

        c1=np.cumsum(y1)
        c2=np.cumsum(y2)
        for acceptable_contamination in acceptable_contaminations:
            cut=9999
            ac=acceptable_contamination
            for k in range(len(c1)):
                if c1[k]>100 and c2[k]/c1[k]>acceptable_contamination:
#                   cut=x[k+1]
                    # interpolate between the bin edges
                    a2=c2[k]/c1[k]
                    a1=c2[k-1]/c1[k-1]

                    interp=(ac-a1)/(a2-a1)
                    
                    cut=x[k+1]*interp+x[k]*(1-interp)
                    
                    break
            plt.axvline(cut, ls='--', color='k', lw=1, alpha=0.5)
            if Aname!="1H":

                s1_cut=len(df.query(f"miss_mass<{cut}"))
                s2_cut=len(df.query(f"secondary_pips+secondary_pims+secondary_pizs>0 and miss_mass<{cut}"))

                converged=abs((s2_cut/s1_cut)-ac)<.005
                
                if converged:
                    print(f"{Aname} & {Q2} & {cut:.2f} & {100*s1_cut/sum(y1):.0f}  \\\\",file=outfiles[acceptable_contamination])
                else:
                    print(f"{Aname} & {Q2} & * & *  \\\\",file=outfiles[acceptable_contamination])
        if i == 0 and j == 0:
            plt.legend()

for a in acceptable_contaminations:
    outfiles[a].close()
            
plt.subplots_adjust(hspace=0)
plt.tight_layout()
plt.savefig("backgrounds.pdf")
