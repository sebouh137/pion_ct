import numpy as np, pandas as pd, matplotlib.pyplot as plt,glob
from scipy.optimize import curve_fit

from matplotlib.backends.backend_pdf import PdfPages
import itertools

outdir="fits"
import os
try:
    os.mkdir(outdir)
except : pass
order=6;

nevents_gen=1e6

for mode, expand in itertools.product(("multi", "single"), (False, True)):
    tag = "" if not expand else "_expand_kinematics"
    f=open(f"fits_Q2tW_{mode}{tag}.csv","w")
    pdf=PdfPages(f'fits_Q2tW_{mode}{tag}.pdf')
    print("Q2,targ,var,min,max,"+",".join(f"p{i}" for i in range(order+1)),file=f)
    for Q2 in "5.0", "6.5", "7.5", "8.5":
        for targ in "1H", "2H", "12C", "63Cu":
            mA={"1H":.9383,"2H":1.876, "12C":11.178, "63Cu":58.647}[targ]
            #print(f"parsed/{targ}_{Q2}_*.csv")
            filenames=glob.glob(f"parsed/{targ}_{Q2}_*.csv")
            #print(filenames)
            df=pd.concat([pd.read_csv(a) for a in filenames])
            #print(df.columns)
            fig,axs=plt.subplots(1,3)
            labels='$Q^2$;$t$;$W$'.split(";")
            units="GeV$^2$","GeV$^2$","GeV"
        
            conv=1e9
        
            for i, var in enumerate(["Q2", "t", "W"]):
                plt.sca(axs[i])
                if mode=="multi":
                    q='secondary_esum>0'
                else:
                    q='secondary_esum==0'
                if not expand:
                    q+=" and accepted==3"
                a=df.query(q)[var]
                print(set(df.query(q).weight_ub))
                weights=df.query(q).weight_ub/nevents_gen*conv
                print("division success")
                r=(a.quantile(0.003), a.quantile(0.997)) if var != "phih" else (-np.pi,np.pi)
                bins=100
                #binwidth
                bw=(r[1]-r[0])/bins
                y,x,_= plt.hist(a, range=r, bins=bins, histtype='step', weights=weights/bw)
                bc=(x[1:]+x[:-1])/2

            
            
                fnc=lambda x,*p : np.polyval(p,x)
            
                p0=[0]*(order+1)
                P, cov=curve_fit(fnc, bc,y, p0, np.sqrt(y*bw/np.mean(weights))+(y==0))
                plt.plot(x,fnc(x,*P))
                plt.xlabel(labels[i]+((" ["+units[i]+"]") if units[i] != "" else "") )
                plt.ylabel("$d\\sigma/d"+labels[i].replace("$","")+"$"+((" [fb/"+units[i]+"]") if units[i] != "" else " [pb]"))
                plt.title(labels[i])
            
                print(Q2,targ,var,*(f"{a:.5f}" for a in r), *(f"{a:.5f}" for a in P),sep=',', file=f)
            fig.suptitle(f"{targ}, $Q^2$={Q2} GeV$^2$")
            plt.tight_layout()
            plt.ylim(0) #ensure that the y axis starts at 0

            plt.savefig(outdir+f"/{targ}_{Q2}{tag}.pdf")
            pdf.savefig()
            plt.close()
            #plt.show()
    f.close()
    pdf.close()
    
