-- schema.sql

CREATE TABLE crisis_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id VARCHAR(255) UNIQUE NOT NULL,
    raw_text TEXT NOT NULL,
    source VARCHAR(50),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    translated_english TEXT,
    location_extracted VARCHAR(255),
    situation_type VARCHAR(100),
    severity VARCHAR(50),
    confidence NUMERIC(3, 2),
    impact_details JSONB,
    status VARCHAR(50) DEFAULT 'Pending'
);

CREATE TABLE agent_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id VARCHAR(255) REFERENCES crisis_events(report_id),
    agent_name VARCHAR(100) NOT NULL,
    action_taken TEXT,
    payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE simulated_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id VARCHAR(255) REFERENCES crisis_events(report_id),
    recommended_actions JSONB,
    simulated_outcome JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
