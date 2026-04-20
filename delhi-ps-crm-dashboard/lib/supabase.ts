import { createClient, SupabaseClient } from "@supabase/supabase-js";

let supabase: SupabaseClient;
let connectionAttempts = 0;
const MAX_CONNECTION_ATTEMPTS = 3;
const CONNECTION_RETRY_DELAY = 1000; // ms

async function createSupabaseClient(): Promise<SupabaseClient> {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  
  if (!url || !key) {
    throw new Error("Missing Supabase configuration");
  }
  
  const client = createClient(url, key);
  
  // Test connection
  try {
    const { error } = await client.from("users").select("count").limit(1);
    if (error) {
      throw new Error(`Supabase connection test failed: ${error.message}`);
    }
    connectionAttempts = 0; // Reset on successful connection
    return client;
  } catch (error) {
    connectionAttempts++;
    console.error(`Supabase connection attempt ${connectionAttempts} failed:`, error);
    
    if (connectionAttempts >= MAX_CONNECTION_ATTEMPTS) {
      throw new Error("Failed to establish Supabase connection after maximum attempts");
    }
    
    // Exponential backoff
    const delay = CONNECTION_RETRY_DELAY * Math.pow(2, connectionAttempts - 1);
    await new Promise(resolve => setTimeout(resolve, delay));
    
    return createSupabaseClient(); // Retry
  }
}

// Initialize client with retry logic
supabase = await createSupabaseClient();

export { supabase };

// Health check function
export async function checkSupabaseHealth(): Promise<boolean> {
  try {
    const { error } = await supabase.from("users").select("count").limit(1);
    return !error;
  } catch (error) {
    console.error("Supabase health check failed:", error);
    return false;
  }
}
