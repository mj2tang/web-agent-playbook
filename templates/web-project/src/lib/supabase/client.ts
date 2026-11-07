import { createBrowserClient } from "@supabase/ssr";
import type { Database } from "@/lib/database.types";
import { supabaseKey, supabaseUrl } from "./env";

/** Supabase client for client components. Uses the publishable key; RLS decides what the user can see. */
export function createClient() {
  return createBrowserClient<Database>(supabaseUrl, supabaseKey);
}
