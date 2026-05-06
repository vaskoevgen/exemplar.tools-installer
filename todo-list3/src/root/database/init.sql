-- Idempotent database initialization script for task management application
-- CROSS-TIER-15: Safe to execute multiple times

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add CHECK constraint on status if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'tasks'::regclass
        AND contype = 'c'
        AND conname = 'tasks_status_check'
    ) THEN
        ALTER TABLE tasks ADD CONSTRAINT tasks_status_check
            CHECK (status IN ('pending', 'in_progress', 'done'));
    END IF;
END
$$;

-- Create or replace the trigger function for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    NEW.created_at = OLD.created_at;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger
        WHERE tgname = 'update_updated_at_column'
        AND tgrelid = 'tasks'::regclass
    ) THEN
        CREATE TRIGGER update_updated_at_column
            BEFORE UPDATE ON tasks
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
END
$$;
