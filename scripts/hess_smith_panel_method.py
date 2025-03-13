import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter("ignore", category=DeprecationWarning)

#################################################################################
## Generates a surface panelization of any NACA 4-series airfoil (with a
## bunching parameter for greater resolution at LE and TE)
#################################################################################

def naca_4series_generator(naca4, npanel):
    # ---------------------------------------------------------------------------
    # STEP 2.1: naca airfoil digits
    # ---------------------------------------------------------------------------
    x = np.zeros(npanel + 1)
    y = np.zeros(npanel + 1)
    n1 = int(naca4[3])
    n2 = int(naca4[2])
    n3 = int(naca4[1])
    n4 = int(naca4[0])

    # ---------------------------------------------------------------------------
    # STEP 2.2: maximum camber, thickness, and location of maximum camber
    # ---------------------------------------------------------------------------
    m = n4 / 100
    p = n3 / 10
    t = (n2 * 10 + n1) / 100

    # ---------------------------------------------------------------------------
    # STEP 2.3: compute thickness and camber distributions
    # ---------------------------------------------------------------------------
    if npanel % 2 != 0:
        raise ValueError("Please choose an even number of panels!")
    nside = int(npanel / 2 + 1)

    # ---------------------------------------------------------------------------
    # STEP 2.4: bunching parameter for higher resolution near leading edge and
    #           trailing edge
    # ---------------------------------------------------------------------------

    an  = 1.5
    anp = an + 1
    xx  = np.zeros(nside)
    yt  = np.zeros(nside)
    yc  = np.zeros(nside)

    # ---------------------------------------------------------------------------
    # STEP 2.4: determine camberline
    # ---------------------------------------------------------------------------
    for i in range(nside):
        frac = i / (nside - 1)
        xx[i] = 1 - anp * frac * (1 - frac) ** an - (1 - frac) ** anp
        yt[i] = (0.29690 * np.sqrt(xx[i]) - 0.12600 * xx[i]
                 - 0.35160 * xx[i] ** 2 + 0.28430 * xx[i] ** 3
                 - 0.10150 * xx[i] ** 4) * t / 0.2
        if xx[i] < p:
            yc[i] = m / p ** 2 * (2 * p * xx[i] - xx[i] ** 2)
        else:
            yc[i] = m / (1 - p) ** 2 * (1 - 2 * p + 2 * p * xx[i] - xx[i] ** 2)

    # ---------------------------------------------------------------------------
    # STEP 2.5: determine airfoil shape = camber + thickness
    # ---------------------------------------------------------------------------
    for i in range(nside):
        x[nside + i - 1] = xx[i]
        x[nside - i - 1] = xx[i]
        y[nside + i - 1] = yc[i] + yt[i]
        y[nside - i - 1] = yc[i] - yt[i]

    return x, y


#################################################################################
## Returns the midpoints, lengths, and orientation (angles) of each panel
#################################################################################

def panel_geometry(x, y, npanel):
    # ---------------------------------------------------------------------------
    # STEP 3.1 allocate all necessary arrays
    # ---------------------------------------------------------------------------
    l           = np.zeros(npanel)
    sin_theta   = np.zeros(npanel)
    cos_theta   = np.zeros(npanel)
    xbar        = np.zeros(npanel)
    ybar        = np.zeros(npanel)

    # ---------------------------------------------------------------------------
    # STEP 3.2 compute various geometrical quantities
    # ---------------------------------------------------------------------------
    # for all panels
    for i in range(npanel):

        # compute length of panel
        l[i] = np.linalg.norm(np.array([x[i+1] - x[i], y[i+1] - y[i]]))
        #l[i] = np.sqrt((x[i+1] - x[i])**2 + (y[i+1] - y[i])**2)

        # compute sin_theta
        sin_theta[i] = (y[i + 1] - y[i]) / l[i]

        # compute  cos_theta
        cos_theta[i] = (x[i + 1] - x[i]) / l[i]

        # compute xbar
        xbar[i] = (x[i + 1] + x[i]) / 2

        # compute ybar
        ybar[i] = (y[i + 1] + y[i]) / 2

    return l, sin_theta, cos_theta, xbar, ybar


#################################################################################
## Computes the influence coefficient matrix 'A' for flow tangency boundary
## condition and Kutta condition
#################################################################################

