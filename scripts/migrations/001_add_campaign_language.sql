-- Migration: Add language field to campaigns table
-- Created: 2026-01-15
-- Description: Adds language column to support multilingual email generation

-- Add language column with default value 'en'
ALTER TABLE campaigns
ADD COLUMN IF NOT EXISTS language VARCHAR(10) NOT NULL DEFAULT 'en';

-- Add comment to document the column
COMMENT ON COLUMN campaigns.language IS 'Language for email generation (en or it)';
