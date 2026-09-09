"""
fix_database.py

Locates your silambam.db (wherever Flask/SQLAlchemy actually put it)
and adds the new columns needed by the updated app.py, WITHOUT
deleting any existing data.

Run this from your project folder with your virtualenv active:

    py fix_database.py
"""

import os
import sqlite3


def find_database():
    """
    Search common locations for silambam.db, since Flask-SQLAlchemy
    stores relative sqlite paths inside an 'instance' folder by
    default, not the project root.
    """

    candidates = [
        "silambam.db",
        os.path.join("instance", "silambam.db"),
        os.path.join("..", "silambam.db"),
    ]

    # Also do a broader search from the current directory, in case
    # it's nested somewhere else entirely.
    for root, _dirs, files in os.walk("."):
        for f in files:
            if f == "silambam.db":
                candidates.append(os.path.join(root, f))

    seen = []
    for path in candidates:
        norm = os.path.normpath(path)
        if norm not in seen and os.path.isfile(norm):
            seen.append(norm)

    return seen


def add_column_if_missing(cursor, table, column, coltype):
    cursor.execute(f"PRAGMA table_info({table})")
    existing_columns = [row[1] for row in cursor.fetchall()]

    if column in existing_columns:
        print(f"  - {table}.{column} already exists, skipping.")
        return False

    cursor.execute(
        f"ALTER TABLE {table} ADD COLUMN {column} {coltype}"
    )
    print(f"  + Added {table}.{column} ({coltype})")
    return True


def migrate(db_path):
    print(f"\nMigrating: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check tables exist first
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    tables = [row[0] for row in cursor.fetchall()]

    if "achievement" in tables:
        add_column_if_missing(cursor, "achievement", "event", "VARCHAR(200)")
        add_column_if_missing(cursor, "achievement", "location", "VARCHAR(200)")
        add_column_if_missing(cursor, "achievement", "position", "VARCHAR(50)")
    else:
        print("  ! No 'achievement' table found yet (that's fine if you haven't used that feature).")

    if "fee" in tables:
        add_column_if_missing(cursor, "fee", "month", "VARCHAR(20)")
    else:
        print("  ! No 'fee' table found yet (that's fine if you haven't used that feature).")

    if "master" in tables:
        add_column_if_missing(cursor, "master", "latitude", "FLOAT")
        add_column_if_missing(cursor, "master", "longitude", "FLOAT")
    else:
        print("  ! No 'master' table found yet (that's fine if you haven't used that feature).")

    conn.commit()
    conn.close()

    print("Done.")


if __name__ == "__main__":

    found = find_database()

    if not found:
        print("Could not find silambam.db anywhere under the current folder.")
        print("Make sure you run this script from your project root")
        print("(the same folder where app.py lives), e.g.:")
        print()
        print("    cd D:\\silambam_attendance")
        print("    py fix_database.py")
        raise SystemExit(1)

    if len(found) > 1:
        print("Found multiple silambam.db files:")
        for i, path in enumerate(found):
            print(f"  [{i}] {path}")
        print("\nMigrating ALL of them to be safe.")

    for path in found:
        migrate(path)

    print("\nAll done! You can now restart your Flask app.")
