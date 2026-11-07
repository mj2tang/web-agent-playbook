import { NextRequest } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";

describe("updateSession", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.resetModules();
  });

  it("lets requests through when Supabase isn't configured yet (fresh clone, before `make env`)", async () => {
    vi.stubEnv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY", "");
    const { updateSession } = await import("@/lib/supabase/proxy");
    const response = await updateSession(new NextRequest("http://localhost:3000/"));
    expect(response.status).toBe(200);
  });
});
