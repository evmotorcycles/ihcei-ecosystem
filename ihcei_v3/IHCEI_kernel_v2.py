"""v2.3 packaging shim — the deploy bundle ships the kernel as ihcei_kernel.py,
but ihcei_api.py (Novora Gateway) imports `IHCEI_kernel_v2`. Re-export here so
the gateway runs out of the box. No logic lives in this file."""
from ihcei_kernel import *            # noqa: F401,F403
from ihcei_kernel import IHCEIKernel, IHCEIVerdict, NetworkHealthReport  # noqa: F401
