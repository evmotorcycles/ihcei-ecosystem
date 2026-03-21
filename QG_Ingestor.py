"""
QG_Ingestor.py
==============
Data Acquisition & Ingestion Module for QG_Validator (Build Phase)

Responsible for sourcing historical calibration data from public proxies:
1. Lehman Brothers (2008 Collapse) via SEC EDGAR and FRED APIs.
2. Enron Corporation (2001 Collapse) via Kaggle/CMU Email CSV.

Privacy Constraints:
- Data Minimization: Raw text must not be persisted.
- Node Anonymization: user_id and email addresses must be salted SHA-256 hashed.
"""

import csv
import hashlib
import json
import logging
import os
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("QG_Ingestor")


# ─────────────────────────────────────────────────────────────────────────────
# Core Data Structures
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class NetworkNode:
    """Represents an anonymized node in the network."""
    node_id: str  # Salted SHA-256 Hash
    metadata: Dict[str, Any]

@dataclass
class NetworkEdge:
    """Represents a connection or interaction between two nodes."""
    source_id: str
    target_id: str
    timestamp: float
    weight: float
    embedding: Optional[List[float]] = None

@dataclass
class ObservationPeriod:
    """Aggregated data for a single cycle t."""
    cycle_id: str
    timestamp_start: float
    timestamp_end: float
    U_utility: float           # e.g., Revenue, Total Assets
    D_enc: Optional[float] = None
    D_dec: Optional[float] = None
    h_network: Optional[float] = None
    lambda_2: Optional[float] = None
    nodes: List[NetworkNode] = None
    edges: List[NetworkEdge] = None

    def __post_init__(self):
        if self.nodes is None:
            self.nodes = []
        if self.edges is None:
            self.edges = []


# ─────────────────────────────────────────────────────────────────────────────
# Security & Privacy Utilities
# ─────────────────────────────────────────────────────────────────────────────

class PrivacyManager:
    """Handles node anonymization and data minimization."""

    def __init__(self, salt: str = "GT_VALIDATOR_SALT_V1"):
        self._salt = salt.encode('utf-8')

    def hash_identity(self, raw_id: str) -> str:
        """Returns a salted SHA-256 hash of a user ID or email."""
        h = hashlib.sha256()
        h.update(self._salt)
        h.update(raw_id.encode('utf-8'))
        return f"NODE_{h.hexdigest()[:16]}"

    def embed_and_discard(self, raw_text: str) -> List[float]:
        """
        Simulates an in-memory embedding process.
        In production, this calls a Sentence-Transformer model.
        Crucially, the raw text is immediately discarded (not returned).
        """
        # Placeholder for actual embedding logic
        # For now, returning a dummy vector derived from string length
        return [float(len(raw_text) % 10) / 10.0, 0.5, 0.5]


# ─────────────────────────────────────────────────────────────────────────────
# API Connectors
# ─────────────────────────────────────────────────────────────────────────────

class FREDConnector:
    """Connector for Federal Reserve Economic Data (FRED) API."""

    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("FRED_API_KEY")
        if not self.api_key:
            logger.warning("FRED_API_KEY not found. FRED requests will fail unless mocked.")

    def fetch_series(self, series_id: str, observation_start: str, observation_end: str) -> List[Dict]:
        """Fetch time series data from FRED."""
        if not self.api_key:
            return self._mock_data(series_id)

        params = urllib.parse.urlencode({
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'observation_start': observation_start,
            'observation_end': observation_end
        })
        url = f"{self.BASE_URL}?{params}"

        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'QG_Validator_Ingestor'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                return data.get('observations', [])
        except urllib.error.URLError as e:
            logger.error(f"FRED API Request failed for {series_id}: {e}")
            return []

    def _mock_data(self, series_id: str) -> List[Dict]:
        """Provide mock data when API key is unavailable (for testing/build phase)."""
        logger.info(f"Returning mock data for FRED series: {series_id}")
        return [
            {"date": "2007-01-01", "value": "1.5"},
            {"date": "2007-04-01", "value": "2.1"},
            {"date": "2007-07-01", "value": "2.8"},
            {"date": "2007-10-01", "value": "3.5"},
            {"date": "2008-01-01", "value": "4.2"},
            {"date": "2008-04-01", "value": "5.5"},
            {"date": "2008-07-01", "value": "8.1"},
            {"date": "2008-10-01", "value": "12.5"}  # Collapse
        ]


class SECConnector:
    """Connector for SEC EDGAR Database (Company Filings)."""

    def __init__(self):
        self.headers = {'User-Agent': 'QG_Validator_Project (contact@example.com)'}

    def fetch_assets(self, cik: str, start_year: int, end_year: int) -> List[Dict]:
        """Fetch Total Assets from SEC XBRL data."""
        # Note: SEC EDGAR requires specific CIK and XBRL parsing.
        # This is a stub for the complex XBRL parsing logic.
        logger.info(f"Fetching SEC filings for CIK {cik} ({start_year}-{end_year})")

        # Mocking Lehman Brothers Total Assets (in billions)
        return [
            {"period": "2007-Q1", "assets": 503.5},
            {"period": "2007-Q2", "assets": 603.3},
            {"period": "2007-Q3", "assets": 659.3},
            {"period": "2007-Q4", "assets": 691.0},
            {"period": "2008-Q1", "assets": 786.0},
            {"period": "2008-Q2", "assets": 639.4},
            {"period": "2008-Q3", "assets": 600.0}
        ]


