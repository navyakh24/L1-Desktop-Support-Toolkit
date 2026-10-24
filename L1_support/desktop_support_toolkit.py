
import platform
import socket
import subprocess
import csv
import shutil
from datetime import datetime
from pathlib import Path

REPORT_DIR = Path("reports")


def run_command(command):
    """Run a Windows diagnostic command safely."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=15,
            shell=False
        )
        output = result.stdout.strip()

        if result.stderr.strip():
            output += "\n" + result.stderr.strip()

        if not output:
            output = "No output returned."

        return output

    except subprocess.TimeoutExpired:
        return "The command timed out."
    except OSError as error:
        return f"Unable to run command: {error}"


def system_information():
    print("\n--- SYSTEM INFORMATION ---")
    print("Computer name:", platform.node())
    print("Operating system:", platform.system())
    print("Windows version:", platform.version())
    print("Processor:", platform.processor())


def network_configuration():
    print("\n--- NETWORK CONFIGURATION ---")
    print(run_command(["ipconfig", "/all"]))


def internet_connectivity():
    print("\n--- INTERNET CONNECTIVITY ---")

    print("\nChecking connectivity to 8.8.8.8...")
    print(run_command(["ping", "-n", "4", "-w", "2000", "8.8.8.8"]))

    print("\nChecking DNS and hostname connectivity...")
    print(run_command(["ping", "-n", "4", "-w", "2000", "google.com"]))


def dns_lookup():
    print("\n--- DNS LOOKUP ---")
    hostname = input("Enter a hostname (e.g., google.com): ").strip()

    if not hostname or any(c.isspace() for c in hostname):
        print("Please enter a valid hostname.")
        return

    try:
        addresses = socket.getaddrinfo(hostname, None)
        unique_ips = sorted({item[4][0] for item in addresses})
        print("Resolved IP addresses:")
        for ip in unique_ips:
            print("-", ip)
    except socket.gaierror:
        print("DNS lookup failed. Check the hostname and DNS connection.")


def disk_space():
    print("\n--- DISK SPACE ---")
    try:
        usage = shutil.disk_usage("C:\\")
        total_gb = usage.total / (1024 ** 3)
        free_gb = usage.free / (1024 ** 3)
        used_gb = total_gb - free_gb

        print(f"Total space: {total_gb:.2f} GB")
        print(f"Used space: {used_gb:.2f} GB")
        print(f"Free space: {free_gb:.2f} GB")

        if total_gb and (usage.free / usage.total) < 0.10:
            print("Warning: Less than 10% of disk space is free.")
    except OSError as error:
        print("Unable to check disk space:", error)


def save_report():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    report = [
        "L1 DESKTOP SUPPORT TROUBLESHOOTING REPORT",
        f"Date and time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Computer: {platform.node()}",
        f"Operating system: {platform.platform()}",
        "",
        "NETWORK CONFIGURATION",
        run_command(["ipconfig"]),
        "",
        "CONNECTIVITY TEST: 8.8.8.8",
        run_command(["ping", "-n", "4", "-w", "2000", "8.8.8.8"]),
        "",
        "DNS LOOKUP TEST: google.com",
        run_command(["nslookup", "google.com"]),
        "",
        "DISK SPACE",
    ]

    try:
        usage = shutil.disk_usage("C:\\")
        report.extend([
            f"Total: {usage.total / (1024 ** 3):.2f} GB",
            f"Free: {usage.free / (1024 ** 3):.2f} GB",
        ])
    except OSError as error:
        report.append(f"Disk check failed: {error}")

    filename = REPORT_DIR / (
        f"support_report_{datetime.now():%Y%m%d_%H%M%S}.txt"
    )

    try:
        filename.write_text("\n".join(report), encoding="utf-8")
        print(f"\nReport saved to: {filename}")
    except OSError as error:
        print("Unable to save report:", error)


def troubleshooting_guide():
    print("\n--- L1 TROUBLESHOOTING GUIDE ---")
    print("1. Internet not working")
    print("2. Computer running slowly")
    print("3. Low disk space")
    print("4. DNS issue")

    choice = input("Select an issue (1-4): ").strip()

    guides = {
        "1": [
            "Check Wi-Fi or Ethernet connection.",
            "Run ipconfig and inspect the IP address.",
            "Check the default gateway.",
            "Test connectivity with ping.",
            "Document findings and escalate if unresolved."
        ],
        "2": [
            "Ask when the issue started.",
            "Check Task Manager for high CPU or memory use.",
            "Check available disk space.",
            "Close unnecessary applications if appropriate.",
            "Record findings and escalate if unresolved."
        ],
        "3": [
            "Check free disk space.",
            "Identify large files using approved methods.",
            "Do not delete user files without permission.",
            "Follow company cleanup procedures."
        ],
        "4": [
            "Check whether the hostname is correct.",
            "Inspect DNS settings using ipconfig /all.",
            "Try a DNS lookup with nslookup.",
            "Document results and escalate if unresolved."
        ]
    }

    if choice in guides:
        for step, instruction in enumerate(guides[choice], start=1):
            print(f"{step}. {instruction}")
    else:
        print("Invalid choice. Select a number from 1 to 4.")


def create_ticket():
    ticket_dir = Path("reports")
    ticket_dir.mkdir(parents=True, exist_ok=True)

    ticket_file = ticket_dir / "tickets.csv"

    print("\n--- CREATE IT SUPPORT TICKET ---")

    username = input("Enter employee name: ").strip()
    issue = input("Describe the technical issue: ").strip()

    print("\nPriority:")
    print("1. Low")
    print("2. Medium")
    print("3. High")

    priorities = {
        "1": "Low",
        "2": "Medium",
        "3": "High"
    }

    priority_choice = input("Choose priority (1-3): ").strip()

    if not username or not issue:
        print("Employee name and issue are required.")
        return

    if priority_choice not in priorities:
        print("Invalid priority.")
        return

    # Read existing tickets to generate the next ID.
    existing_ids = []

    if ticket_file.exists():
        try:
            with ticket_file.open(
                "r", newline="", encoding="utf-8"
            ) as file:
                for row in csv.DictReader(file):
                    ticket_id = row.get("Ticket ID", "")
                    if ticket_id.startswith("INC"):
                        try:
                            existing_ids.append(int(ticket_id[3:]))
                        except ValueError:
                            pass
        except OSError as error:
            print("Unable to read tickets:", error)
            return

    next_number = max(existing_ids, default=0) + 1
    ticket_id = f"INC{next_number:03d}"

    ticket = {
        "Ticket ID": ticket_id,
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Employee": username,
        "Issue": issue,
        "Priority": priorities[priority_choice],
        "Status": "Open"
    }

    fields = [
        "Ticket ID", "Date", "Employee",
        "Issue", "Priority", "Status"
    ]

    try:
        file_exists = ticket_file.exists()

        with ticket_file.open(
            "a", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=fields)

            if not file_exists or ticket_file.stat().st_size == 0:
                writer.writeheader()

            writer.writerow(ticket)

        print("\nTicket created successfully!")
        print("Ticket ID:", ticket_id)
        print("Priority:", ticket["Priority"])
        print("Status:", ticket["Status"])
        print("Saved in:", ticket_file)

    except OSError as error:
        print("Unable to save ticket:", error)

def view_tickets():
    ticket_file = Path("reports") / "tickets.csv"

    print("\n--- VIEW SUPPORT TICKETS ---")

    if not ticket_file.exists():
        print("No tickets found. Create a ticket first.")
        return

    try:
        with ticket_file.open(
            "r", newline="", encoding="utf-8"
        ) as file:
            tickets = list(csv.DictReader(file))

        if not tickets:
            print("No tickets found.")
            return

        for ticket in tickets:
            print("\n----------------------------")
            print("Ticket ID:", ticket.get("Ticket ID", ""))
            print("Date:", ticket.get("Date", ""))
            print("Employee:", ticket.get("Employee", ""))
            print("Issue:", ticket.get("Issue", ""))
            print("Priority:", ticket.get("Priority", ""))
            print("Status:", ticket.get("Status", ""))

    except OSError as error:
        print("Unable to read tickets:", error)

def update_ticket_status():
    ticket_file = Path("reports") / "tickets.csv"

    print("\n--- UPDATE TICKET STATUS ---")

    if not ticket_file.exists():
        print("No tickets found. Create a ticket first.")
        return

    try:
        with ticket_file.open(
            "r", newline="", encoding="utf-8"
        ) as file:
            reader = csv.DictReader(file)
            fields = reader.fieldnames
            tickets = list(reader)

        if not tickets or not fields:
            print("No tickets found.")
            return

        ticket_id = input("Enter ticket ID (e.g., INC001): ")
        ticket_id = ticket_id.strip().upper()

        ticket = next(
            (t for t in tickets
             if t.get("Ticket ID", "").upper() == ticket_id),
            None
        )

        if ticket is None:
            print("Ticket ID not found.")
            return

        print("\n1. Open")
        print("2. In Progress")
        print("3. Resolved")

        statuses = {
            "1": "Open",
            "2": "In Progress",
            "3": "Resolved"
        }

        choice = input("Choose new status (1-3): ").strip()

        if choice not in statuses:
            print("Invalid status choice.")
            return

        ticket["Status"] = statuses[choice]

        with ticket_file.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(tickets)

        print(f"Ticket {ticket_id} updated to {ticket['Status']}.")

    except OSError as error:
        print("Unable to update ticket:", error)


def main():
    while True:
        print("\n================================")
        print(" L1 DESKTOP SUPPORT TOOLKIT")
        print("================================")
        print("1. System Information")
        print("2. Network Configuration")
        print("3. Internet Connectivity Test")
        print("4. DNS Lookup")
        print("5. Disk Space Check")
        print("6. Save Troubleshooting Report")
        print("7. Troubleshooting Guide")
        print("8. Create Support Ticket")
        print("9. View Support Tickets")
        print("10. Update Ticket Status")
        print("0. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            system_information()
        elif choice == "2":
            network_configuration()
        elif choice == "3":
            internet_connectivity()
        elif choice == "4":
            dns_lookup()
        elif choice == "5":
            disk_space()
        elif choice == "6":
            save_report()
        elif choice == "7":
            troubleshooting_guide()
        elif choice == "8":
            create_ticket()
        elif choice == "9":
            view_tickets()  
        elif choice == "10":
            update_ticket_status()  
        elif choice == "0":
            print("Exiting toolkit. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a listed option.")


if __name__ == "__main__":
    main()
