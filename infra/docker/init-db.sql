-- Create n8n database (separate from main app database for security isolation)
-- This script is mounted as /docker-entrypoint-initdb.d/init-db.sql
-- It runs on first Postgres container startup only
CREATE DATABASE n8n;