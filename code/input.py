'''
input.py
NB time (dt,T) in ms, freq in Hz, but qon en qoff in MHz
always first 50 ms silent, then 50 ms noise, then rest
'''

import numpy as np
import random

class Input():
    '''Class containing the input parameters.
    '''
    def __init__(self): #, dt, T, fHandle, seed, input, ron, roff, qon, qoff, kernel, kerneltau, xseed, xfix):
        # For all
        self.dt = None
        self.T = None          
        self.fHandle = [None, None]
        self.seed = None
        self.input = None

        # For Markov models
        self.ron = None
        self.roff = None
        self.qon = []
        self.qoff = []
        self.kernel = None
        self.kerneltau = None
        self.xseed = None
        self.x = None
        self.xfix = None

        # Get dependend variables

    def get_tvec(self):
        '''docstring
        '''
        self.tvec = np.arange(self.dt, self.T+self.dt, self.dt)

    def get_length(self):
        ''' Generate variables dependent on the base variables
        '''  
        if self.tvec == []:
            print('Need a vector ''tvec'' to compute the length try running class.get_tvec first')
        else:
            self.length = len(self.tvec)

    def generate(self):
        ''' Generate input and x from fHandle
        '''
        if not self.fHandle:
            print('fHandle isn''t provided object')
        else:
            [self.input, self.x] = self.fHandle     

    def get_tau(self):
        ''' Description of function
        '''
        if self.ron == None or self.roff == None:
            print('Tau not defined, missing ron/roff')
        else:
            self.tau = 1/(self.ron+self.roff)
        
    def get_p0(self):
        '''Description
        '''
        if self.ron == None or self.roff == None:
            print('P0 not defined, missing ron/roff')
        else:
            self.p0 = self.ron/(self.ron+self.roff)   

    def get_theta(self):
        '''docstring
        '''
        if self.qon == [] or self.qoff == []:
            print('Theta not defined, missing qon/qoff')
        else:
            sum(self.qon-self.qoff)
    
    def get_w(self):
        '''docstring
        '''
        if self.qon == [] or self.qoff == []:
            print('Theta not defined, missing qon/qoff')
        else:
            self.w = np.log(self.qon/self.qoff)

    def get_all(self):
        '''docstring
        '''
        self.get_tvec()
        self.get_length()
        self.generate()
        self.get_tau()
        self.get_p0()
        self.get_theta()
        self.get_w()

    @staticmethod
    def create_qonqoff(mutheta, N, alphan, regime, qseed=None):
        '''Description returns [qon, qoff] with qon and qoff being a matrix
        '''
        random.seed(qseed)
        
        #TODO Check if this is best practice?
        qoff = np.array([[random.random() for e in range(1)] for e in range(N)])
        qon = np.array([[random.random() for e in range(1)] for e in range(N)])
        if N > 1:
            qoff = qoff/np.std(qoff)
            qon = qon/np.std(qon)
        qoff = qoff - np.mean(qoff)
        qon = qon - np.mean(qon)
        
        if regime == 1:
            # Coincedence regime
            qoff = (alphan*qoff+1)*mutheta/N
            qon = (alphan*qon+2)*mutheta/N
        else:
            #Push-pull regime
            qoff = (alphan*qoff+1)*mutheta/np.sqrt(N)
            qon = (alphan*qon+1+1/np.sqrt(N))*mutheta/np.sqrt(N)
        
        qoff[qoff<0] = abs(qoff[qoff<0])
        qon[qon<0] = abs(qon[qon<0])
        return [qon, qoff]
    
    @staticmethod
    def create_qonqoff_balanced(N,  meanq, stdq, qseed=None):
        random.seed(qseed)
        #TODO error if not correct arguments
        qoff = np.array([[random.random() for e in range(1)] for e in range(N)])
        qon = np.array([[random.random() for e in range(1)] for e in range(N)])
        
        if N > 1: 
            qoff = qoff/np.std(qoff)
            qon = qon/np.std(qon)

        qoff = stdq*(qoff-np.mean(qoff))+meanq
        qon = stdq*(qon-np.mean(qon))+meanq

        qoff[qoff<0] = abs(qoff[qoff<0])
        qon[qon<0] = abs(qon[qon<0])
        return [qon, qoff]

    @staticmethod
    def create_qonqoff_balanced_uniform(N, minq, maxq, qseed=None):
        '''docstring
        '''
        random.seed(qseed)

        random_array = np.array([[random.random() for e in range(1)] for e in range(N)])
        qoff = minq + np.multiply((maxq-minq), random_array)
        random_array = np.array([[random.random() for e in range(1)] for e in range(N)])
        qon = minq + np.multiply((maxq-minq), random_array)
        return [qon, qoff]

    def markov(self): # Not a static method as in the Matlab code
        '''Takes qon, qoff, ron and roff from class object and generates
           input and x if xfix empty, generates input with xfix otherwise
        '''
        random.seed(self.xseed)
        ni = len(self.qon)
        nt = self.length 
    
        w = np.log(self.qon/self.qoff) 
        
        # Generate x
        if self.xfix == None:
            #no need to generate p0 again
            xs = np.zeros(np.shape(self.tvec)) 

            #Initial value
            i = random.random()
            if i < self.p0:
                xs[0] = 1
            else:
                xs[0] = 0

            # make x
            for n in np.arange(1, self.length): #Changed 2 to 1 
                i = random.random()
                if xs[n-1] == 1: 
                    if i < self.roff*self.dt:
                        xs[n] = 0
                    else:
                        xs[n] = 1
                else: 
                    if i < self.ron*self.dt:
                        xs[n] = 1
                    else:
                        xs[n] = 0
        else:
            xs = self.xfix
        
        # Make spike trains (implicit)
        stsum = np.zeros((nt, 1))
        if self.kernel != None:
            if self.kernel == 'exponential':
                tfilt = np.arange(0, 5*self.kerneltau+self.dt, self.dt)
                kernelf = np.exp(-tfilt/self.kerneltau)
                kernelf = kernelf/(self.dt*sum(kernelf)) 
            elif self.kernel == 'delta':
                kernelf = 1./self.dt
        
        xon = np.where(xs==1)
        xoff = np.where(xs==0)
         
        random.seed(self.seed)

        # What does this for loop do?
        np.set_printoptions(threshold=np.inf)
        for k in range(ni):
            randon = np.array([[random.random() for e in range(np.shape(xon)[1])] for e in range(np.shape(xon)[0])])
            randoff = np.array([[random.random() for e in range(np.shape(xoff)[1])] for e in range(np.shape(xoff)[0])])
            sttemp = np.zeros((nt, 1))
            sttempon = np.zeros(np.shape(xon))
            sttempoff = np.zeros(np.shape(xoff))

            sttempon[randon < self.qon[k]*self.dt] = 1
            sttempoff[randoff < self.qoff[k]*self.dt] = 1.
         
            sttemp[xon] = np.transpose(sttempon)
            sttemp[xoff] = np.transpose(sttempoff)
            np.where(sttempon==1)

            stsum = stsum + w[k]*sttemp #w[k] is alright sttemp is all zeros 

        if self.kernel != None:
            stsum = np.convolve(stsum.flatten(), kernelf, mode='full')

        stsum = stsum[0:nt]
        ip = stsum 
        return [ip, xs]