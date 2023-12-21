import h5py
import numpy as np
from math import *
import uuid


from PyQt5.QtWidgets import QFrame,QMainWindow, QApplication, QComboBox, QPushButton,QFileDialog,QCheckBox, QTableWidget, QLabel,QLineEdit,QComboBox,QTableWidget,QTextEdit,QTableWidgetItem,QPlainTextEdit,QTextBrowser
from PyQt5 import uic
from sys import argv as argv





#
class UI_SedCAP(QFrame):
    def __init__(self):
        super(UI_SedCAP,self).__init__()

        #load UI
        uic.loadUi("UI_Files/Capacity_only.ui",self)

        

        #define our widgets 



                
        #self.test.textChanged.connect(onChange)
        self.comp_lab = self.findChild(QLabel,"label_comp")
        self.comp_lab2 = self.findChild(QLabel,"label_comp_2")
        self.un_lab1 = self.findChild(QLabel,"label_unit_1")
        self.un_lab2 = self.findChild(QLabel,"label_unit_2")
        self.un_lab3 = self.findChild(QLabel,"label_unit_3")
        self.capacity = self.findChild(QComboBox,"cap_transport")
        self.units = self.findChild(QComboBox,"unit_box")
        self.shearbox = self.findChild(QComboBox,"shear_box")
        self.depthbox = self.findChild(QComboBox,"depth_box")
        self.velbox = self.findChild(QComboBox,"vel_box")
        

        self.button = self.findChild(QPushButton,"SRH2D_Button")
        self.buttoncap = self.findChild(QPushButton,"computecap")
        self.D16_nat1 = self.findChild(QLineEdit,"D16_nat")
        self.D50_nat1 = self.findChild(QLineEdit,"D50_nat")
        self.D84_nat1 = self.findChild(QLineEdit,"D84_nat")
        self.Fs_sand = self.findChild(QLineEdit,"Fs")
        self.filename = "dummy"
        #self.button2 = self.findChild(QPushButton,"fishbaff")
        #self.button3 = self.findChild(QPushButton,"grav_pier")
        #self.button4 = self.findChild(QPushButton,"stabchan")
        #self.button5 = self.findChild(QPushButton,"rational")

        def fpath():
            try:
                filepath = QFileDialog.getOpenFileName(self, "Select XMDF/h5 File","*.h5")
                self.filename = filepath[0]   
                self.comp_lab.setText(self.filename)  
                f = h5py.File(self.filename, "a")    

                print("Keys: %s" % f.keys())
                # get first object name/key; may or may NOT be a group
                dataset = list(f.keys())[0]

                datalist = list(f[dataset])
                print(datalist)

                self.shearbox.clear()
                self.depthbox.clear()
                self.velbox.clear()

                self.shearbox.addItem('Select')
                self.depthbox.addItem('Select')
                self.velbox.addItem('Select')

                for i in range(len(datalist)):
                    self.shearbox.addItem(datalist[i])
                    self.depthbox.addItem(datalist[i])
                    self.velbox.addItem(datalist[i])    

                try: 
                    btxt = 'B_Stress_lb_p_ft2'
                    vtxt = 'Vel_Mag_ft_p_s'
                    dtxt = 'Water_Depth_ft'

                    self.shearbox.setCurrentText(btxt)
                    self.velbox.setCurrentText(vtxt)
                    self.depthbox.setCurrentText(dtxt)
                except:
                    btxt = 'Select'
                    vtxt = 'Select'
                    dtxt = 'Select'

                    self.shearbox.setCurrentText(btxt)
                    self.velbox.setCurrentText(vtxt)
                    self.depthbox.setCurrentText(dtxt)   
            except:
                    comp = "Error: Select XMDF/h5 File"

                    self.comp_lab.setText(comp)
            


        def onChange1(text): ##Enables certain input for sand vs. gravel beds 
            if self.capacity.currentText() == 'Brownlie - Sand Only' or text == 'Brownlie - Sand Only':
                return self.D84_nat1.setEnabled(True), self.D16_nat1.setEnabled(True), self.Fs_sand.setEnabled(False)
            elif self.capacity.currentText() == 'MPM - Gravel Only' or text == 'MPM - Gravel Only':
                return self.D84_nat1.setEnabled(False), self.D16_nat1.setEnabled(False),self.Fs_sand.setEnabled(False)
            else:
                return self.D84_nat1.setEnabled(False), self.D16_nat1.setEnabled(False),self.Fs_sand.setEnabled(True)
            
        def onChange2(text):
            if self.units.currentText() == "in" or text == "in":
                txt = "in"
            else:
                txt = "mm"
            return self.un_lab1.setText(txt),self.un_lab2.setText(txt),self.un_lab3.setText(txt)
        

        
        self.capacity.currentTextChanged.connect(onChange1)
        self.units.currentTextChanged.connect(onChange2)
        


        self.button.clicked.connect(fpath)
        self.buttoncap.clicked.connect(self.compute)
        
        #self.setCentralWidget(self.button2)


       
        self.show()
        
    #def rati(self):
    #    self.ui = UIRational()









