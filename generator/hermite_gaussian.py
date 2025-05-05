import numpy as np
from scipy.special import hermite, genlaguerre
from scipy.constants import c, epsilon_0
from scipy.interpolate import RegularGridInterpolator
import matplotlib.pyplot as plt
import math
import time
import laserbeamsize as lbs

"FUNCTIONS FOR HERMITE-GAUSSIAN BEAMS"
def HGAnalytic(x,y,z,x0,y0,wx,wy,nx,ny,wavelength):
    """
    Evaluates a complex Hermite-Gauss according to eqn3 of DOI: 10.1364/JOSAB.489884
    Specifically this representation allows for the computation of the mode with distinct
    mode widths in x and y while also allows the mode to be calculated at an arbitrary
    location along the propagation axis z
    
    Parameters
    ----------
    x, y: ndarrays of floats (meters)
        Define points on the transverse plane upon which to evaluate the field. These 
        arrays need to all have the same shape, 1d.
    
    z: float (meters)
        Longitudinal (along the propagation axis) position at which to evaluate the 
        field. 
        
    x0,y0: floats (meters)
        The center position of the mode in the x and y plane
        
    wx,wy: floats (meters)
        The size of the mode along the x and y axes at focus
        
    nx,ny: ints 
        The order of the mode along the x and y axes
        
    wavelength: float (meters)
        The wavelength of the laser
        
    Returns
    -------
    HG: ndarray of complex floats
        The field of the evaluated Hermite Gauss mode
        
    """
    
    assert len(x.shape)==1
    assert len(y.shape)==1
    
    k0 = 2*np.pi/wavelength
    
    # Calculate Rayleigh Lengths
    Zx  = np.pi*wx**2/wavelength
    Zy  = np.pi*wy**2/wavelength
    
    # Calculate Size at Location Z
    wxZ = wx*np.sqrt(1 + (z/Zx)**2)
    wyZ = wy*np.sqrt(1 + (z/Zy)**2)
    
    # Calculate Multiplicative Factors
    Anx = 1 / np.sqrt( wxZ * 2**(nx-1/2) * math.factorial(nx) * np.sqrt(np.pi) )
    Any = 1 / np.sqrt( wyZ * 2**(ny-1/2) * math.factorial(ny) * np.sqrt(np.pi) )
    
    # Calculate the Phase contributions from propagation
    phiXz = (nx + 1/2)*np.arctan2(z,Zx)
    phiYz = (ny + 1/2)*np.arctan2(z,Zy)
    phiZ = phiXz + phiYz
    
    # Calculate the HG in each plane
    hgnx = Anx * hermite(nx)( np.sqrt(2) * (x-x0)/wxZ ) * np.exp(-(x-x0)**2/wxZ**2) * np.exp( -1j * k0 * (x-x0)**2/2/(z**2 + Zx**2)*z)
    hgny = Any * hermite(ny)( np.sqrt(2) * (y-y0)/wyZ ) * np.exp(-(y-y0)**2/wyZ**2) * np.exp( -1j * k0 * (y-y0)**2/2/(z**2 + Zy**2)*z)
    
    HGnx,HGny = np.meshgrid(hgnx,hgny)
    # Put it altogether
    HG = HGnx * HGny * np.exp(1j*phiZ)
    
    return HG

def getHGMode(x,y,z,field,x0,y0,wx,wy,nx,ny,wavelength):
    """
    Determine, via projection, the complex amplitude of a single Hermite Gauss mode in 
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
        
    x0,y0: floats (meters)
        The center position of the mode in the x and y plane
        
    wx,wy: floats (meters)
        The size of the mode along the x and y axes at focus
        
    nx,ny: ints 
        The order of the mode along the x and y axes
        
    wavelength: float (meters)
        The wavelength of the laser
        
    Returns
    -------
    coeff: complex float
        The complex amplitude of the selected Hermite Gauss mode within the provided 
        electric field
    
    """
    
    dx = np.mean(np.diff(x))
    dy = np.mean(np.diff(y))
    
    hg = HGAnalytic(x,y,z,x0,y0,wx,wy,nx,ny,wavelength)
    
    coeff = np.sum(field*np.conj(hg))*dx*dy
    
    return coeff
    
def decomposeHG(x,y,z,field,x0,y0,wx,wy,nxMax,nyMax,wavelength,skipAsymmetricModes=False):
    """
    Perform a modal decomposition of the provided electric field distribution into 
    a set of Hermite Gauss modes
    
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
        
    x0,y0: floats (meters)
        The center position of the mode in the x and y plane
        
    wx,wy: floats (meters)
        The size of the mode along the x and y axes at focus
        
    nxMax,nyMax: ints 
        The maximum order of the mode along the x and y axes that will be used in the
        decomposition
        
    wavelength: float (meters)
        The wavelength of the laser
        
    Returns
    -------
    cxy: structure of complex float
        The complex amplitude of the each of the Hermite Gauss modes within the
        decomposition. Each mode amplitude is indexed by a tuple (nx,ny) in which
        nx and ny represent the order of the mode along each axis.
    
    """
    cxy = {}
    for i in range(nxMax):
        for j in range(nyMax):
            if (i != j) and (skipAsymmetricModes):
                cxy[(i,j)] = 0
                continue
            cxy[(i,j)] = getHGMode(x,y,z,field,x0,y0,wx,wy,i,j,wavelength)
        
    return cxy

def reconstructHG(x,y,z,x0,y0,wx,wy,cxy,wavelength,skipAsymmetricModes=False):
    """
    Reconstruct an electric field distribution from a set of complex HG mode amplitudes
    
    
    Parameters
    ----------
    x, y: ndarrays of floats (meters)
        Define points on the transverse plane upon which to evaluate the field. These 
        arrays need to all have the same shape although can be either 1d arrays or a 
        set of 2D arrays created with numpy.meshgrid
    
    z: float (meters)
        Longitudinal (along the propagation axis) position at which to evaluate the 
        field. 
        
    x0,y0: floats (meters)
        The center position of the mode in the x and y plane
        
    wx,wy: floats (meters)
        The size of the mode along the x and y axes at focus
        
    cxy: structure of complex float
        The complex amplitude of the each of the Hermite Gauss modes within the
        decomposition. Each mode amplitude is indexed by a tuple (nx,ny) in which
        nx and ny represent the order of the mode along each axis.
        
    wavelength: float (meters)
        The wavelength of the laser

    skipAsymmetricModes : bool
        If true, the only modes investigated are where nx = ny
        
    Returns
    -------
    field: ndarray of complex floats 
        The reconstructed electric field 
    
    """

    field = 1j*np.zeros((len(y),len(x)))
    
    for nxy in list(cxy):
        if (nxy[0] != nxy[1]) and (skipAsymmetricModes):
            continue
        field += cxy[nxy]*HGAnalytic(x,y,z,x0,y0,wx,wy,nxy[0],nxy[1],wavelength)
        
    return field