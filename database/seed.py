"""
Database Seed Module for Mailroom Management Application.

This module contains all the seed data for the database.
Data is based on professor's SQL scripts from sql-scripts.md.

IMPORTANT: wt_email is set to your WT email for testing notifications!
"""

from datetime import datetime, timedelta
from database.connection import get_connection

# ============================================================
# CONFIGURATION - Change this to your actual WT email
# ============================================================
wt_email = "jtorres8@buffs.wtamu.edu"


def seed_residents():
    """
    Seed Residents table with professor's exact data.
    All 100 residents from sql-scripts.md.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM Residents")
    if cursor.fetchone()[0] > 0:
        print("[INFO] Residents table already has data, skipping seed.")
        conn.close()
        return

    # Professor's exact resident data (100 residents)
    residents_data = [
        (1, 'Kittie Mousdall', wt_email, 101),
        (2, 'Claudette Rait', wt_email, 102),
        (3, 'Eliza Himsworth', wt_email, 103),
        (4, 'Emmit Gann', wt_email, 104),
        (5, 'Aurlie Pedycan', wt_email, 105),
        (6, 'Keriann Kettlesting', wt_email, 106),
        (7, 'Fiorenze Iacovuzzi', wt_email, 107),
        (8, 'Darlene Gravie', wt_email, 108),
        (9, 'Tomasine Challener', wt_email, 109),
        (10, 'Dotti Marple', wt_email, 110),
        (11, 'Gabriel Tofanelli', wt_email, 201),
        (12, 'Aldo Welldrake', wt_email, 202),
        (13, 'Ezmeralda Laydon', wt_email, 203),
        (14, 'Kale Lendrem', wt_email, 204),
        (15, 'Lenard Cubbit', wt_email, 205),
        (16, 'Dedie Caddies', wt_email, 206),
        (17, 'Nancy Janosevic', wt_email, 207),
        (18, 'Layne Whiterod', wt_email, 208),
        (19, 'Averell Labusch', wt_email, 209),
        (20, 'Gordan Raddon', wt_email, 210),
        (21, 'Deloria Johnes', wt_email, 301),
        (22, 'Emmett MacIllrick', wt_email, 302),
        (23, 'Sanderson Simoncelli', wt_email, 303),
        (24, 'Had Hapke', wt_email, 304),
        (25, 'Bellina Rodenburgh', wt_email, 305),
        (26, 'Portie Searle', wt_email, 306),
        (27, 'Ellsworth Richichi', wt_email, 307),
        (28, 'Orlando Mattholie', wt_email, 308),
        (29, 'Noby Phelp', wt_email, 309),
        (30, 'Wilow Caush', wt_email, 310),
        (31, 'Hesther Wincom', wt_email, 401),
        (32, 'Ferdie Jzhakov', wt_email, 402),
        (33, 'Cornelia Burlingham', wt_email, 403),
        (34, 'Rochella Childers', wt_email, 404),
        (35, 'Jennie Christensen', wt_email, 405),
        (36, 'Kalie Cropper', wt_email, 406),
        (37, 'Corinne Garrison', wt_email, 407),
        (38, 'Maybelle Pigne', wt_email, 408),
        (39, 'Wald Kuddyhy', wt_email, 409),
        (40, 'Blancha Ambrosoni', wt_email, 410),
        (41, 'Gussy Moiser', wt_email, 501),
        (42, 'Margette Symcock', wt_email, 502),
        (43, 'Cad Stearnes', wt_email, 503),
        (44, 'Juliann Sumner', wt_email, 504),
        (45, 'Esdras Bresland', wt_email, 505),
        (46, 'Alisha Laspee', wt_email, 506),
        (47, 'Yvon Jirusek', wt_email, 507),
        (48, 'Parrnell Halbeard', wt_email, 508),
        (49, 'Korrie Milesap', wt_email, 509),
        (50, 'Vivyan Petzold', wt_email, 510),
        (51, 'Angie Darben', wt_email, 101),
        (52, 'Eachelle Texton', wt_email, 102),
        (53, 'Lion Imlaw', wt_email, 103),
        (54, 'Delmore Cowhig', wt_email, 104),
        (55, 'Shaine Van Kruis', wt_email, 105),
        (56, 'Yehudi Jones', wt_email, 106),
        (57, 'Hamlen Gerrad', wt_email, 107),
        (58, 'Elisabetta Francescozzi', wt_email, 108),
        (59, 'Gusti Chinn', wt_email, 109),
        (60, 'Candace Hurlston', wt_email, 110),
        (61, 'Odey Butter', wt_email, 201),
        (62, 'Viva Bolletti', wt_email, 202),
        (63, 'Tallie Jubert', wt_email, 203),
        (64, 'Mary Vearnals', wt_email, 204),
        (65, 'Lona Dunbavin', wt_email, 205),
        (66, 'Osmond Bamlett', wt_email, 206),
        (67, 'Nomi Sollom', wt_email, 207),
        (68, 'Hildy Campana', wt_email, 208),
        (69, 'Emmanuel Getcliffe', wt_email, 209),
        (70, 'Danette Danieli', wt_email, 210),
        (71, 'Jan Witt', wt_email, 301),
        (72, 'Woodie Kertess', wt_email, 302),
        (73, 'Corine Cleevely', wt_email, 303),
        (74, 'Inez Mew', wt_email, 304),
        (75, 'Kathie Odd', wt_email, 305),
        (76, 'Mitch Friedlos', wt_email, 306),
        (77, 'Bambi Gostick', wt_email, 307),
        (78, 'Mellicent Roiz', wt_email, 308),
        (79, 'Sukey Avon', wt_email, 309),
        (80, 'Janina Kernan', wt_email, 310),
        (81, 'Jaynell Pitfield', wt_email, 401),
        (82, 'Ricki Hoppner', wt_email, 402),
        (83, 'Rinaldo Stable', wt_email, 403),
        (84, 'Tessy Tabour', wt_email, 404),
        (85, 'Helen Ferencz', wt_email, 405),
        (86, 'Korney Shakelade', wt_email, 406),
        (87, 'Tulley Reiner', wt_email, 407),
        (88, 'Myrle Mersh', wt_email, 408),
        (89, 'Carina Nelthorp', wt_email, 409),
        (90, 'Monte Trahmel', wt_email, 410),
        (91, 'Nate Zavattero', wt_email, 501),
        (92, 'Neddy Bucky', wt_email, 502),
        (93, 'Allissa Collyns', wt_email, 503),
        (94, 'Brianna Ruberry', wt_email, 504),
        (95, 'Roxane Wellen', wt_email, 505),
        (96, 'Ashbey Keddy', wt_email, 506),
        (97, 'Elvin Mico', wt_email, 507),
        (98, 'Nicolas Hanratty', wt_email, 508),
        (99, 'Gary Jochens', wt_email, 509),
        (100, 'Alexina Tarbard', wt_email, 510),
    ]

    cursor.executemany(
        "INSERT INTO Residents (id, full_name, email, unit_number) VALUES (?, ?, ?, ?)",
        residents_data
    )
    conn.commit()
    conn.close()
    print(f"[OK] Seeded {len(residents_data)} residents with email: {wt_email}")


def seed_staff():
    """
    Seed StaffLogin table with professor's exact data.
    Credentials: alice/alice123, bob/bob123
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM StaffLogin")
    if cursor.fetchone()[0] > 0:
        print("[INFO] StaffLogin table already has data, skipping seed.")
        conn.close()
        return

    # Professor's exact staff accounts
    staff_accounts = [
        ('alice', 'alice123'),
        ('bob', 'bob123'),
    ]

    cursor.executemany(
        "INSERT INTO StaffLogin (staff_username, staff_password) VALUES (?, ?)",
        staff_accounts
    )
    conn.commit()
    conn.close()
    print(f"[OK] Seeded {len(staff_accounts)} staff accounts: alice/alice123, bob/bob123")


