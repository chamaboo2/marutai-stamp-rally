-- まるたいスタンプラリー MVP / Supabase schema
-- Streamlit server uses SERVICE_ROLE_KEY. Never expose that key to browser-side code.

create extension if not exists pgcrypto;

create table if not exists public.facilities (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  category text not null check (category in ('sento','super_sento','spa','other')),
  ward text not null,
  address text not null,
  latitude double precision,
  longitude double precision,
  has_open_air_bath boolean not null default false,
  has_natural_hot_spring boolean not null default false,
  website_url text,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.visits (
  id uuid primary key default gen_random_uuid(),
  facility_id uuid not null references public.facilities(id) on delete cascade,
  visited_date date not null,
  original_photo_url text not null,
  stamped_photo_url text not null,
  created_at timestamptz not null default now()
);

create index if not exists facilities_active_ward_idx on public.facilities(active, ward);
create index if not exists visits_facility_date_idx on public.visits(facility_id, visited_date desc);

create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists facilities_set_updated_at on public.facilities;
create trigger facilities_set_updated_at
before update on public.facilities
for each row execute function public.set_updated_at();

-- Keep direct anonymous access closed for the family-only MVP.
alter table public.facilities enable row level security;
alter table public.visits enable row level security;

-- Private Storage bucket. Service role can access it from Streamlit server.
insert into storage.buckets (id, name, public)
values ('visit-photos', 'visit-photos', false)
on conflict (id) do update set public = false;
