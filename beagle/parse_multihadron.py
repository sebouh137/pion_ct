import numpy as	np, pandas as pd, sys

infile=sys.argv[1]
outfile=sys.argv[2]
kin_i=int(sys.argv[3])
A=sys.argv[4]
if A=='1H':
    mA=0.9383
elif A=='2H':
    mA=1.875612945
elif A=="12C":
    mA=11.178
elif A=='63Cu':
    mA=58.602
else:
    print("error:  unknown target")
    exit(0)

if kin_i<4:
    acc=pd.read_csv("acceptance.csv")
    Ebeam=10.7
else :
    # kin_i= 4 through 8 are the old experiment's kinematics
    kin_i-=4
    acc=pd.read_csv("acceptance_old.csv")
    Ebeam=(4.021, 5.012, 5.012, 5.767,5.767)[kin_i]

for a in 'p_pi','th_pi','p_e','th_e':
    acc[f'min_{a}_loose'], acc[f'max_{a}_loose']=3/2*acc[f'min_{a}']-1/2*acc[f'max_{a}'],-1/2*acc[f'min_{a}']+3/2*acc[f'max_{a}']
    #P>acc.min_p_pi[kin_i] and P<acc.max_p_pi[kin_i] and\
    #    th>acc.min_th_pi[kin_i] and th<acc.max_th_pi[kin_i]:

