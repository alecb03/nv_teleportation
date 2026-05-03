# Usage

# Basic teleportation

```python
from nv_teleportation import nv_teleport

# Perfect protocol
F = nv_teleport(F_ent=1.0, T2_E3=None, verbose=True)

# Pfaff et al. realistic parameters
F = nv_teleport(F_ent=0.87, T2_E3='echo', verbose=True)
```

# Parameters

- `bell` — choose the entanglement resource: `'psi_plus'`, `'psi_minus'`, `'phi_plus'`, `'phi_minus'`
- `F_ent` — optical entanglement fidelity (0 to 1). Pfaff measured ~0.87
- `T2_E3` — dephasing model for Bob's qubit: `None`, `'free'`, or `'echo'`