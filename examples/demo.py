
from nv_teleportation import nv_teleport

import numpy as np
import simos as sos
import qutip

# very the protocol works will all 4 bell states
print("Perfect:")
nv_teleport(bell='phi_plus' ,F_ent=1.0, T2_E3=None)
nv_teleport(bell='phi_minus' ,F_ent=1.0, T2_E3=None)
nv_teleport(bell='psi_plus' ,F_ent=1.0, T2_E3=None)
nv_teleport(bell='psi_minus' ,F_ent=1.0, T2_E3=None)

print("Entanglement error only (Pfaff):")
nv_teleport(F_ent=0.87, T2_E3=None)

print("Free decay dephasing only:")
nv_teleport(F_ent=1.0, T2_E3='free')

print("Hahn echo dephasing only:")
nv_teleport(F_ent=1.0, T2_E3='echo')

print("All errors (Pfaff realistic):")
nv_teleport(F_ent=0.87, T2_E3='echo')

