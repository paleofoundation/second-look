import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

// Auth-aware server client. cookies() is async in Next 16.
export async function createSupabaseServer() {
  const cookieStore = await cookies();
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            );
          } catch {
            // Called from a Server Component render — the proxy refreshes cookies.
          }
        },
      },
    }
  );
}

// Reliable server-side "is this reader signed in?" — reads the auth cookie the same way
// the dashboard/middleware do. Used to decide the cosmetic research-feed gate server-side,
// because the client can't read the (httpOnly) session cookie to unlock it itself.
export async function isLoggedIn(): Promise<boolean> {
  try {
    const supabase = await createSupabaseServer();
    const { data } = await supabase.auth.getUser();
    return !!data.user;
  } catch {
    return false;
  }
}
