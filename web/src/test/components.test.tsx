import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ConfirmDialog } from "../components/ConfirmDialog";
import { roleFromSession } from "../auth/AuthProvider";
import { validateComplaint } from "../pages/customer/SubmitComplaintPage";
import type { Session } from "@supabase/supabase-js";

describe("complaint validation (mirrors backend ComplaintSubmit)", () => {
  it("rejects too-short, too-long and long product names", () => {
    expect(validateComplaint("short", "")).toMatch(/at least 10/);
    expect(validateComplaint("x".repeat(5001), "")).toMatch(/under 5000/);
    expect(validateComplaint("The app crashes every time I open it", "p".repeat(201))).toMatch(/Product/);
    expect(validateComplaint("The app crashes every time I open it", "Helpdesk")).toBeNull();
  });
});

describe("role from session", () => {
  const session = (app_metadata: Record<string, unknown>, user_metadata: Record<string, unknown> = {}) =>
    ({ user: { id: "u", email: "a@b.c", app_metadata, user_metadata } }) as unknown as Session;

  it("reads admin only from app_metadata, like the backend", () => {
    expect(roleFromSession(session({ role: "admin" }))).toBe("admin");
    expect(roleFromSession(session({}, { role: "admin" }))).toBe("customer"); // user-editable metadata is ignored
    expect(roleFromSession(null)).toBe("customer");
  });
});

describe("ConfirmDialog", () => {
  it("calls confirm and cancel, and is hidden when closed", async () => {
    const onConfirm = vi.fn();
    const onCancel = vi.fn();
    const { rerender } = render(
      <ConfirmDialog open title="Escalate case #1?" confirmLabel="Send" onConfirm={onConfirm} onCancel={onCancel}>
        <p>Body</p>
      </ConfirmDialog>,
    );
    await userEvent.click(screen.getByRole("button", { name: "Send" }));
    expect(onConfirm).toHaveBeenCalledOnce();
    await userEvent.keyboard("{Escape}");
    expect(onCancel).toHaveBeenCalledOnce();
    rerender(
      <ConfirmDialog open={false} title="x" confirmLabel="Send" onConfirm={onConfirm} onCancel={onCancel}>
        <p>Body</p>
      </ConfirmDialog>,
    );
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("disables both buttons while busy", () => {
    render(
      <ConfirmDialog open busy title="t" confirmLabel="Send" onConfirm={() => {}} onCancel={() => {}}>
        <p>Body</p>
      </ConfirmDialog>,
    );
    expect(screen.getByRole("button", { name: /Send/ })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Cancel" })).toBeDisabled();
  });
});