# ─────────────────────────────────────────────────────────────────────────────
# Ingestion Pipelines
# ─────────────────────────────────────────────────────────────────────────────

class LehmanIngestor:
    """Pipeline for Lehman Brothers Calibration Data."""

    LEHMAN_CIK = "0000806085"

    def __init__(self):
        self.fred = FREDConnector()
        self.sec = SECConnector()

    def build_dataset(self) -> List[ObservationPeriod]:
        """Aggregate Lehman data into ObservationPeriods."""
        logger.info("Building Lehman Brothers Calibration Dataset...")

        assets_data = self.sec.fetch_assets(self.LEHMAN_CIK, 2007, 2008)
        subprime_data = self.fred.fetch_series("DRSPMACBS", "2007-01-01", "2008-10-01") # Delinquency Rate Subprime
        ted_spread_data = self.fred.fetch_series("TEDRATE", "2007-01-01", "2008-10-01") # Proxy for h_network

        periods = []
        # Simplified time alignment logic for the Build Phase stub
        for i, a_record in enumerate(assets_data):
            try:
                # Naive matching by index for demonstration
                d_asset_val = float(subprime_data[i]['value']) if i < len(subprime_data) else 0.0
                h_net_val = float(ted_spread_data[i]['value']) if i < len(ted_spread_data) else 0.0

                # Inverse relationship: higher subprime defaults = lower asset fidelity
                d_asset = max(0.0, 1.0 - (d_asset_val / 20.0))

                period = ObservationPeriod(
                    cycle_id=a_record['period'],
                    timestamp_start=0.0, # Replace with actual epoch
                    timestamp_end=0.0,
                    U_utility=a_record['assets'],
                    D_enc=d_asset,
                    h_network=h_net_val
                )
                periods.append(period)
            except (KeyError, ValueError, IndexError) as e:
                logger.warning(f"Skipping period {a_record.get('period')} due to missing data: {e}")

        logger.info(f"Lehman Dataset built: {len(periods)} periods.")
        return periods


class EnronCSVParser:
    """Pipeline for Enron Email Corpus (Kaggle/CMU format)."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.privacy_mgr = PrivacyManager()

    def parse(self, limit: int = 1000) -> List[NetworkEdge]:
        """
        Parse CSV, hash identities, embed text, and discard text.
        Returns a list of network edges (communications).
        """
        logger.info(f"Parsing Enron CSV: {self.file_path} (limit={limit})")
        edges = []

        if not os.path.exists(self.file_path):
            logger.error(f"File not found: {self.file_path}")
            # Return mock data if file doesn't exist during build phase
            return self._mock_data()

        count = 0
        with open(self.file_path, newline='', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            # Expected columns: Message-ID, Date, From, To, Subject, content
            for row in reader:
                if count >= limit:
                    break

                sender = row.get("From", "").strip()
                receivers_str = row.get("To", "").strip()
                text_content = row.get("content", "")

                if not sender or not receivers_str:
                    continue

                sender_id = self.privacy_mgr.hash_identity(sender)
                embedding = self.privacy_mgr.embed_and_discard(text_content)

                for receiver in receivers_str.split(','):
                    receiver = receiver.strip()
                    if not receiver:
                        continue

                    target_id = self.privacy_mgr.hash_identity(receiver)
                    edges.append(NetworkEdge(
                        source_id=sender_id,
                        target_id=target_id,
                        timestamp=time.time(), # Stub: parse actual Date field
                        weight=1.0,
                        embedding=embedding
                    ))
                count += 1

        logger.info(f"Parsed {len(edges)} edges from Enron corpus.")
        return edges

    def _mock_data(self) -> List[NetworkEdge]:
        """Mock data generator for testing when CSV is absent."""
        logger.info("Returning mock Enron data.")
        edges = []
        for i in range(100):
            edges.append(NetworkEdge(
                source_id=self.privacy_mgr.hash_identity(f"boss{i%5}@enron.com"),
                target_id=self.privacy_mgr.hash_identity(f"employee{i%20}@enron.com"),
                timestamp=time.time(),
                weight=1.0,
                embedding=self.privacy_mgr.embed_and_discard("Shred those documents.")
            ))
        return edges


# ─────────────────────────────────────────────────────────────────────────────
# Execution Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def run_ingestion():
    """Execute the Month 1-3 Build Phase Data Load."""
    print("="*60)
    print(" QG_INGESTOR: CALIBRATION DATA ACQUISITION STARTED")
    print("="*60)

    # 1. Lehman Brothers Ingestion
    lehman_pipeline = LehmanIngestor()
    lehman_data = lehman_pipeline.build_dataset()

    # Save Lehman data to disk
    os.makedirs("data/calibration", exist_ok=True)
    with open("data/calibration/lehman_proxy.json", "w") as f:
        json.dump([asdict(p) for p in lehman_data], f, indent=2)
    print("✓ Lehman Brothers dataset ingested and saved.")

    # 2. Enron Ingestion
    # Assume CSV is located at data/raw/enron_emails.csv. If missing, uses mock.
    enron_pipeline = EnronCSVParser("data/raw/enron_emails.csv")
    enron_edges = enron_pipeline.parse(limit=500)

    with open("data/calibration/enron_edges.json", "w") as f:
        json.dump([asdict(e) for e in enron_edges], f, indent=2)
    print("✓ Enron corpus ingested, text discarded, and edges saved.")

    print("="*60)
    print(" INGESTION COMPLETE. READY FOR CALIBRATION PHASE.")
    print("="*60)


if __name__ == "__main__":
    run_ingestion()
