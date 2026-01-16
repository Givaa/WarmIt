-- Migration: Add next_send_time field to campaigns and emails tables
-- Created: 2026-01-16
-- Description: Adds scheduling fields for random timing of emails throughout the day

-- Add next_send_time to campaigns
ALTER TABLE campaigns
ADD COLUMN IF NOT EXISTS next_send_time TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN campaigns.next_send_time IS 'Next scheduled time to send emails for this campaign';

-- Add scheduled_send_time to emails for reply timing
ALTER TABLE emails
ADD COLUMN IF NOT EXISTS scheduled_send_time TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN emails.scheduled_send_time IS 'Scheduled time to send this email (for delayed replies)';