def infl_coeff(x, y, xbar, ybar, st, ct, npanel):

    # ---------------------------------------------------------------------------
    # STEP 4.1 precompute common terms
    # ---------------------------------------------------------------------------

    A = np.zeros((npanel + 1, npanel + 1))

    sin_i_j = np.outer(st, ct) - np.outer(ct, st)
    cos_i_j = np.outer(ct, ct) + np.outer(st, st)

    # Initialize all variables
    
    r_ij = np.zeros((npanel, npanel, 2))
    r_ij_1 = np.zeros((npanel, npanel, 2))
    beta_ij = np.zeros((npanel, npanel))
    u_s_star_ij = np.zeros((npanel, npanel))
    v_s_star_ij = np.zeros((npanel, npanel))

    # ---------------------------------------------------------------------------
    # Step 4.2 Define the elements of the matrix of A aero influence coefficients
    # ---------------------------------------------------------------------------
    # ith panel (major loop)
    for i in range(npanel):

        # find contribution of the jth panel (inner loop)
        for j in range(npanel):

            # compute r_ij
            r_ij[i, j] = [x[j] - xbar[i], y[j] - ybar[i]]

            # compute r_ij+1
            r_ij_1[i, j] = [x[j + 1] - xbar[i], y[j + 1] - ybar[i]]

            norm1 = np.linalg.norm(r_ij[i, j])
            norm2 = np.linalg.norm(r_ij_1[i, j])

            # compute beta_ij
            if i == j:
              beta_ij[i, j] = np.pi
            else:
                dot_product = np.dot(r_ij[i, j], r_ij_1[i, j])
                cross_product = np.cross(r_ij[i, j], r_ij_1[i, j])
                beta_ij[i, j] = np.arctan2(cross_product, dot_product)

            # compute u_s_star_i_j
            u_s_star_ij[i, j] = - np.log(norm2 / norm1) / (2 * np.pi)

            # compute v_s_star_i_j
            v_s_star_ij[i, j] = beta_ij[i, j] / (2 * np.pi)

            # compute all elements of A, the influence coefficient matrix
            A[i, j] = sin_i_j[i, j] * -u_s_star_ij[i, j] + cos_i_j[i, j] * v_s_star_ij[i, j]

            if i == 0 or i == npanel - 1:
                A[npanel, j] += (sin_i_j[i, j] * beta_ij[i, j] - cos_i_j[i, j] * np.log(norm2 / norm1)) / (2 * np.pi)
                A[npanel, npanel] += A[i, j]

            A[i, npanel] += (cos_i_j[i, j] * np.log(norm2 / norm1) - sin_i_j[i, j] * beta_ij[i, j]) / (2 * np.pi)


    # check to see if matrix is singular
    if np.linalg.det(A) == 0:
        raise ValueError("Matrix is singular")

    return A


#################################################################################
## Computes the surface velocities from source/vortex distribution at each panel  
#################################################################################

def velocity_distribution(lambda_gamma, x, y, xbar, ybar, sin_theta, cos_theta, alpha, npanel):

    # ---------------------------------------------------------------------------
    # STEP 4.1 precompute common terms
    # ---------------------------------------------------------------------------

    # Need tangential velocity at each panel
    vt = np.zeros(npanel)

    # Compute cosine and sine for i-j
    sin_i_j = np.outer(sin_theta, cos_theta) - np.outer(cos_theta, sin_theta)
    cos_i_j = np.outer(cos_theta, cos_theta) + np.outer(sin_theta, sin_theta)

    # ---------------------------------------------------------------------------
    # STEP 7.2 allocate all necessary arrays
    # ---------------------------------------------------------------------------

    # Create empty arrays to be appended through iteration
    r_ij = np.zeros((npanel, npanel, 2))
    r_ij_1 = np.zeros((npanel, npanel, 2))
    beta_ij = np.zeros((npanel, npanel))

    # ---------------------------------------------------------------------------
    # Step 7.3 flow tangency boundary condition - source distribution
    # ---------------------------------------------------------------------------
    # ith panel (major loop)
    for i in range(npanel):

        # Initialize sums
        summation_1 = 0
        summation_2 = 0

        # find contribution of the jth panel (inner loop)
        for j in range(npanel):

            # For r_ij, r_ij+1, beta_ij, same formula as infl_coeff

            # compute r_ij
            # Use equation from lecture
            r_ij[i, j] = [x[j] - xbar[i], y[j] - ybar[i]]

            # compute r_ij+1
            r_ij_1[i, j] = [x[j + 1] - xbar[i], y[j + 1] - ybar[i]]

            norm1 = np.linalg.norm(r_ij[i, j])
            norm2 = np.linalg.norm(r_ij_1[i, j])

            # compute beta_ij

            if i == j:
              beta_ij[i, j] = np.pi
            else:
                dot_product = np.dot(r_ij[i, j], r_ij_1[i, j])
                cross_product = np.cross(r_ij[i, j], r_ij_1[i, j])
                beta_ij[i, j] = np.arctan2(cross_product, dot_product)

            # compute vt

            # from class notes:
            summation_1 += (lambda_gamma[j] / (2 * np.pi)) * (sin_i_j[i, j] * beta_ij[i, j] - cos_i_j[i, j] * np.log(norm2 / norm1))
            summation_2 += (sin_i_j[i, j] * np.log(norm2 / norm1) + cos_i_j[i, j] * beta_ij[i, j])

        cos_theta_i_alpha = cos_theta[i] * np.cos(alpha) + sin_theta[i] * np.sin(alpha)
        # Assume V_inf = 0
        vt[i] = cos_theta_i_alpha + summation_1 + (lambda_gamma[npanel] / (2 * np.pi)) * summation_2


    return vt


#################################################################################
## Computes aerodynamic coefficients Cl, Cd, Cm
#################################################################################

