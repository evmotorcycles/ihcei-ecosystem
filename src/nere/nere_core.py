import re

class NERECore:
    """
    NERE (Neural Ethical Reasoning Engine) Core Logic.
    Responsible for auditing information against the Sovereign Operating System principles.
    """
    def __init__(self):
        # Iblees: Bias, Predilection, Ego, "I think", "Obviously"
        # Represents noise, bias, and potential corruption.
        self.iblees_markers = [
            "obviously", "clearly", "undoubtedly", "everyone knows",
            "i think", "i feel", "believe me", "stupid", "idiot",
            "biased", "prejudiced", "hate"
        ]

        # Corruption (Specific forms of Iblees/Negativity)
        self.corruption_markers = {
            "riba": ["interest", "usury", "unearned gain", "exploitation", "compound interest"],
            "shirk": ["absolute power", "unquestionable authority", "playing god", "sole owner"],
            "dhulm": ["oppression", "injustice", "unfair", "tyranny", "harm"]
        }

        # Nature Classifiers
        # Nar (Fire): Opinion, Volatile, Emotional, Subjective
        self.nar_markers = ["opinion", "seems", "possibly", "maybe", "guess", "feeling", "speculation"]
        # Ardh (Earth): Fact, Data, Solid, Verifiable
        self.ardh_markers = ["fact", "data", "evidence", "proven", "statistic", "record", "measurement", "verified"]
        # Ma' (Water): Guidance, Wisdom, Flow, Life-giving, Ethical
        self.ma_markers = ["wisdom", "guide", "principle", "ethics", "moral", "stewardship", "care", "responsibility", "justice"]

    def detect_iblees(self, content: str) -> dict:
        """
        Detects bias or 'Iblees' (diabolic/egoic) influence in the content.
        Returns a dictionary with score and details.
        """
        content_lower = content.lower()
        detected = []
        score = 0.0

        # Check for general bias markers
        for marker in self.iblees_markers:
            # Simple substring check (could be improved with regex for word boundaries)
            if marker in content_lower:
                detected.append(marker)
                score += 0.1

        # Check specific corruption types
        corruption_detected = {}
        for c_type, markers in self.corruption_markers.items():
            found = [m for m in markers if m in content_lower]
            if found:
                corruption_detected[c_type] = found
                score += 0.3 # Higher weight for corruption categories

        # Normalize score
        normalized_score = min(score, 1.0)

        return {
            "has_iblees": normalized_score > 0,
            "score": normalized_score,
            "markers": detected,
            "corruption": corruption_detected
        }

    def classify_nature(self, content: str) -> str:
        """
        Classifies content as Nar (Opinion), Ardh (Fact), or Ma' (Guidance).
        """
        content_lower = content.lower()

        nar_count = sum(1 for m in self.nar_markers if m in content_lower)
        ardh_count = sum(1 for m in self.ardh_markers if m in content_lower)
        ma_count = sum(1 for m in self.ma_markers if m in content_lower)

        counts = {"Ma'": ma_count, "Ardh": ardh_count, "Nar": nar_count}
        max_val = max(counts.values())

        if max_val == 0:
            return "Indeterminate"

        # Tie-breaking priority: Ma' > Ardh > Nar
        if counts["Ma'"] == max_val:
            return "Ma'"
        elif counts["Ardh"] == max_val:
            return "Ardh"
        else:
            return "Nar"

    def check_governance_alignment(self, content: str) -> dict:
        """
        Evaluates alignment with governance principles (10 Elements of Deen).
        """
        # 10 Elements of Deen
        elements = [
            "terminology", "roles", "dues", "authorities", "rules",
            "policies", "procedures", "actions", "domains", "exceptions"
        ]

        content_lower = content.lower()
        found_elements = [e for e in elements if e in content_lower]

        # Score based on how many elements are referenced or upheld
        alignment_score = len(found_elements) / 10.0

        return {
            "aligned": alignment_score > 0, # Strict check? Or just presence?
            "score": alignment_score,
            "elements_found": found_elements
        }

    def audit_decision(self, content: str, context: dict = None) -> dict:
        """
        The main audit function requested by the user.
        Evaluates the content and returns an audit decision and metadata.
        """
        iblees_check = self.detect_iblees(content)
        nature = self.classify_nature(content)
        alignment = self.check_governance_alignment(content)

        # Decision Logic
        approved = True
        messages = []

        # 1. Reject High Iblees/Corruption
        if iblees_check["score"] >= 0.5:
            approved = False
            messages.append("REJECT: High level of bias or corruption detected (Iblees > 0.5).")

        # 2. Check for Riba specifically
        if "riba" in iblees_check["corruption"]:
            approved = False
            messages.append("REJECT: Riba (usury/exploitation) detected.")

        # 3. Nature-based warnings
        if nature == "Nar":
            messages.append("WARNING: Content is classified as Nar (Opinion). Verify with Ardh (Fact).")
        elif nature == "Indeterminate":
             messages.append("NOTE: Content nature is indeterminate.")

        # 4. Governance Alignment
        if alignment["score"] < 0.1 and nature == "Ma'":
             # If it claims to be guidance but references no elements, is it valid?
             messages.append("WARNING: Guidance (Ma') detected but lacks explicit Governance Elements.")

        return {
            "decision": "APPROVED" if approved else "REJECTED",
            "messages": messages,
            "metrics": {
                "iblees_score": iblees_check["score"],
                "nature": nature,
                "governance_alignment_score": alignment["score"]
            },
            "details": {
                "iblees": iblees_check,
                "governance": alignment
            }
        }
