"""Tests for `nv_teleportation` package."""

import nv_teleportation


def test_import():
    """Verify the package can be imported."""
    assert nv_teleportation


"""
Tests for the nv_teleportation package.

Run with:  pytest tests/test_nv_teleportation.py -v

Pytest discovers functions whose names start with test_.
Each test_ function is independent — a failure in one does not
affect the others.
"""

import numpy as np
import pytest
import simos as sos
import qutip

from nv_teleportation import nv_teleport   

# ── Shared constants ──────────────────────────────────────────────────────────
CLASSICAL_BOUND = 2 / 3


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 1 — Import
# ═══════════════════════════════════════════════════════════════════════════════

def test_import():
    """Verify the function can be imported from the package."""
    assert callable(nv_teleport), "nv_teleport should be a callable function"


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 2 — Perfect protocol (no errors)
# F_avg should be 1.0 for all Bell states and all source states
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("bell", ["psi_plus", "psi_minus", "phi_plus", "phi_minus"])
def test_perfect_protocol_all_bell_states(bell):
    """
    With no errors, every Bell state resource should give F_avg = 1.0.
    This is the ground truth check for the core circuit logic.
    """
    F = nv_teleport(F_ent=1.0, T2_E3=None, bell=bell, verbose=False)
    assert abs(F - 1.0) < 1e-4, (
        f"Perfect protocol with {bell}: F_avg={F:.6f}, expected 1.0"
    )


