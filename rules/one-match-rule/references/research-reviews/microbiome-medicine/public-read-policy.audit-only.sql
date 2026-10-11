-- Public, read-only site: anon may read published content + media.
alter table public.content_items enable row level security;
alter table public.media enable row level security;

drop policy if exists "public read published content" on public.content_items;
create policy "public read published content"
  on public.content_items for select
  using (status = 'publish');

drop policy if exists "public read media" on public.media;
create policy "public read media"
  on public.media for select
  using (true);