def aero_coeff(x, y, cp, al, npanel):

    # ---------------------------------------------------------------------------
    # STEP 3.1 allocate all necessary arrays
    # ---------------------------------------------------------------------------
    Cn = 0
    Ca = 0
    Cm = 0

    for i in range(npanel):
        # compute dx
        dx = x[i+1] - x[i]

        # compute dy
        dy = y[i+1] - y[i]

        # compute xa at quarter chord
        xa = 0.5 * (x[i+1] + x[i]) - 0.25

        # compute ya
        ya = 0.5 * (y[i+1] + y[i])

        # compute dCn
        dCn = -cp[i] * dx

        # compute dCa
        dCa = cp[i] * dy

        # recursively compute Cn, Ca and Cm
        Cn += dCn
        Ca += dCa
        Cm += - (dCn * xa) + (dCa * ya)

    # compute Cl
    Cl  = Cn * np.cos(al) - Ca * np.sin(al)

    # compute Cd
    Cd  = Cn * np.sin(al) + Ca * np.cos(al)

    return Cl, Cd, Cm


#################################################################################
## Computes the surface surface pressure coefficient, force coefficients using 
## all previously defined functions
#################################################################################

def hess_smith(x,y,alpha):
    # ---------------------------------------------------------------------------
    # STEP 1: allocate all necessary arrays
    # ---------------------------------------------------------------------------
    npanel       = len(x) - 1
    cp           = np.zeros(npanel + 1)
    l            = np.zeros(npanel)
    sin_theta    = np.zeros(npanel)
    cos_theta    = np.zeros(npanel)
    xbar         = np.zeros(npanel)
    ybar         = np.zeros(npanel)

    # ---------------------------------------------------------------------------
    # STEP 3: generate panel geometry data for later use
    # ---------------------------------------------------------------------------
    [l, sin_theta, cos_theta, xbar, ybar] = panel_geometry(x, y, npanel)


    # ---------------------------------------------------------------------------
    # STEP 4: compute matrix of aerodynamic influence coefficients
    # ---------------------------------------------------------------------------
    A = np.zeros((npanel + 1, npanel + 1))
    A = infl_coeff(x, y, xbar, ybar, sin_theta, cos_theta, npanel)


    # ---------------------------------------------------------------------------
    # STEP 5: compute right hand side vector for the specified angle of attack
    # ---------------------------------------------------------------------------
    b = np.zeros(npanel + 1)
    al = alpha * np.pi / 180

    for i in range(npanel):
        b[i] = sin_theta[i] * np.cos(al) - np.sin(al) * cos_theta[i]
    b[npanel] = -(cos_theta[0] * np.cos(al) + sin_theta[0] * np.sin(al)) - (cos_theta[npanel-1] * np.cos(al) + sin_theta[npanel-1] * np.sin(al))


    # ---------------------------------------------------------------------------
    # STEP 6: solve matrix system for vector of lambda_i and gamma
    # ---------------------------------------------------------------------------
    lambda_gamma = np.linalg.inv(A) @ b


    # ---------------------------------------------------------------------------
    # STEP 7: compute the tangential velocity distribution at the midpoint of panels
    # ---------------------------------------------------------------------------
    vt = velocity_distribution(lambda_gamma, x, y, xbar, ybar, sin_theta, cos_theta, al, npanel)


    # ---------------------------------------------------------------------------
    # STEP 8: compute pressure coefficient
    # ---------------------------------------------------------------------------
    cp = 1 - vt ** 2

    # ---------------------------------------------------------------------------
    # STEP 9: compute force coefficients
    # ---------------------------------------------------------------------------
    cl, cd, cm = aero_coeff(x, y, cp, al, npanel)

    return cl, cd, cm,cp, xbar, ybar, vt, cos_theta, sin_theta


#################################################################################
## EXAMPLE IMPLEMENTATION: Function returns cl, cd, cm, cp distribution.
#################################################################################

def pm(alpha, naca_list, npanel):
    # user input desired AoA
    alpha = alpha
    # user input desired NACA airfoil (type=list)
    naca_4  = naca_list
    # user change number of panels based on desired accuracy, computational cost
    npanel = npanel

    # ---------------------------------------------------------------------------
    # generate airfoil coordinates
    # ---------------------------------------------------------------------------
    x, y = naca_4series_generator(naca_4, npanel)

    # ---------------------------------------------------------------------------
    # run hess smith panel code
    # ---------------------------------------------------------------------------
    cl, cd, cm, cp, xbar, ybar, vt, ct, st = hess_smith(x,y,alpha)
    
    return cl, cd, cm, xbar, cp


# -------------------------------------------------------------------------------
#  NACA 2410 airfoil, 250 panels, AoA = 4 deg.
# -------------------------------------------------------------------------------
cl, cd, cm, xbar, cp = pm(4, [2,4,1,0], 250)

fig = plt.figure(figsize=(12, 12), tight_layout=True)

plt.plot(xbar, cp, 'b')
plt.xlabel('Chord Position')
plt.ylabel('$c_p$')
plt.title("Presure Coefficient Plot")
plt.ylim(1.25, -2.5)
plt.grid(True)
plt.show()

print('Cl: ', cl)
print('Cd: ', cd)
print('Cm: ', cm)