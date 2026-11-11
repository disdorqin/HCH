"""Frozen fit_base_predict state-order regression, with ineligible outlier days.

Standalone synthetic tests; no access to research targets or frozen runner imports.
"""
from __future__ import annotations
import copy

import numpy as np
import torch

from hch.capacity import inner_split
from hch.model import DailyPatchShape, signed_direction
from hch.pipeline import _fit_one, _fresh, _forward, LR, WD


def _case():
    rng = np.random.default_rng(101)
    n = 32
    x = rng.normal(size=(n, 624)).astype(np.float32)
    cal = x[:, 528:624].copy()
    state = rng.normal(size=(n, 24)).astype(np.float64)
    valid = np.ones(n, dtype=bool)
    valid[[3, 8, 27]] = False  # zero-residual/ineligible training origins
    state[[3, 8, 27]] += 400.0  # deliberately different state distribution
    pred_x = x[-3:].copy()
    pred_state = np.full((3, 24), 40.0)
    pred_cal = cal[-3:].copy()
    target = rng.normal(size=(n, 24)).astype(np.float32)
    target /= np.linalg.norm(target, axis=1, keepdims=True)
    target[~valid] = 0  # target zero, still part of state normalization
    return x, state, cal, target, valid, pred_x, pred_state, pred_cal


def _moments_before_filter(state, valid, pred_state):
    mu = state.mean(axis=0, keepdims=True)
    sd = state.std(axis=0, keepdims=True) + 1e-6
    all_norm = (state - mu) / sd
    test_norm = (pred_state - mu) / sd
    return all_norm[valid], test_norm, mu[0], sd[0]


def test_frozen_full_prefix_state_norm_includes_ineligible_outlier_origins():
    args = _case()
    x, state, cal, target, valid, pred_x, pred_state, pred_cal = args
    model, direction, selected, mu, sd = _fit_one(
        x, state, cal, target, valid, np.arange(len(x)),
        pred_x, pred_state, pred_cal, 1, 17, (0,)
    )
    eligible_state, later_state, expect_mu, expect_sd = _moments_before_filter(
        state, valid, pred_state
    )
    np.testing.assert_array_equal(mu, expect_mu)
    np.testing.assert_array_equal(sd, expect_sd)
    # Old bug: filtering valid rows first moves the state moments massively.
    assert np.max(np.abs(mu - state[valid].mean(axis=0))) > 30
    assert selected == 0 and eligible_state.shape[0] == valid.sum()
    with torch.no_grad():
        expected = signed_direction(_forward(model, pred_x, later_state, pred_cal)).numpy()
    np.testing.assert_array_equal(direction, expected)


def test_checkpoint_and_identical_initialization_full_refit_match_frozen_order():
    x, state, cal, target, valid, pred_x, pred_state, pred_cal = _case()
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(1)
    chosen, direction, selected, mu, sd = _fit_one(
        x, state, cal, target, valid, np.arange(len(x)),
        pred_x, pred_state, pred_cal, 1, 29, (0, 25)
    )
    eligible_idx = np.flatnonzero(valid)
    sf, sp, expected_mu, expected_sd = _moments_before_filter(state, valid, pred_state)
    np.testing.assert_array_equal(mu, expected_mu)
    np.testing.assert_array_equal(sd, expected_sd)
    tr, va = inner_split(np.arange(len(eligible_idx)))
    init = copy.deepcopy(_fresh(29, 1).state_dict())

    def loss(model, ix, st):
        z = _forward(model, x[eligible_idx[ix]], sf[ix], cal[eligible_idx[ix]])
        y = torch.as_tensor(target[eligible_idx[ix]], dtype=torch.float32)
        return torch.nn.functional.mse_loss(z, y)

    probe = DailyPatchShape(1)
    probe.load_state_dict(init)
    reference_best = float(loss(probe, va, sf).detach())
    reference_step = 0
    opt = torch.optim.AdamW(probe.parameters(), lr=LR, weight_decay=WD)
    for step in range(1, 26):
        opt.zero_grad(set_to_none=True)
        objective = loss(probe, tr, sf)
        objective.backward()
        torch.nn.utils.clip_grad_norm_(probe.parameters(), 1.0)
        opt.step()
        if step == 25:
            value = float(loss(probe, va, sf).detach())
            if value < reference_best - 1e-12:
                reference_best, reference_step = value, step
    assert selected == reference_step

    refit = DailyPatchShape(1)
    refit.load_state_dict(init)
    if reference_step:
        opt2 = torch.optim.AdamW(refit.parameters(), lr=LR, weight_decay=WD)
        full = np.arange(len(eligible_idx))
        for _ in range(reference_step):
            opt2.zero_grad(set_to_none=True)
            objective = loss(refit, full, sf)
            objective.backward()
            torch.nn.utils.clip_grad_norm_(refit.parameters(), 1.0)
            opt2.step()
    for name, reference in refit.state_dict().items():
        torch.testing.assert_close(chosen.state_dict()[name], reference, rtol=0, atol=0)
    with torch.no_grad():
        expected = signed_direction(_forward(refit, pred_x, sp, pred_cal)).numpy()
    np.testing.assert_array_equal(direction, expected)
