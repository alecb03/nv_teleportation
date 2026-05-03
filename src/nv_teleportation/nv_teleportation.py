import numpy as np
import simos as sos
import qutip

def nv_teleport(
    a     = 1/np.sqrt(2),
    b     = 1/np.sqrt(2),
    bell  = 'psi_plus',
    F_ent = 1.0,
    T2_E3 = None,       # None | 'free' | 'echo'
    verbose = True,
):
    '''
    NV Center teleportation protocol based on Pfaff et al.
    https://doi.org/10.48550/arXiv.1404.4369

    Parameters
    ----------
    a, b    : complex amplitudes of the source state a|0> + b|1>
              (will be normalised automatically)
    bell    : entanglement resource -- 'psi_plus' | 'psi_minus' |
                                       'phi_plus' | 'phi_minus'
    F_ent   : optical entanglement fidelity (1.0 = perfect)
              Pfaff measured F_ent ~ 0.87
    T2_E3   : dephasing model for Bob's qubit during the BSM gate time
              None   -- no dephasing
              'free' -- T2* free decay:  exp(-t/T2*)   T2* = 2 us
              'echo' -- Hahn echo decay: exp(-(t/T2)^n) T2 = 1.8 ms, n=1.5
    verbose : print per-outcome results

    Returns
    -------
    avg_F : probability-weighted average teleportation fidelity
    '''

    # ═══════════════════════════════════════════════════════════════
    # STEP 1 — System and basis states
    # ═══════════════════════════════════════════════════════════════

    N  = {"name": "N",  "val": 1/2}   # qubit 1: N14 nuclear spin (eff. spin-1/2)
    E2 = {"name": "E2", "val": 1/2}   # qubit 2: Alice's electron spin
    E3 = {"name": "E3", "val": 1/2}   # qubit 3: Bob's electron spin

    s     = sos.System([N, E2, E3])
    s_bob = sos.System([{"name": "E3", "val": 1/2}])

    # Convention: m = -0.5 --> |0>,  m = +0.5 --> |1>
    ket_000 = sos.state(s, "N[-0.5],E2[-0.5],E3[-0.5]")
    ket_001 = sos.state(s, "N[-0.5],E2[-0.5],E3[0.5]")
    ket_010 = sos.state(s, "N[-0.5],E2[0.5],E3[-0.5]")
    ket_011 = sos.state(s, "N[-0.5],E2[0.5],E3[0.5]")
    ket_100 = sos.state(s, "N[0.5],E2[-0.5],E3[-0.5]")
    ket_101 = sos.state(s, "N[0.5],E2[-0.5],E3[0.5]")
    ket_110 = sos.state(s, "N[0.5],E2[0.5],E3[-0.5]")
    ket_111 = sos.state(s, "N[0.5],E2[0.5],E3[0.5]")

    # ═══════════════════════════════════════════════════════════════
    # STEP 2 — Ideal CNOT gate (N control, E2 target)
    # ═══════════════════════════════════════════════════════════════
    #
    # Built as an explicit unitary from its action on each basis state.
    # N=|0> (m=-0.5): E2 unchanged
    # N=|1> (m=+0.5): E2 flipped

    U_cnot = (  ket_000 * ket_000.dag()
               + ket_001 * ket_001.dag()
               + ket_010 * ket_010.dag()
               + ket_011 * ket_011.dag()
               + ket_110 * ket_100.dag()   # |100> -> |110>
               + ket_111 * ket_101.dag()   # |101> -> |111>
               + ket_100 * ket_110.dag()   # |110> -> |100>
               + ket_101 * ket_111.dag()   # |111> -> |101>
              )

    # ═══════════════════════════════════════════════════════════════
    # STEP 3 — Build Psi_total
    # ═══════════════════════════════════════════════════════════════
    #
    # Psi_total = (a|0> + b|1>)_N  ⊗  |Bell>_{E2,E3}
    # Expanded:
    #   psi_plus:  (1/√2)(a(|001>+|010>) + b(|101>+|110>))
    #   psi_minus: (1/√2)(a(|001>-|010>) + b(|101>-|110>))
    #   phi_plus:  (1/√2)(a(|000>+|011>) + b(|100>+|111>))
    #   phi_minus: (1/√2)(a(|000>-|011>) + b(|100>-|111>))

    bell_kets = {
        'psi_plus':  (a*ket_001 + a*ket_010 + b*ket_101 + b*ket_110),
        'psi_minus': (a*ket_001 - a*ket_010 + b*ket_101 - b*ket_110),
        'phi_plus':  (a*ket_000 + a*ket_011 + b*ket_100 + b*ket_111),
        'phi_minus': (a*ket_000 - a*ket_011 + b*ket_100 - b*ket_111),
    }
    if bell not in bell_kets:
        raise ValueError(f"bell must be one of {list(bell_kets.keys())}")

    rho = sos.ket2dm(bell_kets[bell].unit())

    # ═══════════════════════════════════════════════════════════════
    # STEP 4 — Optical entanglement error (Werner state noise)
    # ═══════════════════════════════════════════════════════════════
    #
    # The heralded Bell state is never perfect. We model the imperfect
    # state as a mixture of the ideal state and the maximally mixed state:
    #   rho_noisy = F_ent * rho_ideal + (1 - F_ent) * I/8
    # F_ent = 0.87 from Pfaff et al.

    if F_ent < 1.0:
        rho_mixed = qutip.tensor(
            qutip.qeye(2), qutip.qeye(2), qutip.qeye(2)
        ) / 8
        rho = F_ent * rho + (1 - F_ent) * rho_mixed

    # ═══════════════════════════════════════════════════════════════
    # STEP 5 — T2 dephasing on Bob's qubit (E3)
    # ═══════════════════════════════════════════════════════════════
    #
    # Bob's qubit dephases while Alice performs her BSM operations.
    # We apply a Kraus dephasing channel:
    #   rho -> K0 rho K0† + K1 rho K1†
    #   K0 = sqrt((1+decay)/2) * I
    #   K1 = sqrt((1-decay)/2) * Z    (Z = 2*E3z in our spin-1/2 convention)
    #
    # Two decay models:
    #   free: exp(-t/T2*)      T2* = 2 us   (no echo, dominated by spin bath)
    #   echo: exp(-(t/T2)^n)   T2  = 1.8ms, n=1.5  (with Hahn echo)
    #
    # Gate time: T_gate = pi/Omega = pi*sqrt(3)/A_hf ~ 397 ns

    A_hf   = 2.19e6                         # hyperfine coupling [Hz]
    T_gate = np.pi / (A_hf / np.sqrt(3))    # CNOT gate time [s]

    if T2_E3 is not None:
        t = T2_E3.lower()   # normalise capitalisation
        if t == 'free':
            T2_star = 2e-6                          # T2* = 2 us
            decay = np.exp(-T_gate / T2_star)
        elif t == 'echo':
            T2_hahn = 1.8e-3                        # T2 = 1.8 ms
            n       = 1.5                           # stretch exponent
            decay = np.exp(-(T_gate / T2_hahn)**n)
        else:
            raise ValueError("T2_E3 must be None, 'free', or 'echo'")

        # Kraus operators acting on the full 8-dim space via E3z
        K0 = np.sqrt((1 + decay) / 2) * s.Nid       # s.Nid = 8x8 identity
        K1 = np.sqrt((1 - decay) / 2) * (2 * s.E3z) # 2*E3z = Pauli Z on E3

        rho = K0 * rho * K0.dag() + K1 * rho * K1.dag()

        if verbose:
            print(f"  E3 dephasing ({t}): "
                  f"T_gate={T_gate*1e9:.0f}ns, decay={decay:.6f}")

    # ═══════════════════════════════════════════════════════════════
    # STEP 6 — BSM circuit: CNOT then Hadamard on N
    # ═══════════════════════════════════════════════════════════════

    rho = U_cnot * rho * U_cnot.dag()
    rho = sos.rot(s.Ny, np.pi/2, rho)

    # ═══════════════════════════════════════════════════════════════
    # STEP 7 — Discover the feed-forward correction table
    # ═══════════════════════════════════════════════════════════════
    #
    # We find the correct Pauli correction for each BSM outcome by
    # running the ideal circuit on a fixed asymmetric test state and
    # checking which Pauli gives F=1.
    # We use an asymmetric state (a not equal to b) so that I, X, Y, Z all
    # produce distinguishably different output states.
    # This is done on a clean rho (no noise) so the table is exact.

    def discover_correction_table():
        a_t = 1/np.sqrt(3)
        b_t = np.sqrt(2/3)

        psi_test = bell_kets[bell]   # reuse same Bell state structure
        # rebuild with test coefficients
        test_map = {
            'psi_plus':  (a_t*ket_001 + a_t*ket_010 + b_t*ket_101 + b_t*ket_110),
            'psi_minus': (a_t*ket_001 - a_t*ket_010 + b_t*ket_101 - b_t*ket_110),
            'phi_plus':  (a_t*ket_000 + a_t*ket_011 + b_t*ket_100 + b_t*ket_111),
            'phi_minus': (a_t*ket_000 - a_t*ket_011 + b_t*ket_100 - b_t*ket_111),
        }
        rho_t = sos.ket2dm(test_map[bell].unit())  # clean, no noise
        rho_t = U_cnot * rho_t * U_cnot.dag()
        rho_t = sos.rot(s.Ny, np.pi/2, rho_t)

        ket_E3_0 = sos.state(s_bob, "E3[-0.5]")
        ket_E3_1 = sos.state(s_bob, "E3[0.5]")
        rho_target_t = sos.ket2dm((a_t*ket_E3_0 + b_t*ket_E3_1).unit())

        P_N0 = s.Np[-0.5]; P_N1 = s.Np[0.5]
        P_E0 = s.E2p[-0.5]; P_E1 = s.E2p[0.5]
        projectors_t = {
            "00": P_N0 * P_E0, "01": P_N0 * P_E1,
            "10": P_N1 * P_E0, "11": P_N1 * P_E1,
        }
        candidates = {
            "I": lambda r: r,
            "X": lambda r: sos.rot(s_bob.E3x, np.pi, r),
            "Y": lambda r: sos.rot(s_bob.E3y, np.pi, r),
            "Z": lambda r: sos.rot(s_bob.E3z, np.pi, r),
        }
        table = {}
        for outcome, P in projectors_t.items():
            prob = float(sos.expect(P, rho_t).real)
            rho_E3 = ((P * rho_t * P) / prob).ptrace([2])
            best_pauli, best_F = "I", -1
            for pauli, correction in candidates.items():
                F = float((rho_target_t * correction(rho_E3)).tr().real)
                if F > best_F:
                    best_F, best_pauli = F, pauli
            table[outcome] = candidates[best_pauli]
        return table

    correction_table = discover_correction_table()

    # ═══════════════════════════════════════════════════════════════
    # STEP 8 — Measure, correct, compute fidelity
    # ═══════════════════════════════════════════════════════════════

    P_N0 = s.Np[-0.5]; P_N1 = s.Np[0.5]
    P_E0 = s.E2p[-0.5]; P_E1 = s.E2p[0.5]
    projectors = {
        "00": P_N0 * P_E0, "01": P_N0 * P_E1,
        "10": P_N1 * P_E0, "11": P_N1 * P_E1,
    }

    ket_E3_0 = sos.state(s_bob, "E3[-0.5]")
    ket_E3_1 = sos.state(s_bob, "E3[0.5]")
    rho_target = sos.ket2dm((a * ket_E3_0 + b * ket_E3_1).unit())

    fidelities = []   
    if verbose:
        print(f"\n  Bell={bell}  F_ent={F_ent}  T2_E3={T2_E3}")
        print(f"  {'─'*40}")

    for outcome, P in projectors.items():
        prob = float(sos.expect(P, rho).real)
        if prob < 1e-10:
            continue
        rho_E3       = ((P * rho * P) / prob).ptrace([2])
        rho_corrected = correction_table[outcome](rho_E3)
        F = float((rho_target * rho_corrected).tr().real)
        fidelities.append((prob, F))
        if verbose:
            print(f"  BSM={outcome}  p={prob:.4f}  F={F:.4f}")

    avg_F = sum(p * F for p, F in fidelities)

    if verbose:
        print(f"  {'─'*40}")
        print(f"  F_avg = {avg_F:.4f}")
    return avg_F


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    print("Perfect:")
    nv_teleport(bell='phi_plus' ,F_ent=1.0, T2_E3=None)

    print("Entanglement error only (Pfaff):")
    nv_teleport(F_ent=0.87, T2_E3=None)

    print("Free decay dephasing only:")
    nv_teleport(F_ent=1.0, T2_E3='free')

    print("Hahn echo dephasing only:")
    nv_teleport(F_ent=1.0, T2_E3='echo')

    print("All errors (Pfaff realistic):")
    nv_teleport(F_ent=0.87, T2_E3='echo')

