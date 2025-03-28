import MagneticModel as magmod
import numpy as np
import csv
def compute_stability(a):
    Jg = -a.dot(np.array([[dFdx , dFdy], [dIdx, dIdy]]))
    ev,_=np.linalg.eig(Jg)
    evreal = np.real(ev)
    evimag = np.imag(ev)
    is_unstable = evreal[0] > 1e-12 or evreal[1] > 1e-12
    is_degenerate = abs(evreal[0]) < 1e-12 or abs(evreal[1]) < 1e-12
    has_rotation = evimag[0] != 0 or evimag[1] != 0

    if is_unstable:
        if has_rotation:
            return 0.75  # Spiral source (light green)
        else:
            return 1  # Unstable node (yellow)
    else:
        if is_degenerate:
            return 0.5  # Neutrally stable
        else:
            if has_rotation:
                return 0.25  # Spiral sink (medium green)
            else:
                return 0  # Stable node (dark green)

magmodel=magmod.MagneticModel(None)
goal_lat,goal_lon=17.7,56.3
dFdx, dFdy, dIdx, dIdy =  magmodel.estimate_gradients(17.7,56.3, ddeg=1e-3)
print(dFdx*dIdy-dFdy*dIdx)
print(dFdx, dFdy, dIdx, dIdy )
# Open CSV file in write mode
with open('stability_results.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Write header row
    writer.writerow(['av', 'bv', 'cv', 'dv', 'A Matrix', 'Stability'])
    for av in range(-10,10):
        for bv in range(-10,10):
            for cv in range(-10,10):
                for dv in range(-10,10):
                    aMat = np.array([[av, bv], [cv, dv]])
                    stability = compute_stability(aMat)
                        
                        # Write the matrix and stability to the CSV file
                    writer.writerow([av, bv, cv, dv, aMat.tolist(), stability])