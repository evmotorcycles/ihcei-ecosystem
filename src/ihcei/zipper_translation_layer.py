from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class GovernanceTruth:
    icon_name: str
    source_code_state: str # Al-Haqq
    moral_causality: str
    c_dev_impact: float

class DomainTranslator:
    """
    Translates secular data (Icons / As-Sidq) into Governance Truth (Source Code / Al-Haqq).
    """

    # Mapping Logic (Simplified for demonstration)
    METRIC_MAP = {
        "User Engagement": {
            "High": "Addiction/Slavery",
            "Low": "Disinterest",
            "Balanced": "Empowerment"
        },
        "Profit Margin": {
            "Excessive": "Hoarding/Riba",
            "Sustainable": "Zakat Flow",
            "Loss": "Waste"
        },
        "Click-Through Rate": {
            "Clickbait": "Deception/Ghurur",
            "Informative": "Guidance/Huda"
        }
    }

    def __init__(self):
        pass

    def al_3assr_extraction(self, metric_name: str, value: Any) -> GovernanceTruth:
        """
        Hacks the Interface: Extracts the "Source Code" state from the "Icon".
        Calculates Moral Causality and C_dev Impact.
        """

        source_code = "Unknown"
        moral_causality = "Neutral"
        c_dev_impact = 0.0

        if metric_name in self.METRIC_MAP:
            # Simple threshold logic (can be expanded)
            if metric_name == "User Engagement":
                if value > 80.0: # High engagement -> Addiction
                    source_code = self.METRIC_MAP[metric_name]["High"]
                    moral_causality = "Agency Reduction"
                    c_dev_impact = -50.0
                elif value < 20.0:
                    source_code = self.METRIC_MAP[metric_name]["Low"]
                    moral_causality = "Disconnection"
                    c_dev_impact = -10.0
                else:
                    source_code = self.METRIC_MAP[metric_name]["Balanced"]
                    moral_causality = "Agency Preservation"
                    c_dev_impact = 20.0

            elif metric_name == "Profit Margin":
                 if value > 0.4: # > 40% margin -> Riba
                    source_code = self.METRIC_MAP[metric_name]["Excessive"]
                    moral_causality = "Systemic Extraction"
                    c_dev_impact = -100.0
                 elif value > 0.0:
                    source_code = self.METRIC_MAP[metric_name]["Sustainable"]
                    moral_causality = "Resource Circulation"
                    c_dev_impact = 50.0
                 else:
                    source_code = self.METRIC_MAP[metric_name]["Loss"]
                    moral_causality = "Inefficiency"
                    c_dev_impact = -5.0

        return GovernanceTruth(
            icon_name=metric_name,
            source_code_state=source_code,
            moral_causality=moral_causality,
            c_dev_impact=c_dev_impact
        )
