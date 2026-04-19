"""One-time migration script -- adds missing columns to raw_complaints table."""

from config import supabase

COLUMNS = {
    "rating": "ALTER TABLE raw_complaints ADD COLUMN IF NOT EXISTS rating INTEGER;",
    "raw_message": "ALTER TABLE raw_complaints ADD COLUMN IF NOT EXISTS raw_message TEXT;",
    "ward": "ALTER TABLE raw_complaints ADD COLUMN IF NOT EXISTS ward TEXT;",
    "categories": "ALTER TABLE raw_complaints ADD COLUMN IF NOT EXISTS categories TEXT[];",
}


def check_column_exists(col_name: str) -> bool:
    """Check if a column exists by trying to select it."""
    try:
        supabase.table("raw_complaints").select(col_name).limit(1).execute()
        return True
    except Exception:
        return False


def try_rpc_migration(sql: str) -> bool:
    """Try executing SQL via an exec_sql RPC function if it exists."""
    try:
        supabase.rpc("exec_sql", {"query": sql}).execute()
        return True
    except Exception:
        return False


def main():
    print("=" * 55)
    print("  Delhi PS-CRM -- Database Migration")
    print("=" * 55)
    print()

    missing = []
    for col_name, sql in COLUMNS.items():
        exists = check_column_exists(col_name)
        if exists:
            print(f"  [OK] '{col_name}' -- already exists")
        else:
            missing.append((col_name, sql))
            print(f"  [--] '{col_name}' -- MISSING, will attempt to add")

    if not missing:
        print("\n  All columns present. No migration needed.")
        return

    print(f"\n  Attempting to add {len(missing)} missing column(s)...\n")
    manual_needed = []
    for col_name, sql in missing:
        ok = try_rpc_migration(sql)
        if ok:
            print(f"  [OK] '{col_name}' -- added successfully via RPC")
        else:
            manual_needed.append((col_name, sql))
            print(f"  [!!] '{col_name}' -- RPC failed")

    if manual_needed:
        print("\n  The following SQL must be run manually in")
        print("  Supabase Dashboard > SQL Editor > New Query:\n")
        print("  " + "-" * 50)
        for _, sql in manual_needed:
            print(f"  {sql}")
        print("  " + "-" * 50)
    else:
        print("\n  All migrations applied successfully!")


if __name__ == "__main__":
    main()
