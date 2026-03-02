-- QG-COS Layer 2 Database Architecture (MTN Uganda MoKash)
-- Translates raw telecom exhaust into the semantic extraction layer

-- Enable UUID extension for secure, distributed IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =========================================================================
-- TABLE 1: mokash_transaction_exhaust (The Data Plane / Layer 2 Ingestion)
-- Raw telecom exhaust, focusing on transactional behavior (U_efficiency)
-- =========================================================================
CREATE TABLE mokash_transaction_exhaust (
    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id VARCHAR(50) NOT NULL, -- e.g., hashed phone number or account ID
    interaction_timestamp TIMESTAMPTZ NOT NULL, -- Crucial for time_month aggregation
    transaction_type VARCHAR(50) NOT NULL, -- e.g., 'loan_request', 'repayment', 'balance_check'
    amount DECIMAL(15, 2),
    status VARCHAR(20) NOT NULL, -- e.g., 'success', 'failed', 'declined'
    metadata JSONB, -- Additional data (e.g., location, device, app version)
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Index for temporal aggregation and entity lookups
CREATE INDEX idx_mokash_tx_entity_time ON mokash_transaction_exhaust (entity_id, interaction_timestamp);

-- =========================================================================
-- TABLE 2: mokash_comms_ledger (The SMS Text / Layer 2 Ingestion)
-- Raw communications representing system/user interactions (D_audit / h_network extraction)
-- =========================================================================
CREATE TABLE mokash_comms_ledger (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id VARCHAR(50) NOT NULL,
    interaction_timestamp TIMESTAMPTZ NOT NULL,
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('inbound', 'outbound')),
    message_content TEXT NOT NULL, -- The unstructured data for Gemini extraction
    message_type VARCHAR(50), -- e.g., 'system_alert', 'customer_support', 'marketing'
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Index for temporal aggregation and entity lookups
CREATE INDEX idx_mokash_comms_entity_time ON mokash_comms_ledger (entity_id, interaction_timestamp);

-- =========================================================================
-- TABLE 3: nere_governance_telemetry (The Semantic Output / Layer 3 Ready for Layer 1 Regression)
-- The aggregated, orthogonal metric panel mapped to the ADGE crucible
-- =========================================================================
CREATE TABLE nere_governance_telemetry (
    telemetry_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id VARCHAR(50) NOT NULL,
    time_month DATE NOT NULL, -- Stored as the first day of the month for easy grouping

    -- Extracted NLP Metrics (Orthogonally scored by Gemini)
    d_audit_score NUMERIC(4, 3) CHECK (d_audit_score >= 0.0 AND d_audit_score <= 1.0),
    h_network_score NUMERIC(4, 3) CHECK (h_network_score >= 0.0 AND h_network_score <= 1.0),

    -- Quantitative Telemetry Metrics (Derived from transaction exhaust)
    u_efficiency NUMERIC(8, 4), -- Utility/Performance (e.g., repayment rate, activity score)
    c_dev NUMERIC(8, 4), -- Cognitive Capital / Capability (e.g., credit score growth, platform mastery)

    -- Falsification/Audit Trails
    extraction_trace JSONB, -- Stores the D_reasoning and h_reasoning from the LLM for Layer 6 verification

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    -- Ensure only one record per entity per month exists for the regression panel
    CONSTRAINT unique_entity_month UNIQUE (entity_id, time_month)
);

-- Index for rapid extraction into the pandas dataframe for the Layer 1 Regression
CREATE INDEX idx_nere_telemetry_regression ON nere_governance_telemetry (time_month, entity_id);
