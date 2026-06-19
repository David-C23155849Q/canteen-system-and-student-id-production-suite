# 🛡️ MTRC | Canteen Intelligence & ID Suite v2.2
**A Unified Ecosystem for Student Identification and Meal Security.**

The MTRC Suite is a dual-sided Django application designed to manage the full lifecycle of a student's campus identity—from ID card generation and barcode printing to secure canteen meal tracking.

---

## 🚀 Key Modules

### 1. Admin Control Center (The Registry)
* **ID Production Suite**: A dedicated platform to design and print student IDs directly from the browser.
* **Barcode/QR Generator**: Automatically generates unique, scannable identifiers for every new intake.
* **Data Analytics**: Critical analysis reports on student attendance, peak meal times, and session-based participation.

### 2. Canteen Operations (The Gatekeeper)
* **Scanner Integration**: Real-time barcode/QR scanning to verify student eligibility.
* **Anti-Cheat System**: Instant alerts and logic-gate blocking for "double-dipping" or unauthorized meal attempts.
* **Session Management**: Tracks breakfast, lunch, and dinner sessions to ensure 1-meal-per-student-per-session compliance.
* **Data Analytics**: Critical analysis reports on student attendance, peak meal times, and session-based participation.
* **Data Analytics**: Canteen staff session tracking.

---

## 🛠️ Technical Architecture

* **Backend**: Python / Django (Robust ORM for student records and meal logs).
* **Frontend**: HTML5, CSS3, Tailwind CSS (Modern, high-speed administrative UI).
* **Hardware Compatibility**: Integrated for standard ID Card Printers and USB/HID Barcode/QR Scanners.

---

## 📂 System Flow

### **Phase A: Enrollment & Printing**
1. Admin enters student data into the **Registry**.
2. System generates a unique identifier and encodes it into a **Barcode**.
3. Admin uses the **ID Production Suite** to print the physical card.

### **Phase B: Verification & Analytics**
1. Student scans ID at the **Canteen Station**.
2. **Anti-Cheat Engine** checks if the ID has already been scanned for the current session.
3. If valid, the meal is logged; if not, an **Alert** is triggered.
4. **Admin Side** pulls the data into a **Critical Analysis** dashboard to monitor canteen efficiency.

---

## 🖨️ PDF & Print Engine

The system uses a custom `@media print` CSS engine to ensure that ID cards and Registry Reports are formatted with pixel-perfection for standard CR80 (ID Card) and A4 paper sizes.

---

## 🛠️ Setup & Installation

1.  **Clone & Install Dependencies**:
    ```bash
    git clone https://github.com/Morgenster-Teachers-College-Official/Canteen-meal-tracking-system.git

    cd Canteen-meal-tracking-system

    python -m venv venv

    venv\Scripts\activate   # Windows

    pip install -r requirements.txt

    python manage.py createsuperuser
    ```
2.  **Database Migration**:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
3.  **Hardware Connection**:
    Connect your Barcode Scanner (HID Mode) and ensure your ID Printer is set as the default system printer for the `ID Production` view.
    ```
    This part in not necessary if you dont have the equipment yet, laptop (current device) webcam will do .
    ```

5.  **Run Server**:
    ```bash
    python qr_scanner.py
    python manage.py runserver
    ```

---

## 🔒 Security Features
* **Session-Locking**: Prevents the same barcode from being used twice in a 4-hour window.
* **Duplicate Detection**: Real-time monitoring of "cheat meals" via a live-updating admin feed.
* **Audit Trails**: Every meal served is timestamped and linked to a verified Student ID.

---

## ⚖️ License
Internal Use Only - Morgenster Teachers College © 2026
