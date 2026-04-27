# TSIS1 PhoneBook
import csv
import json
import os
from connect import get_connection


def print_rows(rows):
    if not rows:
        print("No contacts found.")
        return

    print("\nContacts:")
    for row in rows:
        print("-" * 60)
        print(f"ID: {row[0]}")
        print(f"Name: {row[1]}")
        print(f"Email: {row[2]}")
        print(f"Birthday: {row[3]}")
        print(f"Group: {row[4]}")
        print(f"Phones: {row[5]}")
        print(f"Created at: {row[6]}")
    print("-" * 60)


def run_sql_file(filename):
    if not os.path.exists(filename):
        print(f"{filename} not found.")
        return

    with open(filename, "r", encoding="utf-8") as file:
        sql = file.read()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(sql)
    conn.commit()

    cur.close()
    conn.close()

    print(f"{filename} executed successfully.")


def setup_database():
    print("WARNING: schema.sql will recreate tables and delete old data.")
    answer = input("Continue? yes/no: ").strip().lower()

    if answer != "yes":
        print("Cancelled.")
        return

    run_sql_file("schema.sql")
    run_sql_file("procedures.sql")


def add_contact():
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    birthday = input("Birthday YYYY-MM-DD, or empty: ").strip()
    group_name = input("Group Family/Work/Friend/Other: ").strip()

    if not name:
        print("Name cannot be empty.")
        return

    if email == "":
        email = None

    if birthday == "":
        birthday = None

    if group_name == "":
        group_name = "Other"

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "CALL add_contact(%s, %s, %s, %s)",
        (name, email, birthday, group_name)
    )

    conn.commit()
    cur.close()
    conn.close()

    print("Contact added/updated.")

    add_phone_answer = input("Add phone now? yes/no: ").strip().lower()
    if add_phone_answer == "yes":
        phone = input("Phone: ").strip()
        phone_type = input("Type home/work/mobile: ").strip().lower()

        if phone_type == "":
            phone_type = "mobile"

        add_phone_to_contact(name, phone, phone_type)


def add_phone_to_contact(name, phone, phone_type):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "CALL add_phone(%s, %s, %s)",
            (name, phone, phone_type)
        )
        conn.commit()
        print("Phone added.")
    except Exception as error:
        conn.rollback()
        print("Error:", error)

    cur.close()
    conn.close()


def add_phone():
    name = input("Contact name: ").strip()
    phone = input("Phone: ").strip()
    phone_type = input("Type home/work/mobile: ").strip().lower()

    if phone_type == "":
        phone_type = "mobile"

    add_phone_to_contact(name, phone, phone_type)


def move_to_group():
    name = input("Contact name: ").strip()
    group_name = input("New group Family/Work/Friend/Other: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "CALL move_to_group(%s, %s)",
            (name, group_name)
        )
        conn.commit()
        print("Contact moved to group.")
    except Exception as error:
        conn.rollback()
        print("Error:", error)

    cur.close()
    conn.close()


def search_contacts():
    query = input("Search by name/email/phone/group: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_contacts(%s)", (query,))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    print_rows(rows)


