"""Exact architecture of the registered HCH B2 direction estimator.

Scientific source: frozen S1-B2 runner DailyPatchShape (provenance retained in the author research archive).
The method's output is raw direction scores, not a forecast, learned amplitude, or verifier gate.
"""
from __future__ import annotations
import torch
from torch import nn

class DailyPatchShape(nn.Module):
    def __init__(self, nstate: int):
        super().__init__()
        self.hist = nn.Linear(72, 32)
        self.future = nn.Linear(24 * (1 + nstate + 4), 32)
        self.gru = nn.GRU(32, 32, batch_first=True)
        self.readout = nn.Linear(32, 24)

    def features(self, x: torch.Tensor, state: torch.Tensor, cal: torch.Tensor) -> torch.Tensor:
        ha = x[:, :168].reshape(-1, 7, 24)
        hr = x[:, 168:336].reshape(-1, 7, 24)
        hm = x[:, 336:504].reshape(-1, 7, 24)
        ht = torch.nn.functional.silu(self.hist(torch.cat((ha, hr, hm), 2)))
        host = x[:, 504:528]
        ft = torch.nn.functional.silu(self.future(torch.cat((host, state, cal), 1))).unsqueeze(1)
        _, z = self.gru(torch.cat((ht, ft), 1))
        return z[-1]

    def forward(self, x: torch.Tensor, state: torch.Tensor, cal: torch.Tensor) -> torch.Tensor:
        return self.readout(self.features(x, state, cal))

def signed_direction(raw_scores: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    """Per-origin L2-stabilized signed 24-hour direction; eps matches the frozen runner."""
    return raw_scores / (torch.linalg.vector_norm(raw_scores, dim=1, keepdim=True) + eps)
