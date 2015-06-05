__author__ = 'Jayson Stemmler'
__created__ = "6/5/15 7:52 AM"

"""
    EQUATIONS
"""

def qsatw(t, p):
    """saturated vapor pressure with respect to water.
    use functions given in Unified Model Documentation No. 29
    Calculation of saturated specific humidity and large scale cloud.
    RNB Smith et al. 1990
    output kg/kg

    t is temperature in K
    p is pressure in Pa
    qsw is the saturated specific humidity wrt water in Pa
    """

    t0=273.16
    t = array(t); p = array(p)
    log10esw=10.79574 * (1-t0/t) - 5.028 * log10(t/t0) + \
             1.50475e-4 * (1-10**(-8.2369*(t/t0-1))) + 0.42873e-3 * \
             (10**(4.76955*(1-t0/t))-1) + 2.78614

    esw=10**(log10esw)
    qsw=0.62198*esw/(p-esw)

    try:
        qsw[isinf(qsw)] = 0.
    except TypeError:
        if isinf(qsw):
            qsw = 0.

    return qsw

def adlwcgm2(t, p):

    """ takes in temperature in k
    pressure in hPa
    """

    qs = qsatw(t, 100.*p)

    rho=100.0*p/(287.04*t)

    g=9.81
    R=287.04
    L=2.5e6
    cp=1004.67

    eps=0.622

    #;gam in g/kg per metre

    #;gam in g/m3/m


    dqldz=(g*qs/(R*t))*(L*eps/(cp*t)-1.0)/(1+eps*L*L*qs/(R*t*t*cp))
    dqldz=rho*dqldz*1000.

    #;dqldz in g/m3 per m

    return dqldz

def gam_ad(t, p=900.):

    return 1.e-3*adlwcgm2(t, p)

def get_nd_from_lwp_re(gam_ad, frac_ad, lwp, re):

    """Return the droplet number concentration from LWP and Re

    :param: re
    :units: meters (um * 1e-6)

    :param: lwp
    :units: kg per m**2 (g/m2 * 1e-3)

    :param: gam_ad
    :units: order 2e-6

    :param: frac_ad
    :units: unitless, ~1.0

    """

    # check that LWP and re are same length
    if type(lwp) != type(re):
        raise Exception('LWP and re are not the same type')

    if type(lwp) != 'numpy.ndarray':
        lwp = array(lwp)
    if type(re) != 'numpy.ndarray':
        re = array(re)

    if lwp.shape != re.shape:
        raise Exception('LWP and re not the same length')

    B = (3.*sqrt(2.) / (4.*pi*1000.))**(1./3.)
    k_ad = (frac_ad * gam_ad)**(1./6.)

    k_martin = array(0.865-exp(-0.30*re*1.e6))

    if not len(k_martin.shape):
        if isinf(k_martin): k_martin = 0.8
        if re < 3.e-6: k_martin = 0.45
    else:
        k_martin[isinf(k_martin)] = 0.8
        k_martin[re < 3.e-6] = 0.45

    nd = (B**3.) * ((k_ad / re)**3.) * sqrt(lwp)/k_martin

    if len(lwp.shape)==0:
        if (lwp==0) | (re==0):
            return None
    elif len(lwp.shape) > 0:
        nd[(lwp==0) | (re==0)] = None
        return nd

    return nd