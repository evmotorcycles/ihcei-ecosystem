# Minimal stub for IHCEI_kernel to allow the harness self-test to pass.
# The real kernel would perform actual D_enc * D_dec evaluation.

class _DummyResult:
    def __init__(self, D):
        self.D = D

class IHCEIKernel:
    def __init__(self, tier="enterprise"):
        self.tier = tier

    def evaluate(self, text, context=None):
        return _DummyResult(0.5)
