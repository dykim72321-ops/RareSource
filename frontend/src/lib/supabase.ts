import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://cheaaltkiwxwrpgyjwgp.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNoZWFhbHRraXd4d3JwZ3lqd2dwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY5MjA3ODgsImV4cCI6MjA4MjQ5Njc4OH0.PgUaKVFpOsEX5-ZkCZGhoC5VUWl6kCeTrHmIKecMFt0';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
