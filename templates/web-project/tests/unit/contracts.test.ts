import { describe, expect, it } from "vitest";
import { Credentials, fieldErrors } from "@/lib/contracts/auth";
import { NOTE_MAX_LENGTH, NoteInput } from "@/lib/contracts/notes";

describe("NoteInput", () => {
  it("accepts and trims a normal note", () => {
    expect(NoteInput.parse({ body: "  buy milk  " })).toEqual({ body: "buy milk" });
  });

  it("rejects an empty or whitespace-only note", () => {
    const result = NoteInput.safeParse({ body: "   " });
    expect(result.success).toBe(false);
    if (!result.success) expect(fieldErrors(result.error).body).toBe("Write something first.");
  });

  it("matches the database limit of 2000 characters", () => {
    expect(NoteInput.safeParse({ body: "x".repeat(NOTE_MAX_LENGTH) }).success).toBe(true);
    expect(NoteInput.safeParse({ body: "x".repeat(NOTE_MAX_LENGTH + 1) }).success).toBe(false);
  });
});

describe("Credentials", () => {
  it("requires a valid email and an 8+ character password", () => {
    const result = Credentials.safeParse({ email: "nope", password: "short" });
    expect(result.success).toBe(false);
    if (!result.success) {
      const errors = fieldErrors(result.error);
      expect(errors.email).toBe("Enter a valid email address.");
      expect(errors.password).toBe("Use at least 8 characters.");
    }
  });
});
