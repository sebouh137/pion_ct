import numpy as np, pandas as pd, matplotlib.pyplot as plt,glob
from scipy.optimize import curve_fit

from matplotlib.backends.backend_pdf import PdfPages

outdir="fits"
import os
try:
    os.mkdir(outdir)
except : pass
order=6;
f=open("fits/fits.csv","w")
pdf=PdfPages(outdir+'all.pdf')
print("Q2,targ,var,min,max,"+",".join(f"p{i}" for i in range(order+1)),file=f)
for Q2 in "5.0", "6.5", "7.5", "8.5":
    for targ in "1H", "2H", "12C", "63Cu":
        mA={"1H":.9383,"2H":1.876, "12C":11.178, "63Cu":58.647}[targ]
        #print(f"parsed/{targ}_{Q2}_*.csv")
        filenames=glob.glob(f"parsed/{targ}_{Q2}_*.csv")
        #print(filenames)
        df=pd.concat([pd.read_csv(a) for a in filenames])
        #print(df.columns)
        fig,axs=plt.subplots(2,3)
        labels='$x$;$Q^2$;$m_{\\rm miss}$;$\\phi_\\pi$;$p_T^2$'.split(";")
        units='',"GeV$^2$","GeV","rad","GeV$^2$"
        
        for i, var in enumerate(["x", "Q2", "miss_mass", "phih", "pt2"]):
            plt.sca(axs[i//3][i%3])
            a=df.query('secondary_esum>0')[var]
            r=(a.quantile(0.003), a.quantile(0.997)) if var != "phih" else (-np.pi,np.pi)
            y,x,_= plt.hist(a, range=r, bins=100, histtype='step')
            bc=(x[1:]+x[:-1])/2
            if var != "phih":
                fnc=lambda x,*p : np.polyval(p,x)
            elif var!="miss_mass":
                fnc=lambda x, *p : np.sum([p[i]*np.cos(i*x) for i in range(len(p))], axis=0)
            else :
                fnc=lambda x,*p : np.polyval(p,x-mA)
            p0=[0]*(order+1)
            P, cov=curve_fit(fnc, bc,y, p0, np.sqrt(y)+(y==0))
            plt.plot(x,fnc(x,*P))
            plt.xlabel(labels[i]+((" ["+units[i]+"]") if units[i] != "" else "") )
            plt.title(labels[i])
            
            print(Q2,targ,var,*(f"{a:.5f}" for a in r), *(f"{a:.5f}" for a in P),sep=',', file=f)
        fig.suptitle(f"{targ}, $Q^2$={Q2} GeV$^2$")
        plt.tight_layout()
        plt.savefig(outdir+f"/{targ}_{Q2}.pdf")
        pdf.savefig()
        plt.close()
        #plt.show()
f.close()
pdf.close()
