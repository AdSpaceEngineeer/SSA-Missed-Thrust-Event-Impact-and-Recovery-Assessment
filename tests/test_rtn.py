import numpy as np

from ssa_mte.rtn import relative_state_eci_to_rtn, rtn_rotation_matrix_from_state


def test_rtn_rotation_matrix_is_orthonormal_for_circular_equatorial_state():
    r = np.array([7000.0, 0.0, 0.0])
    v = np.array([0.0, 7.5, 0.0])

    c = rtn_rotation_matrix_from_state(r, v)

    np.testing.assert_allclose(c @ c.T, np.eye(3), atol=1e-12)
    np.testing.assert_allclose(c[0], np.array([1.0, 0.0, 0.0]), atol=1e-12)
    np.testing.assert_allclose(c[1], np.array([0.0, 1.0, 0.0]), atol=1e-12)
    np.testing.assert_allclose(c[2], np.array([0.0, 0.0, 1.0]), atol=1e-12)


def test_relative_state_eci_to_rtn_projects_position_and_velocity():
    op_r = np.array([7000.0, 0.0, 0.0])
    op_v = np.array([0.0, 7.5, 0.0])
    target_r = np.array([7001.0, 2.0, 3.0])
    target_v = np.array([0.1, 7.7, -0.3])

    rel = relative_state_eci_to_rtn(op_r, op_v, target_r, target_v)

    np.testing.assert_allclose(rel["rel_r_km"], 1.0)
    np.testing.assert_allclose(rel["rel_t_km"], 2.0)
    np.testing.assert_allclose(rel["rel_n_km"], 3.0)
    np.testing.assert_allclose(rel["rel_v_r_km_s"], 0.1)
    np.testing.assert_allclose(rel["rel_v_t_km_s"], 0.2)
    np.testing.assert_allclose(rel["rel_v_n_km_s"], -0.3)
