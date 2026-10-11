import { createBrowserClient } from "@supabase/ssr";

// Auth-aware browser client (persists session in cookies for SSR).
export function createSupabaseBrowser() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}
