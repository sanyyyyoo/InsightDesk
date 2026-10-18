import { ApiError, apiRequest, friendlyMessage, setTokenGetter } from "../api/client";
import { shouldRetry } from "../api/hooks";

function mockFetch(status: number, body: unknown) {
  return vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    statusText: "x",
    text: async () => (body === undefined ? "" : typeof body === "string" ? body : JSON.stringify(body)),
  });
}

describe("api client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    setTokenGetter(async () => null);
  });

  it("sends the bearer token and parses JSON", async () => {
    const fetch = mockFetch(200, { ok: 1 });
    vi.stubGlobal("fetch", fetch);
    setTokenGetter(async () => "tok123");
    await expect(apiRequest("/x")).resolves.toEqual({ ok: 1 });
    expect(fetch.mock.calls[0][1].headers.Authorization).toBe("Bearer tok123");
  });

  it("turns FastAPI error details into ApiError", async () => {
    vi.stubGlobal("fetch", mockFetch(400, { detail: "Case could not be escalated." }));
    await expect(apiRequest("/x", { method: "POST" })).rejects.toMatchObject({ status: 400, detail: "Case could not be escalated." });
  });

  it("joins FastAPI validation errors", async () => {
    vi.stubGlobal("fetch", mockFetch(422, { detail: [{ msg: "too short" }, { msg: "rating out of range" }] }));
    await expect(apiRequest("/analyze")).rejects.toMatchObject({ detail: "too short; rating out of range" });
  });

  it("maps network failures to status 0", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
    const err = (await apiRequest("/x").catch((e: unknown) => e)) as ApiError;
    expect(err).toBeInstanceOf(ApiError);
    expect(err.status).toBe(0);
    expect(friendlyMessage(err)).toMatch(/Cannot reach/);
  });

  it("retries only retryable errors, at most twice", () => {
    expect(shouldRetry(0, new ApiError(500, "boom"))).toBe(true);
    expect(shouldRetry(2, new ApiError(500, "boom"))).toBe(false);
    expect(shouldRetry(0, new ApiError(401, "no"))).toBe(false);
    expect(shouldRetry(0, new ApiError(404, "no"))).toBe(false);
  });
});
