import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function GET() {
  const supabase = await createClient();
  // RLS returns zero rows for anonymous callers; a successful query still proves the database answers.
  const { error } = await supabase.from("notes").select("id", { head: true, count: "exact" });
  if (error) {
    console.error(JSON.stringify({ event: "health", outcome: "db_error", code: error.code }));
    return NextResponse.json({ db: "error" }, { status: 503 });
  }
  return NextResponse.json({ db: "ok" });
}
