from hermite_gaussian import *
from laguerre_gaussian import *
import os
import numpy as np

count = 0

x = np.linspace(-50e-6,50e-6,256)
y = np.linspace(-50e-6,50e-6,256)
z = 100e-6
x0 = 0
y0 = 0
wx = 10e-6
wy = 10e-6
wavelength = 800e-9


for n in range(0, 10):
    for m in range(0, 10):
        count += 1
        print(f'Rendering mode {count}/100')
        
        HGfield = HGAnalytic(x,y,z,x0,y0,wx,wy,m,n,wavelength)
        
        extent=(x.min()*1e6,x.max()*1e6,y.min()*1e6,y.max()*1e6)
        fig,ax = plt.subplots(1,2)
        ax[0].imshow(np.abs(HGfield)**2,aspect='equal',extent=extent,cmap='bone')
        ax[0].set_xlabel(u'x [\u03bc m]')
        ax[0].set_ylabel(u'y [\u03bc m]')
        ax[0].set_title('Intensity')
        ax[1].imshow(np.unwrap(np.angle(HGfield)/(2.*np.pi)),aspect='equal',cmap='bone')
        ax[1].set_title('Phase')
        plt.savefig('../img/HG/' + f'{m}_{n}.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        LGfield = LGAnalytic(x,y,z,wx,m,n,wavelength)
        
        extent=(x.min()*1e6,x.max()*1e6,y.min()*1e6,y.max()*1e6)
        fig,ax = plt.subplots(1,2)
        ax[0].imshow(np.abs(LGfield)**2,aspect='equal',extent=extent,cmap='bone')
        ax[0].set_xlabel(u'x [\u03bc m]')
        ax[0].set_ylabel(u'y [\u03bc m]')
        ax[0].set_title('Intensity')
        ax[1].imshow(np.unwrap(np.angle(LGfield)/(2.*np.pi)),aspect='equal',cmap='bone')
        ax[1].set_title('Phase')
        plt.savefig('../img/LG/' + f'{m}_{n}.png', dpi=300, bbox_inches='tight')
        plt.close()