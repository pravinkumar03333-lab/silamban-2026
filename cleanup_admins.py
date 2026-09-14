"""
cleanup_admins.py

One-time cleanup: deletes every Admin account EXCEPT the one whose
username matches ADMIN_USERNAME in your .env file.

Run this once from your project folder:

    py cleanup_admins.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Import your actual app and db/model definitions so this script
# uses the exact same database your app.py uses.
from app import app, db, Admin  # noqa: E402


def main():

    keep_username = os.environ.get("ADMIN_USERNAME", "admin")

    with app.app_context():

        all_admins = Admin.query.all()

        print(f"Found {len(all_admins)} admin account(s):")

        for admin in all_admins:
            print(f"  - {admin.username}")

        print(f"\nKeeping only: {keep_username}")

        removed = 0

        for admin in all_admins:

            if admin.username != keep_username:

                print(f"Deleting old admin account: {admin.username}")
                db.session.delete(admin)
                removed += 1

        db.session.commit()

        if removed == 0:
            print("\nNothing to remove — only one admin account exists already.")
        else:
            print(f"\nDone. Removed {removed} old admin account(s).")


if __name__ == "__main__":
    main()