def get_contacts(limit_value, offset_value, sort_by, group_filter):
    allowed_sort = {
        "name": "LOWER(c.name) ASC",
        "birthday": "c.birthday ASC NULLS LAST",
        "date": "c.created_at DESC"
    }

    order_by = allowed_sort.get(sort_by, "LOWER(c.name) ASC")

    if group_filter:
        where_clause = "WHERE LOWER(g.name) = LOWER(%s)"
        params = (group_filter, limit_value, offset_value)
    else:
        where_clause = ""
        params = (limit_value, offset_value)

    query = f"""
        SELECT
            c.id,
            c.name,
            c.email,
            c.birthday,
            g.name AS group_name,
            COALESCE(
                STRING_AGG(p.phone || ' (' || p.type || ')', ', '),
                ''
            ) AS phones,
            c.created_at
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        {where_clause}
        GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
        ORDER BY {order_by}
        LIMIT %s OFFSET %s;
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(query, params)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


def show_contacts_paginated():
    sort_by = input("Sort by name/birthday/date: ").strip().lower()
    group_filter = input("Filter by group, or empty: ").strip()

    limit_value = 5
    offset_value = 0

    while True:
        rows = get_contacts(limit_value, offset_value, sort_by, group_filter)
        print_rows(rows)

        command = input("next / prev / quit: ").strip().lower()

        if command == "next":
            offset_value += limit_value

        elif command == "prev":
            offset_value -= limit_value
            if offset_value < 0:
                offset_value = 0

        elif command == "quit":
            break

        else:
            print("Invalid command.")


def delete_contact():
    delete_by = input("Delete by name or phone? ").strip().lower()

    conn = get_connection()
    cur = conn.cursor()

    try:
        if delete_by == "name":
            name = input("Name: ").strip()
            cur.execute("CALL delete_contact_proc(%s, %s)", (name, None))

        elif delete_by == "phone":
            phone = input("Phone: ").strip()
            cur.execute("CALL delete_contact_proc(%s, %s)", (None, phone))

        else:
            print("Invalid option.")
            cur.close()
            conn.close()
            return

        conn.commit()
        print("Delete completed.")

    except Exception as error:
        conn.rollback()
        print("Error:", error)

    cur.close()
    conn.close()


def contact_exists(name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
    result = cur.fetchone()

    cur.close()
    conn.close()

    return result is not None


def overwrite_contact(name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL delete_contact_proc(%s, %s)", (name, None))

    conn.commit()
    cur.close()
    conn.close()


def import_contacts_from_csv():
    filename = input("CSV filename, for example contacts.csv: ").strip()

    if not os.path.exists(filename):
        print("File not found.")
        return

    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            name = row.get("name") or row.get("username") or row.get("Username")
            phone = row.get("phone") or row.get("Phone")
            email = row.get("email") or None
            birthday = row.get("birthday") or None
            group_name = row.get("group") or row.get("group_name") or "Other"
            phone_type = row.get("type") or "mobile"

            if not name:
                continue

            if contact_exists(name):
                choice = input(f"{name} already exists. skip/overwrite: ").strip().lower()

                if choice == "skip":
                    continue

                elif choice == "overwrite":
                    overwrite_contact(name)

                else:
                    print("Skipped.")
                    continue

            conn = get_connection()
            cur = conn.cursor()

            cur.execute(
                "CALL add_contact(%s, %s, %s, %s)",
                (name, email, birthday, group_name)
            )

            conn.commit()
            cur.close()
            conn.close()

            if phone:
                add_phone_to_contact(name, phone, phone_type)

    print("CSV import completed.")


def get_all_contacts_for_export():
    query = """
        SELECT
            c.id,
            c.name,
            c.email,
            c.birthday,
            g.name AS group_name,
            c.created_at
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY c.name;
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(query)
    contacts = cur.fetchall()

    data = []

    for contact in contacts:
        contact_id = contact[0]

        cur.execute(
            "SELECT phone, type FROM phones WHERE contact_id = %s",
            (contact_id,)
        )
        phones = cur.fetchall()

        data.append({
            "id": contact[0],
            "name": contact[1],
            "email": contact[2],
            "birthday": str(contact[3]) if contact[3] else None,
            "group_name": contact[4],
            "created_at": str(contact[5]),
            "phones": [
                {
                    "phone": phone[0],
                    "type": phone[1]
                }
                for phone in phones
            ]
        })

    cur.close()
    conn.close()

    return data


def export_contacts_to_json():
    filename = input("JSON filename, for example contacts.json: ").strip()

    if filename == "":
        filename = "contacts.json"

    data = get_all_contacts_for_export()

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"Export completed: {filename}")


def import_contacts_from_json():
    filename = input("JSON filename, for example contacts.json: ").strip()

    if not os.path.exists(filename):
        print("File not found.")
        return

    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    for item in data:
        name = item.get("name")
        email = item.get("email")
        birthday = item.get("birthday")
        group_name = item.get("group_name") or "Other"
        phones = item.get("phones", [])

        if not name:
            continue

        if contact_exists(name):
            choice = input(f"{name} already exists. skip/overwrite: ").strip().lower()

            if choice == "skip":
                continue

            elif choice == "overwrite":
                overwrite_contact(name)

            else:
                print("Skipped.")
                continue

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "CALL add_contact(%s, %s, %s, %s)",
            (name, email, birthday, group_name)
        )

        conn.commit()
        cur.close()
        conn.close()

        for phone_item in phones:
            phone = phone_item.get("phone")
            phone_type = phone_item.get("type") or "mobile"

            if phone:
                add_phone_to_contact(name, phone, phone_type)

    print("JSON import completed.")


def menu():
    while True:
        print("\n--- TSIS1 PHONEBOOK MENU ---")
        print("1. Setup database")
        print("2. Add contact")
        print("3. Add phone to contact")
        print("4. Move contact to group")
        print("5. Search contacts")
        print("6. Show contacts with pagination")
        print("7. Import contacts from CSV")
        print("8. Export contacts to JSON")
        print("9. Import contacts from JSON")
        print("10. Delete contact")
        print("0. Exit")

        choice = input("Choose option: ").strip()

        if choice == "1":
            setup_database()
        elif choice == "2":
            add_contact()
        elif choice == "3":
            add_phone()
        elif choice == "4":
            move_to_group()
        elif choice == "5":
            search_contacts()
        elif choice == "6":
            show_contacts_paginated()
        elif choice == "7":
            import_contacts_from_csv()
        elif choice == "8":
            export_contacts_to_json()
        elif choice == "9":
            import_contacts_from_json()
        elif choice == "10":
            delete_contact()
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    menu()