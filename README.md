# Xsplittr

Xsplittr is a collaborative expense management application designed to simplify group expense tracking and settlements. It allows users to create groups, add participants, log shared expenses, and calculate settlements with ease.

---

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Acknowledgments](#acknowledgments)

---

## Features

- **Group Management**:
  - Create and delete groups for organizing expenses.
  - Add participants with unique nicknames to groups.

- **Expense Tracking**:
  - Log bills with details like title, amount, date, and split method (equal or percentage).
  - Support for custom split ratios and automatic calculations.

- **Settlement Calculation**:
  - View final settlements for each group.
  - Generate QR codes for settlement details, simplifying payments.

- **Interactive GUI**:
  - Intuitive interface built using PyQt5.

---

## Installation

### Prerequisites

- Python 3.7+
- Pip package manager

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/Olicat96/Xsplittr.git
   cd xsplittr
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database:

   ```bash
   python database.py
   ```

4. Run the application:

   ```bash
   python gui.py
   ```

---

## Usage

### Launching the App

Run the main GUI application:

```bash
python gui.py
```

### Key Functions

1. **Create a Group**:
   - Enter the group name and click "Create Group."

2. **Add Participants**:
   - Open the group, input participant details (first name, last name, and unique nickname), and click "Add Participant."

3. **Add a Bill**:
   - Choose the split method (equal or percentage) and input the bill details.

4. **View Settlements**:
   - Click "Finish Trip" to calculate settlements and generate QR codes for payments.

### Example

1. Create a group named `Vacation2023`.
2. Add participants `Alice`, `Bob`, and `Charlie`.
3. Add bills for shared expenses like hotel, food, and transportation.
4. View settlements and share QR codes for easy transactions.

---

## Acknowledgments

- **Inspiration**: Tools like Splitwise inspired this project.
- **Technologies**: Built using Python, PyQt5, and SQLite.
- **Contributors**: Special thanks to everyone who has contributed to the project.

---