with open(infile,"r") as inf, open(outfile,"w")	as outf:
    print("x,Q2,W,miss_mass,phih,pt2,t,secondary_pips,secondary_pims,secondary_pizs,secondary_esum,accepted", file=outf)
    secondary_pips=0
    secondary_pims=0
    secondary_pizs=0
    secondary_esum=0
    electron_kin=None
    pion_kin=None
    accepted=0
    for line in inf.readlines():
        split=line.split()
        if len(split)<2:
            continue
        is_electron= split[1]=='1' and split[2]=='11'
        is_pion= (split[1]=='1' and (split[2] == '211' or split[2] == '-211')) or (split[1]=='2' and split[2] == '111')

        if is_electron or is_pion:

            px,py,pz,E=float(split[7]),float(split[8]),float(split[9]),float(split[10])
            P=np.sqrt(px**2+py**2+pz**2)
            th=np.arctan2(np.hypot(px,py),-pz)

            #if(is_pion):
                #print(split[2], P, th)
            if is_electron and P>acc.min_p_e_loose[kin_i] and P<acc.max_p_e_loose[kin_i] and th>acc.min_th_e_loose[kin_i] and th<acc.max_th_e_loose[kin_i]:
                electron_kin=E,px,py,pz,th
                #print("acc e")
                if P>acc.min_p_e[kin_i] and P<acc.max_p_e[kin_i] and th>acc.min_th_e[kin_i\
] and th<acc.max_th_e[kin_i]:
                    accepted=accepted|1
            elif is_pion and split[2] == '211' and P>acc.min_p_pi_loose[kin_i] and P<acc.max_p_pi_loose[kin_i] and th>acc.min_th_pi_loose[kin_i] and th<acc.max_th_pi_loose[kin_i]:
                pion_kin=E,px,py,pz,th
                #print("acc pi")
                if P>acc.min_p_pi[kin_i] and P<acc.max_p_pi[kin_i] and\
 th>acc.min_th_pi[kin_i] and th<acc.max_th_pi[kin_i]:
                    accepted=accepted|2
            elif is_pion:
                if split[2]=='211':
                    secondary_pips+=1
                elif split[2]=='-211':
                    secondary_pims+=1
                elif split[2]=='111':
                    secondary_pizs+=1
                secondary_esum+=E
        if "Event finished" in line:
            if electron_kin is not None and pion_kin is not None:
                miss_mass2=(Ebeam+mA-pion_kin[0]-electron_kin[0])**2-(-pion_kin[1]-electron_kin[1])**2-(-pion_kin[2]-electron_kin[2])**2-(-Ebeam-pion_kin[3]-electron_kin[3])**2

                # next check if the two particles are within the oop acceptance.
                # to avoid throwing out events force the electron to be in oop
                # acceptance by rotating along the z axis.

                phi_e=np.arctan2(electron_kin[2],electron_kin[1])
                phi_pi=np.arctan2(pion_kin[2],pion_kin[1])
                
                theta_e_central=(acc.min_th_e[kin_i]+acc.max_th_e[kin_i])/2
                theta_pi_central=(acc.min_th_pi[kin_i]+acc.max_th_pi[kin_i])/2

                theta_e=electron_kin[4]
                theta_pi=pion_kin[4]
                
                import random
                r=random.Random()
                phi_e_rot=phi_e
                count=0 #if you can't get the oop thing to work, skip the event
                while True:
                    phi_e_rot=2*np.sin(theta_e_central)*r.uniform(-acc.max_oop_e[kin_i], acc.max_oop_e[kin_i])
                    #oop_electron=np.arccos(np.sin(theta_e)*np.cos(phi_e_rot)*np.sin(theta_e_central)+np.cos(theta_e)*np.cos(theta_e_central))
                    #sin(theta_e)*cos(phi_e),sin(theta_e)*sin(phi_e), cos(theta_e)
                    #
                    oop_electron=np.arctan2(np.sin(theta_e)*np.sin(phi_e_rot),
                                            np.cos(theta_e_central)*np.cos(theta_e)*np.cos(phi_e_rot)+np.sin(theta_e_central)*np.sin(theta_e))
                    if abs(oop_electron)<acc.max_oop_e[kin_i]:
                        break
                    count+=1
                    if count>100:
                        print("failed oop")
                        break
                if count>100:
                    break
                phi_pi_rot=phi_pi+phi_e_rot-phi_e+np.pi
                oop_pion=np.arctan2(np.sin(theta_pi)*np.sin(phi_pi_rot),
                                            np.cos(theta_pi_central)*np.cos(theta_pi)*np.cos(phi_pi_rot)+np.sin(theta_pi_central)*np.sin(theta_pi))

                if abs(oop_pion)<acc.max_oop_pi[kin_i]:
                    
                    E_e=electron_kin[0]
                    theta_e=electron_kin[4]
                    Q2=4*Ebeam*E_e*np.sin(theta_e/2)**2
                    x=Q2/(2*.9383*(Ebeam-E_e))
                    W=np.sqrt(-Q2+.9383**2+2*.9383*(Ebeam-E_e));
                    E_pi,px_pi,py_pi,pz_pi=pion_kin[0:4]
                    E_e,px_e,py_e,pz_e=electron_kin[0:4]

                    #print("mpi=",np.sqrt(E_pi**2-px_pi**2-py_pi**2-pz_pi**2))
                    
                    #get the transformation to get phih
                    # note:  in BeAGLE, the electron beam is in the -z direction.  
                    qx,qy,qz=-px_e,-py_e,-Ebeam-pz_e

                    print('this should be zero', qx**2+qy**2+qz**2-(Ebeam-E_e)**2-Q2)
                    #print(f"{180/np.pi*np.atan2(np.hypot(qx,qy),qz):.3f}\t{theta_pi*180/np.pi:.3f}")
                    
                    qdote=qx*px_e+qy*py_e+qz*pz_e
                    q2=(qx**2+qy**2+qz**2)
                    tmp=qdote/q2
                    Sxx,Sxy,Sxz=(px_e-qx*tmp), (py_e-qy*tmp), (pz_e-qz*tmp)
                    tmp=np.sqrt(Sxx**2+Sxy**2+Sxz**2)
                    Sxx,Sxy,Sxz=Sxx/tmp,Sxy/tmp,Sxz/tmp
                    tmp=np.sqrt(q2)
                    Szx,Szy,Szz=qx/tmp,qy/tmp,qz/tmp
                    Syx,Syy,Syz=(Szy*Sxz-Szz*Sxy),(Szz*Sxx-Szx*Sxz),(Szx*Sxy-Szy*Sxx)
                    #print(Sxx**2+Sxy**2+Sxz**2, Szx**2+Szy**2+Szz**2, Syx**2+Syy**2+Syz**2, Sxx*Szx+Sxy*Szy+Sxz*Szz, Syx*Szx+Syy*Szy+Syz*Szz, Sxx*Syx+Sxy*Syy+Sxz*Syz)
                    
                    phih=np.arctan2(px_pi*Syx+py_pi*Syy+pz_pi*Syz, px_pi*Sxx+py_pi*Sxy+pz_pi*Sxz)
                    
                    pt2=px_pi**2+py_pi**2+pz_pi**2-(qx*px_pi+qy*py_pi+qz*pz_pi)**2/q2

                    t=-Q2+.1396**2-2*(Ebeam-E_e)*E_pi+2*(qx*px_pi+qy*py_pi+qz*pz_pi)
                    
                    print(f"{x:.4f},{Q2:.4f},{W:.4f},{np.sqrt(miss_mass2):.4f},{phih:.4f},{pt2:.4f},{t:.4f},{secondary_pips},{secondary_pims},{secondary_pizs},{secondary_esum:.5f},{accepted}", file=outf)
            electron_kin, pion_kin, secondary_pips,secondary_pims,secondary_pizs,secondary_esum,accepted=None, None, 0,0,0,0,0
            
