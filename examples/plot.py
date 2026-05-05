import numpy as np
import simos as sos
import qutip
from nv_teleportation import nv_teleport
import matplotlib.pyplot as plt

F_ent_values = np.linspace(0.25, 1.0)

F_no_dephasing = [nv_teleport(F_ent=f, T2_E3=None,   verbose=False) for f in F_ent_values]
F_free         = [nv_teleport(F_ent=f, T2_E3='free',  verbose=False) for f in F_ent_values]
F_echo         = [nv_teleport(F_ent=f, T2_E3='echo',  verbose=False) for f in F_ent_values]

plt.figure(figsize=(8, 5))
plt.plot(F_ent_values, F_free,         label='Free decay (T2*=2us)')
plt.plot(F_ent_values, F_echo,         label='Hahn echo (T2=1.8ms)')
plt.axvline(0.87, color='gray', linestyle=':', label='Pfaff F_ent=0.87')
plt.xlabel('Entanglement fidelity F_ent')
plt.ylabel('Average teleportation fidelity F_avg')
plt.title('NV Center Teleportation Fidelity vs Entanglement Quality')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('fidelity_sweep.png', dpi=150)
plt.show()