@pytest.mark.parametrize("a, b, label", [
    (1.0,           0.0,           "|0>"),
    (0.0,           1.0,           "|1>"),
    (1/np.sqrt(2),  1/np.sqrt(2),  "|+>"),
    (1/np.sqrt(2), -1/np.sqrt(2),  "|->"),
    (1/np.sqrt(2),  1j/np.sqrt(2), "|+i>"),
    (1/np.sqrt(3),  np.sqrt(2/3),  "asymmetric"),
])
def test_perfect_protocol_source_states(a, b, label):
    """
    With no errors, teleportation should work perfectly for any source state.
    Tests the six cardinal Bloch sphere states plus an asymmetric state.
    """
    F = nv_teleport(a=a, b=b, F_ent=1.0, T2_E3=None,
                    bell='psi_plus', verbose=False)
    assert abs(F - 1.0) < 1e-4, (
        f"Perfect protocol, source={label}: F_avg={F:.6f}, expected 1.0"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 3 — Classical bound
# Realistic error parameters should still exceed F > 2/3
# ═══════════════════════════════════════════════════════════════════════════════

def test_perfect_exceeds_classical_bound():
    """Perfect protocol must comfortably exceed F > 2/3."""
    F = nv_teleport(F_ent=1.0, T2_E3=None, verbose=False)
    assert F > CLASSICAL_BOUND, (
        f"Perfect protocol: F={F:.4f} should exceed {CLASSICAL_BOUND:.4f}"
    )


def test_pfaff_realistic_exceeds_classical_bound():
    """
    Pfaff et al. realistic parameters (F_ent=0.87, Hahn echo dephasing)
    should still demonstrate quantum teleportation (F > 2/3).
    """
    F = nv_teleport(F_ent=0.87, T2_E3='echo', verbose=False)
    assert F > CLASSICAL_BOUND, (
        f"Pfaff realistic: F={F:.4f} should exceed {CLASSICAL_BOUND:.4f}"
    )


def test_pfaff_pessimistic_exceeds_classical_bound():
    """
    Even with T2* free decay (no echo, pessimistic), Pfaff parameters
    should still exceed the classical bound.
    """
    F = nv_teleport(F_ent=0.87, T2_E3='free', verbose=False)
    assert F > CLASSICAL_BOUND, (
        f"Pfaff pessimistic: F={F:.4f} should exceed {CLASSICAL_BOUND:.4f}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 4 — Entanglement fidelity degrades F_avg monotonically
# ═══════════════════════════════════════════════════════════════════════════════

def test_entanglement_fidelity_monotonic_decrease():
    """
    As F_ent decreases, F_avg should decrease monotonically.
    Checks that the Werner noise model is correctly wired in.
    """
    F_values = []
    for F_ent in [1.0, 0.95, 0.90, 0.87, 0.80, 0.70]:
        F = nv_teleport(F_ent=F_ent, T2_E3=None, verbose=False)
        F_values.append((F_ent, F))

    for i in range(len(F_values) - 1):
        F_ent_hi, F_hi = F_values[i]
        F_ent_lo, F_lo = F_values[i + 1]
        assert F_lo <= F_hi + 1e-4, (
            f"F_avg should decrease as F_ent decreases: "
            f"F_ent={F_ent_lo} gave F={F_lo:.4f}, "
            f"but F_ent={F_ent_hi} gave F={F_hi:.4f}"
        )


def test_maximally_mixed_resource_fails_classically():
    """
    F_ent = 0.25 means the resource state is maximally mixed (no entanglement).
    The protocol should fail to exceed the classical bound.
    """
    F = nv_teleport(F_ent=0.25, T2_E3=None, verbose=False)
    assert F <= CLASSICAL_BOUND + 0.01, (
        f"Maximally mixed resource: F={F:.4f} should be <= {CLASSICAL_BOUND:.4f}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 5 — Dephasing effects
# ═══════════════════════════════════════════════════════════════════════════════

def test_free_decay_reduces_fidelity():
    """
    T2* free decay (T2*=2us) should significantly reduce fidelity
    because T_gate (~397ns) is comparable to T2*.
    """
    F_perfect = nv_teleport(F_ent=1.0, T2_E3=None,   verbose=False)
    F_free    = nv_teleport(F_ent=1.0, T2_E3='free',  verbose=False)
    assert F_free < F_perfect - 1e-4, (
        f"Free decay should reduce fidelity: "
        f"F_free={F_free:.4f}, F_perfect={F_perfect:.4f}"
    )


def test_echo_barely_affects_fidelity():
    """
    Hahn echo dephasing (T2=1.8ms) should barely affect fidelity
    because T_gate (~397ns) << T2_hahn (1.8ms).
    The difference should be less than 1%.
    """
    F_perfect = nv_teleport(F_ent=1.0, T2_E3=None,   verbose=False)
    F_echo    = nv_teleport(F_ent=1.0, T2_E3='echo',  verbose=False)
    diff = abs(F_echo - F_perfect)
    assert diff < 0.01, (
        f"Echo dephasing should barely affect fidelity: "
        f"difference={diff:.6f}, expected < 0.01"
    )


def test_echo_better_than_free_decay():
    """
    Echo model (T2=1.8ms) should give higher fidelity than free decay
    (T2*=2us) because echo refocuses the slow noise.
    """
    F_echo = nv_teleport(F_ent=1.0, T2_E3='echo', verbose=False)
    F_free = nv_teleport(F_ent=1.0, T2_E3='free', verbose=False)
    assert F_echo > F_free - 1e-4, (
        f"Echo should give higher fidelity than free decay: "
        f"F_echo={F_echo:.4f}, F_free={F_free:.4f}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 6 — BSM measurement probability sanity
# Each outcome should have p=0.25, all four should sum to 1
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def three_qubit_system():
    """
    Pytest fixture: builds the 3-qubit system and initial Bell state.
    Shared across all probability sanity tests.
    A fixture runs once per test that requests it.
    """
    N  = {"name": "N",  "val": 1/2}
    E2 = {"name": "E2", "val": 1/2}
    E3 = {"name": "E3", "val": 1/2}
    s  = sos.System([N, E2, E3])

    ket_001 = sos.state(s, "N[-0.5],E2[-0.5],E3[0.5]")
    ket_010 = sos.state(s, "N[-0.5],E2[0.5],E3[-0.5]")
    ket_101 = sos.state(s, "N[0.5],E2[-0.5],E3[0.5]")
    ket_110 = sos.state(s, "N[0.5],E2[0.5],E3[-0.5]")

    a = b = 1/np.sqrt(2)
    rho = sos.ket2dm((a*ket_001 + a*ket_010 + b*ket_101 + b*ket_110).unit())

    P_N0 = s.Np[-0.5]; P_N1 = s.Np[0.5]
    P_E0 = s.E2p[-0.5]; P_E1 = s.E2p[0.5]
    projectors = {
        "00": P_N0 * P_E0,
        "01": P_N0 * P_E1,
        "10": P_N1 * P_E0,
        "11": P_N1 * P_E1,
    }
    probs = {
        k: float(sos.expect(P, rho).real)
        for k, P in projectors.items()
    }
    return s, rho, projectors, probs


def test_probabilities_sum_to_one(three_qubit_system):
    """All four BSM outcome probabilities must sum to 1."""
    _, _, _, probs = three_qubit_system
    total = sum(probs.values())
    assert abs(total - 1.0) < 1e-6, (
        f"Probabilities sum to {total:.8f}, expected 1.0"
    )


@pytest.mark.parametrize("outcome", ["00", "01", "10", "11"])
def test_equal_bsm_probabilities(three_qubit_system, outcome):
    """
    For a maximally entangled Bell state with equal superposition source,
    each BSM outcome should occur with probability 0.25.
    """
    _, _, _, probs = three_qubit_system
    p = probs[outcome]
    assert abs(p - 0.25) < 1e-4, (
        f"Outcome {outcome}: p={p:.6f}, expected 0.25"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 7 — Density matrix sanity
# ═══════════════════════════════════════════════════════════════════════════════

def test_initial_state_is_pure(three_qubit_system):
    """Initial state (no noise) must be a pure state: Tr(rho^2) = 1."""
    _, rho, _, _ = three_qubit_system
    purity = (rho * rho).tr().real
    assert abs(purity - 1.0) < 1e-6, (
        f"Initial state purity = {purity:.6f}, expected 1.0"
    )


def test_initial_state_trace_one(three_qubit_system):
    """Initial density matrix must have Tr(rho) = 1."""
    _, rho, _, _ = three_qubit_system
    tr = rho.tr().real
    assert abs(tr - 1.0) < 1e-6, f"Tr(rho) = {tr:.6f}, expected 1.0"


def test_werner_state_is_mixed(three_qubit_system):
    """
    After Werner noise mixing, the state should be mixed: Tr(rho^2) < 1.
    Checks the entanglement noise model produces a genuinely mixed state.
    """
    _, rho, _, _ = three_qubit_system
    rho_mixed = qutip.tensor(qutip.qeye(2), qutip.qeye(2), qutip.qeye(2)) / 8
    rho_noisy = 0.87 * rho + 0.13 * rho_mixed
    purity = (rho_noisy * rho_noisy).tr().real
    assert purity < 0.999, (
        f"Werner state purity = {purity:.6f}, expected < 0.999 (mixed)"
    )


def test_werner_state_trace_one(three_qubit_system):
    """Werner noise mixing must preserve Tr(rho) = 1."""
    _, rho, _, _ = three_qubit_system
    rho_mixed = qutip.tensor(qutip.qeye(2), qutip.qeye(2), qutip.qeye(2)) / 8
    rho_noisy = 0.87 * rho + 0.13 * rho_mixed
    tr = rho_noisy.tr().real
    assert abs(tr - 1.0) < 1e-6, f"Werner state Tr = {tr:.6f}, expected 1.0"


def test_dephasing_channel_preserves_trace(three_qubit_system):
    """Kraus dephasing channel must preserve Tr(rho) = 1."""
    s, rho, _, _ = three_qubit_system
    decay = np.exp(-397e-9 / 2e-6)
    K0 = np.sqrt((1 + decay) / 2) * s.Nid
    K1 = np.sqrt((1 - decay) / 2) * (2 * s.E3z)
    rho_dephased = K0 * rho * K0.dag() + K1 * rho * K1.dag()
    tr = rho_dephased.tr().real
    assert abs(tr - 1.0) < 1e-6, (
        f"Dephasing channel Tr = {tr:.6f}, expected 1.0"
    )


def test_dephasing_channel_makes_state_mixed(three_qubit_system):
    """
    Dephasing channel should reduce purity below 1.
    A pure state should become mixed after dephasing.
    """
    s, rho, _, _ = three_qubit_system
    decay = np.exp(-397e-9 / 2e-6)
    K0 = np.sqrt((1 + decay) / 2) * s.Nid
    K1 = np.sqrt((1 - decay) / 2) * (2 * s.E3z)
    rho_dephased = K0 * rho * K0.dag() + K1 * rho * K1.dag()
    purity = (rho_dephased * rho_dephased).tr().real
    assert purity < 0.999, (
        f"Dephased state purity = {purity:.6f}, expected < 0.999"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 8 — Input validation
# ═══════════════════════════════════════════════════════════════════════════════

def test_invalid_bell_state_raises():
    """Passing an unrecognised Bell state name should raise ValueError."""
    with pytest.raises(ValueError):
        nv_teleport(bell='invalid', verbose=False)


def test_invalid_t2_model_raises():
    """Passing an unrecognised T2_E3 model string should raise ValueError."""
    with pytest.raises(ValueError):
        nv_teleport(T2_E3='invalid', verbose=False)