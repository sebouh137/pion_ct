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

with open(infile,"r") as inf, open(outfile,"w")	as outf:
    print("miss_mass,secondary_pips,secondary_pims,secondary_pizs,secondary_esum", file=outf)
    secondary_pips=0
    secondary_pims=0
    secondary_pizs=0
    secondary_esum=0
    electron_kin=None
    pion_kin=None
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
            if is_electron and P>acc.min_p_e[kin_i] and P<acc.max_p_e[kin_i] and th>acc.min_th_e[kin_i] and th<acc.max_th_e[kin_i]:
                electron_kin=E,px,py,pz,th
                #print("acc e")
            elif is_pion and split[2] == '211' and P>acc.min_p_pi[kin_i] and P<acc.max_p_pi[kin_i] and th>acc.min_th_pi[kin_i] and th<acc.max_th_pi[kin_i]:
                pion_kin=E,px,py,pz,th
                print("acc pi")
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

                    print(f"{np.sqrt(miss_mass2):.3f},{secondary_pips},{secondary_pims},{secondary_pizs},{secondary_esum:.5f}", file=outf)
            electron_kin, pion_kin, secondary_pips,secondary_pims,secondary_pizs,secondary_esum=None, None, 0,0,0,0
            
