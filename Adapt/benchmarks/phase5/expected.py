"""Phase 5 benchmark constants. Frozen before execution."""

from __future__ import annotations

BENCHMARK_VERSION = "phase5-v1"
RANDOM_SEED = 20260814
PLANNED_PARTICIPANTS = 10

SYNTHETIC_EXPECTED = {
    "SYN-A": 0.10,
    "SYN-B": -0.10,
    "SYN-C": 0.0,
}

HISTORICAL_ARTIFACTS = (
    "results/phase1e/metrics.json",
    "results/phase1e/raw_results.json",
    "results/phase1e/report.md",
    "results/phase1f/metrics.json",
    "results/phase1f/raw_results.json",
    "results/phase1f/report.md",
    "results/phase1f/holdout_results.json",
    "results/phase1f/development_results.json",
    "results/phase2/metrics.json",
    "results/phase2/raw_results.json",
    "results/phase2/report.md",
    "results/phase3/metrics.json",
    "results/phase3/raw_results.json",
    "results/phase3/report.md",
    "results/phase3/trajectories.json",
    "results/phase4/metrics.json",
    "results/phase4/raw_results.json",
    "results/phase4/report.md",
    "results/phase4/usability.md",
)

HISTORICAL_SHA256 = {
    "results/phase1e/metrics.json": "0aa9cfeabd0fa9cc123cf9af04cd8b2f729b643151c77fdbe4a94b489e113e85",
    "results/phase1e/raw_results.json": "4efc304481b00841b46babb698368891ddb9171f714209e095543790bfd895ba",
    "results/phase1e/report.md": "8751b514438fc3f671e0c95e489551d381ec6f67a681cf29284e24c670dae672",
    "results/phase1f/metrics.json": "a5e1b75df91072a134b0df743f7b402b66af8dd4d5ea0915d3a89dc43f0bb9c0",
    "results/phase1f/raw_results.json": "3971bec69c5bc13e8bd64f545443b66933b562d63bd3841ea4be20f3b64b3a4a",
    "results/phase1f/report.md": "5f55c0f8aa8c5b55e674d9f46cc7f0abcf3f5524d3d16d40aeaab1c52997ba4b",
    "results/phase1f/holdout_results.json": "8ca74bb0eedb96a499d0ff6e27ee83d62df961fbef50e5bbdf7cd6072bd44d0f",
    "results/phase1f/development_results.json": "e7b84821b03415add96f6cda576b8aae9d2278c6d04699a9ea772ff0a6ed686b",
    "results/phase2/metrics.json": "97a232f7315a37a55ba27c579a4b1292baefe2ffd7bc9736ea87795a402ca53a",
    "results/phase2/raw_results.json": "4766d466e8a45e04389f6261585cb646a721d9485d6b2d51944466b45243309a",
    "results/phase2/report.md": "e5135fee217a69b0e47c27f8112c344e24edc239dfa8dfd23bed99f5e08150c8",
    "results/phase3/metrics.json": "bc81ddaf9f0f02ba18108219bab1c43181bc642820540dfce3396c3e5bd6cb16",
    "results/phase3/raw_results.json": "dbff7ec0bfe04a5a2a154263e8577ce3a9806161b61200ec5593668e00ef1e09",
    "results/phase3/report.md": "9d3e1b329126b446883ac46356c2eae50c5d11baa0c23893fb78ca99851e3bee",
    "results/phase3/trajectories.json": "853b06339a6584fcfb148068311d06e6e2b3f71b302e9cbf451c74c95e021e4d",
    "results/phase4/metrics.json": "38ae3fd53dbc05296adf366d8823c133bac7fb02eaa59d65f62dab6f10664bb9",
    "results/phase4/raw_results.json": "d0082f1853f9d0606a198e1c462b1ae14477b4bde915afa7af6e69e046b82f83",
    "results/phase4/report.md": "4742057dedb475e1bb2b4b29c9dd31ff7d63ee6a51a524490511d8cab1d1af44",
    "results/phase4/usability.md": "6128a5dc2c685cddd6470e30be1b805f6907d546ff56d4962a8787bbd40e7b0d",
}
