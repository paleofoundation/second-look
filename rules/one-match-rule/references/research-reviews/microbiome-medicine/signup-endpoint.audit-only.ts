import { createClient } from "@supabase/supabase-js";

// Single signup endpoint for the "Join the Waitlist" form. Creates the account
// server-side and auto-confirms the email (using the service-role key) so the
// person can be signed in immediately — true "unlock everything" on submit.
// The selected bucket (clinician / researcher / int_ind) + all collected fields
// are stored in user_metadata so they're exportable and queryable.

const ROLES = new Set(["clinician", "researcher", "int_ind"]);
const PROFILE_FIELDS = [
  "name",
  "user_country",
  "user_interest_areas",
  // clinician
  "user_clinic",
  "user_medical_specialty",
  "user_license_id",
  "user_practice_country",
  // researcher
  "user_institution",
  "user_academic_role",
  "user_research_focus",
  "user_orchid_id",
  // interested individual
  "user_interest_reason",
];

export async function POST(req: Request) {
  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return Response.json({ error: "Invalid request." }, { status: 400 });
  }

  const email = String(body.email ?? "").trim().toLowerCase();
  const password = String(body.password ?? "");
  const role = ROLES.has(String(body.role)) ? String(body.role) : "int_ind";

  if (!email || !email.includes("@")) {
    return Response.json({ error: "A valid email address is required." }, { status: 400 });
  }
  if (password.length < 6) {
    return Response.json({ error: "Password must be at least 6 characters." }, { status: 400 });
  }

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !serviceKey) {
    return Response.json({ error: "Sign-up is temporarily unavailable." }, { status: 500 });
  }

  const admin = createClient(url, serviceKey, { auth: { persistSession: false } });

  const meta: Record<string, string> = { role };
  for (const f of PROFILE_FIELDS) {
    const v = body[f];
    if (v) meta[f] = String(v).slice(0, 500);
  }
  if (meta.name) meta.full_name = meta.name;

  const { error } = await admin.auth.admin.createUser({
    email,
    password,
    email_confirm: true,
    user_metadata: meta,
  });

  if (error) {
    const already = /registered|already|exists|duplicate/i.test(error.message);
    return Response.json(
      { error: already ? "That email is already registered — please log in instead." : error.message },
      { status: 400 }
    );
  }

  return Response.json({ ok: true });
}