def seed_sample_packages():
    """
    Seed Packages table with sample data for demo purposes.
    Creates 10 pending + 5 picked up packages.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM Packages")
    if cursor.fetchone()[0] > 0:
        print("[INFO] Packages table already has data, skipping seed.")
        conn.close()
        return

    carriers = [ "Amazon", "DHL", "FedEx", "Walmart", "USPS", "UPS",]
    packages = []
    today = datetime.now()

    # 10 pending packages
    for i in range(10):
        resident_id = i + 1
        carrier = carriers[i % len(carriers)]
        delivery_date = (today - timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S")
        packages.append((resident_id, carrier, delivery_date, "Pending"))

    # 5 picked up packages
    for i in range(5):
        resident_id = i + 11
        carrier = carriers[i % len(carriers)]
        delivery_date = (today - timedelta(days=i + 5)).strftime("%Y-%m-%d %H:%M:%S")
        packages.append((resident_id, carrier, delivery_date, "PickedUp"))

    cursor.executemany(
        "INSERT INTO Packages (resident_id, carrier, delivery_date, status) VALUES (?, ?, ?, ?)",
        packages
    )
    conn.commit()
    conn.close()
    print(f"[OK] Seeded {len(packages)} sample packages (10 pending, 5 picked up)")


def seed_sample_unknown_packages():
    """
    Seed UnknownPackages table with sample data for demo purposes.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM UnknownPackages")
    if cursor.fetchone()[0] > 0:
        print("[INFO] UnknownPackages table already has data, skipping seed.")
        conn.close()
        return

    unknown_packages = [
        ("J. Doe", "USPS", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ("Mike S.", "UPS", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ("A. Johnson", "FedEx", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    ]

    cursor.executemany(
        "INSERT INTO UnknownPackages (name_on_label, carrier, delivery_date) VALUES (?, ?, ?)",
        unknown_packages
    )
    conn.commit()
    conn.close()
    print(f"[OK] Seeded {len(unknown_packages)} sample unknown packages")


def seed_all():
    """
    Seed all tables with initial data.
    """
    seed_residents()
    seed_staff()
    seed_sample_packages()
    seed_sample_unknown_packages()


if __name__ == "__main__":
    seed_all()