# def Qs(Rr,w,Sr): #bed load (cfs)
#     return qb(Rr,Sr)*w


    def compute(self):
        #rom pathlib import Path
        #filepath = str(QFileDialog.getExistingDirectory(self, "Select XMDF File"))
        #filepath = QFileDialog.setNameFilter(self,"hdf5 (*.h5)")

        #try:

            print(self.filename)

            #print(filename)

            print(self.capacity.currentText())


            #filename = "Q100_XMDF.h5"


            #data_name = "Brownlie_cfs_ft"

            if self.units.currentText() == "in":
                D84_nat = float(self.D84_nat1.text()) #in
                D50_nat = float(self.D50_nat1.text()) #in
                D16_nat = float(self.D16_nat1.text()) #in
            else: #Convert mm to in
                D84_nat = float(self.D84_nat1.text())/25.4 #in
                D50_nat = float(self.D50_nat1.text())/25.4 #in
                D16_nat = float(self.D16_nat1.text())/25.4 #in


            Fsand =float(self.Fs_sand.text())

            #D50_nat = 1 #in
            #D84_nat = 0.1 #in
            #D16_nat = 0.001 #in
            rho = 1.94
            g = 32.2
            Sg = 2.65
            nu = 1.217*10**-5

                ###MPM for D50 only####
            def MPM(tau,D,V): #bed load per unit width (cfs/ft)
                """MPM Bed Load Equation, cfs per Unit Width""" 

                # l = len(tau)
                

                # gs = np.array([-999.0]*l)



                # for i in range(l):

                #     if tau[i] > 0:
                #         u_star = sqrt(tau[i]/rho) 

                #         Rs = u_star*(D84_nat/12)/nu
                        
                #         if Rs <= 5:
                #             BCoeff = 5.5+2.5*log(Rs,exp(1))
                #         elif Rs <= 70:
                #             BCoeff = 0.297918+24.8666*log10(Rs)-22.9885*(log10(Rs)**2)+8.5199*(log10(Rs)**3)-1.10752*(log10(Rs)**4)
                #         else:
                #             BCoeff = 8.5


                #         if D[i] > 0:   

                #             fprime = (2.82843/(BCoeff-3.75+2.5*log(2*D[i]/(D84_nat/12),exp(1))))**2
                            
                            
                #             rkr = sqrt(fprime/8)*(V[i]/u_star)

                #             gs[i] = (((rkr**1.5)*tau[i]-(0.047*rho*g*(Sg-1)*D50_nat/12))/(0.25*(rho**(1/3))*(((Sg-1)/Sg)**(2/3))))**1.5  ##RAS MPM lb/sec
                        
                #out = gs

                tau_star = tau/(rho*g*(Sg-1)*D50_nat/12)  
                q_star = 3.97*((tau_star-0.0495)**1.5)    
                out = q_star*(D50_nat/12)*sqrt(g*(Sg-1)*D50_nat/12) #(cfs/ft)
                out = rho*g*Sg*out #lb/sec-ft

                


                for i in range(len(out)): 
                    if isnan(out[i])==True: 
                        out[i]=-999
                    elif out[i]==-999: 
                        out[i] = -999
                    else:
                        out[i] = out[i]*(86400/2000) #tons/day
                        #print(out[i])
                
                return out 

            def two(x):
                out = x 
                for i in range(len(x)):
                    if x[i] == -999.0:
                        out[i] = -999.9
                    else:
                        out[i] = 2*x[i]
                
                return out


            def Brown(tau,Rbb,Vmag):
                """Brownlie Sand Transport Equation, cfs/ft"""

                Sf = tau/(rho*g*Rbb)
                sigma = 0.5*((D84_nat/D50_nat)+(D50_nat/D16_nat))
                Fg = Vmag/sqrt(g*(D50_nat/12)*(Sg-1))
                Rg = sqrt(g*(D50_nat/12)**3)/nu
                Yg = ((sqrt(Sg-1)*Rg)**-0.6)
                t_star_o = 0.22*Yg+0.06*10**(-7.7*Yg)
                Fgo = (4.596*t_star_o**0.5293)/((Sf**0.1405)*sigma**0.1606)
                Cin = 9022*((Fg-Fgo)**1.978)*(Sf**0.6601)*(Rbb/(D50_nat/12))**-0.3301  #concentration ppm
                out = (rho*g*Vmag*Rbb*Cin/100000)*(86400/2000) #convert to tons/day-ft
                
                for i in range(len(out)):
                    if isnan(out[i])==True: out[i]=-999


                return  out
            

            def Wilk_Crowe(tau,fS):
                """Wilcock-Crowe 2003 Surface Based transport Model"""
                print('here')


                d = D50_nat # grain size of interest 
                dsm = D50_nat #median grain size 
                tau_star = tau/(rho*g*(Sg-1)*D50_nat/12) 


                
                trm_star = 0.021+0.015*exp(-20*fS)
                b = 0.67/(1+exp(1.5-d/dsm))
                tri_star = trm_star*(d/dsm)**b


                #print(b, tri_star)
                u_star = np.array([-999.0]*len(tau))
                W_star = np.array([-999.0]*len(tau))
                qb = np.array([-999.0]*len(tau))
                out = np.array([-999.0]*len(tau))
                

                for i in range(len(u_star)):
                    try:
                        u_star[i] = sqrt(tau[i]/rho)
                        
                        #Transport Function 
                        if tau_star[i]/tri_star < 1.35:
                            W_star[i] = 0.002*(tau_star[i]/tri_star)**7.5  
                        else:
                            W_star[i]= 14*(1+0.894/sqrt(tau_star[i]/tri_star)**4.5)

                        qb[i]= (u_star[i]**3)*W_star[i]/((Sg-1)*g) #cfs/ft
                        out[i] = rho*g*Sg*qb[i]*(86400/2000) #Tons/day-ft
                        #print(out[i])
                    except:
                       out[i] = -999.0

               
                

                
               


                # for i in range(len(tau)): 
                #     if isnan(out[i])==True: 
                #         out[i]=-999
                #     elif out[i]==-999: 
                #         out[i] = -999
                #     else:
                #         out[i] = out[i]*(86400/2000) #tons/day

                #print(out)

                return out

            
            comp = str(self.filename)

            self.comp_lab.setText(comp)

            if self.capacity.currentText() == "Brownlie - Sand Only": 
                data_name = "Brownlie_tons_p_day_p_ft"
            elif self.capacity.currentText() == "MPM - Gravel Only": 
                data_name = "MPM_tons_p_day_p_ft"
            else:
                data_name = "Wilcock_tons_p_day_p_ft"


            f = h5py.File(self.filename, "a")    
    
            sheartext = self.shearbox.currentText()
            veltext = self.velbox.currentText()
            depthstext = self.depthbox.currentText()

            shear = np.array(f['Datasets/'+sheartext+'/Values'])
            depths = np.array(f['Datasets/'+depthstext+'/Values'])
            vels = np.array(f['Datasets/'+veltext+'/Values'])


            try:
                del f['Datasets/'+data_name]
            except:  
                print('create dataset')
            
            try:
                f.copy(f['Datasets/B_Stress_lb_p_ft2'],f['Datasets'],data_name)
            except:
                print('already here')

            #print(f['Datasets/'+data_name+'/Values'])

            var = [0]*len(shear)
            mins = [0]*len(shear)
            maxs = [0]*len(shear)


            for i in range(len(shear)):
                #var[i] = qb(shear[i])
                if self.capacity.currentText() == "Brownlie - Sand Only": 
                    var[i] = Brown(shear[i],depths[i],vels[i])
                elif self.capacity.currentText() == "MPM - Gravel Only": 
                    var[i] = MPM(shear[i],depths[i],vels[i])
                else:
                    var[i] = Wilk_Crowe(shear[i],Fsand)

                
                wx = [i for i in var[i] if i != -999.0] #Removes values that are equal to -999.0
                #print(wx)
                mins[i] = min(wx)
                maxs[i] = max(wx)
            #print(var)

            
            #del f['Datasets/MP2']

            
            del f['Datasets/'+data_name+'/Values']
            del f['Datasets/'+data_name+'/Maxs']
            del f['Datasets/'+data_name+'/Mins']
            
            print('not needed')

            f.create_dataset('Datasets/'+data_name+'/Values',data=var)
            f.create_dataset('Datasets/'+data_name+'/Maxs',data=maxs)
            f.create_dataset('Datasets/'+data_name+'/Mins',data=mins)

            comp = "Complete"
            out =  data_name

            self.comp_lab2.setText(out)

            self.comp_lab.setText(comp)
                
            #self.buttoncap.clicked.connect(computecap)

        # except:
        #     out = "Error: Select File or Appropriate Variables"
        #     self.comp_lab.setText(out)


  
app = QApplication(argv)
UIWindow = UI_SedCAP()
app.exec_()
