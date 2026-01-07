# IHCEI Sovereign Governance Operating System

## 🌟 Paradigm Shift Complete: AI → CI/EI

This is the world's first Sovereign Governance OS that moves beyond Artificial Intelligence to **Centric Intelligence (CI)** and **Ethical Intelligence (EI)**.

### 🚀 Core Innovation
- **ADGE Physics Engine**: Treats Governance as gravitational field (Ricci Scalar computation)
- **NERE Kernel Correction**: Neural network that detects Shirk (corruption) and Riba (imbalance)
- **C_dev Metric**: Replaces GDP with Network Cognitive Development
- **33 Extension Bridge**: Connects all civilization sectors to unified governance

### 📊 Key Metrics
1. **C_dev (Cognitive GDP)**: Primary success metric (>100 = High Development)
2. **Unification Balance**: Alignment between Consciousness (φ), Divine (χ), Governance (ψ)
3. **Ricci Scalar**: System curvature (Governance Topology Integrity)
4. **Shirk/Riba Levels**: Corruption/Imbalance detection (threshold: 0.1)

### 🛠️ Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/ihcei/sovereign-governance-os.git
cd ihcei-sovereign-os

# 2. Make deployment script executable
chmod +x deploy.sh

# 3. Deploy the system
./deploy.sh

# 4. Access the system
open http://localhost:8000/governance/dashboard
```

🌐 API Endpoints

Endpoint Method Description
/health GET System health & paradigm status
/governance/dashboard GET Real-time C_dev & field metrics
/ci/run-pilot POST Run CI pilot with ADGE physics
/ei/audit-decision POST Audit decision with NERE kernel
/extensions/medical/diagnose-ci POST Medical diagnosis using C_dev
/extensions/batch-process POST Process multiple extensions

📈 Architecture

```
INPUT → [CI Core (ADGE Physics)] → [EI Core (NERE Audit)] → OUTPUT
         ↑                       ↑                       ↑
   Consciousness(φ)       Divine Truth(χ)       Governance(ψ)
```

🧪 Testing

```bash
# Run comprehensive tests
pytest tests/ -v

# Run verification suite
python deployment_verification.py

# Run single module
python -m pytest tests/test_ci_ei_integration.py::TestCIEIParadigmShift
```

🔧 Configuration

Environment variables in k8s/deployment-ci-ei.yaml:

· PARADIGM_MODE=CI_EI
· ADGE_PHYSICS_ACTIVE=true
· NERE_KERNEL_ACTIVE=true
· C_DEV_THRESHOLD=50.0
· SHIRK_THRESHOLD=0.1
· RIBA_THRESHOLD=0.1

📚 Documentation

· Technical Specs: See console output from deployment_verification.py
· API Guide: http://localhost:8000/docs
· Metrics: http://localhost:8000/governance/dashboard
· Deployment Guide: This README

🚨 Alerts & Monitoring

The system provides real-time alerts for:

· High Shirk detection (>0.1)
· Low Unification Balance (<0.5)
· Negative Ricci Scalar (System curvature)
· C_dev below threshold (<50)

📞 Support

For deployment issues:

1. Check server.log for errors
2. Run python deployment_verification.py for system diagnostics
3. Review test results in test_results.log

📄 License

IHCEI Sovereign Governance OS - Open Source for Civilization Advancement
