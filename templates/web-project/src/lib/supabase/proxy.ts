import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";
import { supabaseKey, supabaseUrl } from "./env";

/** Refresh the auth session on every request so server code never sees an expired token. */
export async function updateSession(request: NextRequest) {
  let response = NextResponse.next({ request });
  // Not configured yet (fresh clone, before `make env`): public pages still render; pages that need the
  // database report the missing configuration themselves.
  if (!supabaseKey) return response;
  const supabase = createServerClient(supabaseUrl, supabaseKey, {
    cookies: {
      getAll() {
        return request.cookies.getAll();
      },
      setAll(cookiesToSet) {
        cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value));
        response = NextResponse.next({ request });
        cookiesToSet.forEach(({ name, value, options }) => response.cookies.set(name, value, options));
      },
    },
  });
  // Validates the JWT with the auth server and refreshes it if needed. Don't remove.
  await supabase.auth.getUser();
  return response;
}
