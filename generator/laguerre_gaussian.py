import numpy as np
from scipy.special import hermite, genlaguerre
from scipy.constants import c, epsilon_0
from scipy.interpolate import RegularGridInterpolator
import matplotlib.pyplot as plt
import math
import time
import laserbeamsize as lbs

"FUNCTIONS FOR LAGUERRE-GAUSSIAN BEAMS"
def LGAnalytic(x,y,z,w0,p,m,wavelength):
    """
    Evaluates a complex Laguerre-Gauss according to pg647 eqn64 of DOI: https://doi.org/10.1017/S0263034600003050
    
    Parameters
    ----------
    x, y: ndarrays of floats (meters)
        Define points on the transverse plane upon which to evaluate the field. These 
        arrays need to all have the same shape, 1d.
    
    z: float (meters)
        Longitudinal (along the propagation axis) position at which to evaluate the 
        field. 
        
    w0: floats (meters)
        The size of the mode waist at focus
        
    p, m: ints 
        The radial and azimuthal mode numbers respectively
        
    wavelength: float (meters)
        The wavelength of the laser
        
    Returns
    -------
    LG: ndarray of complex floats
        The field of the evaluated Laguerre Gauss mode
        
    """
    
    assert len(x.shape)==1
    assert len(y.shape)==1

    X,Y = np.meshgrid(x, y, indexing='ij')
    
    k0 = 2*np.pi/wavelength
    
    # Calculate Rayleigh Length
    Zr  = np.pi*w0**2/wavelength
    
    # Calculate Size at Location Z
    w0Z = w0*np.sqrt(1 + (z/Zr)**2)
       
    # Calculate Multiplicative Factors 
    A = np.sqrt(2.0 * math.factorial(p) / (np.pi * math.factorial(m + p))) / w0Z

    # Calculate the Phase contributions from propagation
    phiZ = (2.0 * p + m + 1) * np.arctan2(z,Zr)

    # Calculate the LG in each plane
    LGn = A * (np.sqrt(2.0) * np.sqrt(X**2 + Y**2) / w0Z) ** (m) * genlaguerre(p, m)(2.0 * (X**2 + Y**2) / w0Z**2) \
             * np.exp(-(X**2+Y**2)/w0Z**2) * np.exp( -1j * k0 * (X**2+Y**2)/2/(z**2 + Zr**2)*z)
    
    # Put it altogether
    LG = LGn * np.exp(1j*phiZ) * np.exp(-1j*m*np.arctan2(Y,X))
    
    return LG

def getLGMode(x,y,z,field,w0,p,m,wavelength):
    """
    Determine, via projection, the complex amplitude of a single Laguerre Gauss mode in 
    a provided electric field
    
    Parameters
    ----------
    x, y: ndarrays of floats (meters)
        Points on the transverse plane upon which to field is evaluated. These 
        arrays need to all have the same shape although can be either 1d arrays or a 
        set of 2D arrays created with numpy.meshgrid
    
    z: float (meters)
        Longitudinal (along the propagation axis) position at which the field is evaluated.
        
    field: ndarray of complex floats 
        The electric field onto which the Hermite Gauss mode should be projected
        
    w0: floats (meters)
        The size of the mode at focus
        
    p, m: ints 
        The radial and azimuthal mode numbers
        
    wavelength: float (meters)
        The wavelength of the laser
        
    Returns
    -------
    coeff: complex float
        The complex amplitude of the selected Laguerre Gauss mode within the provided 
        electric field
    
    """
    
    dx = np.mean(np.diff(x))
    dy = np.mean(np.diff(y))
    
    lg = LGAnalytic(x,y,z,w0,p,m,wavelength)
    
    coeff = np.sum(field*np.conj(lg))*dx*dy
    
    return coeff
    
def decomposeLG(x,y,z,field,w0,pMax,mMax,wavelength):
    """
    Perform a modal decomposition of the provided electric field distribution into 
    a set of Laguerre Gauss modes
    
    Parameters
    ----------
    x, y: ndarrays of floats (meters)
        Points on the transverse plane upon which to field is evaluated. These 
        arrays need to all have the same shape although can be either 1d arrays or a 
        set of 2D arrays created with numpy.meshgrid
    
    z: float (meters)
        Longitudinal (along the propagation axis) position at which the field is evaluated.
        
    field: ndarray of complex floats 
        The electric field onto which the Hermite Gauss mode should be projected
        
    w0: floats (meters)
        The size of the mode at focus
        
    pMax,mMax: ints 
        The maximum order of the radial and azimuthal modes that will be used in the
        decomposition
        
    wavelength: float (meters)
        The wavelength of the laser
        
    Returns
    -------
    cxy: structure of complex float
        The complex amplitude of the each of the Laguerre Gauss modes within the
        decomposition. Each mode amplitude is indexed by a tuple (p,m) in which
        p and m represent the order of the radial and azimuthal modes.
    
    """
    cxy = {}
    for i in range(pMax):
        for j in range(mMax):
            cxy[(i,j)] = getLGMode(x,y,z,field,w0,i,j,wavelength)
        
    return cxy

def reconstructLG(x,y,z,w0,cxy,wavelength):
    """
    Reconstruct an electric field distribution from a set of complex LG mode amplitudes
    
    
    Parameters
    ----------
    x, y: ndarrays of floats (meters)
        Define points on the transverse plane upon which to evaluate the field. These 
        arrays need to all have the same shape although can be either 1d arrays or a 
        set of 2D arrays created with numpy.meshgrid
    
    z: float (meters)
        Longitudinal (along the propagation axis) position at which to evaluate the 
        field. 
        
    w0: floats (meters)
        The size of the mode waist at focus
        
    p, m: ints 
        The radial and azimuthal mode numbers respectively
        
    cxy: structure of complex float
        The complex amplitude of the each of the Laguerre Gauss modes within the
        decomposition. Each mode amplitude is indexed by a tuple (p,m) in which
        p and m represent the radial and azimuthal order of the mode.
        
    wavelength: float (meters)
        The wavelength of the laser
        
    Returns
    -------
    field: ndarray of complex floats 
        The reconstructed electric field 
    
    """

    field = 1j*np.zeros((len(y),len(x)))
    
    for nxy in list(cxy):
        field += cxy[nxy]*LGAnalytic(x,y,z,w0,nxy[0],nxy[1],wavelength)
        
    return field