"""
=============================================================
  IT Incident Root Cause Analysis — Samuel San Diego
  Portfolio Project for Universal Destinations & Experiences
  IT Operational Excellence Internship Application
=============================================================

WHAT THIS SCRIPT DOES:
  Think of this like a detective analyzing crime reports to find
  patterns. Instead of crimes, we're looking at IT incidents —
  and instead of suspects, we're finding the most common causes.

  Steps:
    1. Generate a realistic sample dataset (simulates real incident logs)
    2. Clean and validate the data
    3. Analyze trends, categories, and resolution times
    4. Identify repeat (recurring) issues — the core of Root Cause Analysis
    5. Print a clean summary report
    6. Save results to CSV for use in Excel or Power BI
"""

import csv
import random
import os
from datetime import datetime, timedelta
from collections import Counter, defaultdict


# ── 1. GENERATE SAMPLE INCIDENT DATA ─────────────────────────────────────────
# Think of this like printing fake-but-realistic incident tickets to practice on.
# In a real job, you'd load actual data from ServiceNow or a database.

def generate_incidents(num_incidents=200):
    """
    Creates a list of fake IT incident records.
    Each incident is a dictionary — like a row in a spreadsheet.
    """

    systems = [
        "WiFi - Park East", "WiFi - Park West", "WiFi - Hotels",
        "Ride Control - Coasters", "Ride Control - Water Rides",
        "POS - Merchandise", "POS - Food & Beverage",
        "Ticketing Gates", "CCTV - Park Zone A", "CCTV - Park Zone B",
        "Server - Primary", "Server - Backup",
        "Hotel Property Mgmt System", "Employee Devices",
    ]

    # Root causes — these are the "why did it break?" categories
    root_causes = [
        "Hardware Failure",       # physical equipment broke
        "Configuration Error",    # someone set something up wrong
        "Network Connectivity",   # cables, routers, switches
        "Software Bug",           # a program had an error
        "Human Error",            # someone made a mistake
        "Capacity/Overload",      # too much traffic, system overwhelmed
        "Vendor/Third-Party",     # external service went down
        "Unknown / Pending RCA",  # still investigating
    ]

    priorities = ["Critical", "High", "Medium", "Low"]
    # Weighted — most real incidents are Medium or Low
    priority_weights = [0.05, 0.15, 0.50, 0.30]

    statuses = ["Resolved", "Resolved", "Resolved", "Open", "In Progress"]
    # 60% resolved, 20% open, 20% in-progress

    incidents = []
    base_date = datetime(2026, 1, 1)

    for i in range(1, num_incidents + 1):
        priority = random.choices(priorities, weights=priority_weights)[0]
        system   = random.choice(systems)
        cause    = random.choices(
            root_causes,
            # Make network + config errors more common — realistic
            weights=[0.10, 0.20, 0.25, 0.15, 0.10, 0.08, 0.07, 0.05]
        )[0]
        status   = random.choice(statuses)

        # Resolution time varies by priority (higher priority = faster response)
        res_time_map = {
            "Critical": random.uniform(0.5, 2.0),
            "High":     random.uniform(1.0, 4.0),
            "Medium":   random.uniform(2.0, 8.0),
            "Low":      random.uniform(4.0, 24.0),
        }
        resolution_hours = round(res_time_map[priority], 2) if status == "Resolved" else None

        # Random date within the last 60 days
        days_offset = random.randint(0, 59)
        hour_offset = random.randint(0, 23)
        created_at = base_date + timedelta(days=days_offset, hours=hour_offset)

        incidents.append({
            "incident_id":       f"INC-{3000 + i:04d}",
            "created_date":      created_at.strftime("%Y-%m-%d"),
            "system_affected":   system,
            "priority":          priority,
            "status":            status,
            "root_cause":        cause,
            "resolution_hours":  resolution_hours,
            "sla_breached":      resolution_hours is not None and resolution_hours > {
                "Critical": 1.0, "High": 4.0, "Medium": 8.0, "Low": 24.0
            }[priority],
        })

    return incidents


# ── 2. DATA CLEANING & VALIDATION ────────────────────────────────────────────
# Like proofreading a spreadsheet before you analyze it.

def clean_data(incidents):
    """
    Checks for missing or invalid values. Returns cleaned list + a report.
    """
    cleaned = []
    issues_found = []

    for row in incidents:
        # Check for missing resolution time on resolved incidents
        if row["status"] == "Resolved" and row["resolution_hours"] is None:
            issues_found.append(f"{row['incident_id']}: Missing resolution time (status=Resolved)")
            row["resolution_hours"] = 0.0  # fill with 0 as default

        # Check for negative resolution times (shouldn't happen, but good to check)
        if row["resolution_hours"] is not None and row["resolution_hours"] < 0:
            issues_found.append(f"{row['incident_id']}: Negative resolution time — corrected to 0")
            row["resolution_hours"] = 0.0

        cleaned.append(row)

    return cleaned, issues_found


# ── 3. ANALYSIS FUNCTIONS ─────────────────────────────────────────────────────

def count_by_field(incidents, field):
    """
    Count how many incidents have each value for a given field.
    Think of it like sorting a deck of cards by suit and counting each pile.
    """
    counter = Counter(row[field] for row in incidents)
    return counter.most_common()


def avg_resolution_by_category(incidents, group_field):
    """
    For each category (e.g. root cause), calculate the average time to resolve.
    Like figuring out which type of homework takes you the longest.
    """
    totals = defaultdict(list)
    for row in incidents:
        if row["resolution_hours"] is not None:
            totals[row[group_field]].append(row["resolution_hours"])

    averages = {
        category: round(sum(times) / len(times), 2)
        for category, times in totals.items()
    }
    return dict(sorted(averages.items(), key=lambda x: x[1], reverse=True))


def find_recurring_issues(incidents, threshold=5):
    """
    Root Cause Analysis: Find system + cause combos that keep happening.
    Like noticing that the same pothole keeps popping up on the same street.
    """
    combo_counter = Counter()
    for row in incidents:
        key = (row["system_affected"], row["root_cause"])
        combo_counter[key] += 1

    # Only show combos that repeat more than `threshold` times
    recurring = {k: v for k, v in combo_counter.items() if v >= threshold}
    return dict(sorted(recurring.items(), key=lambda x: x[1], reverse=True))


def sla_breach_summary(incidents):
    """
    How many incidents broke SLA (didn't get fixed in time)?
    SLA = Service Level Agreement — a promise about response time.
    """
    total    = len([i for i in incidents if i["status"] == "Resolved"])
    breached = sum(1 for i in incidents if i.get("sla_breached"))
    rate     = round((breached / total * 100), 1) if total > 0 else 0
    return {"total_resolved": total, "sla_breaches": breached, "breach_rate_pct": rate}


# ── 4. PRINT REPORT ───────────────────────────────────────────────────────────

def print_report(incidents, clean_issues):
    """
    Prints a clean summary — like a one-page executive brief.
    """
    divider = "─" * 60

    print("\n" + "=" * 60)
    print("  IT INCIDENT ROOT CAUSE ANALYSIS REPORT")
    print("  Universal Destinations & Experiences · Q1 2026")
    print("  Analyst: Samuel San Diego")
    print("=" * 60)

    # ── Overview
    print(f"\n{divider}")
    print("  OVERVIEW")
    print(divider)
    total = len(incidents)
    resolved = sum(1 for i in incidents if i["status"] == "Resolved")
    open_    = sum(1 for i in incidents if i["status"] == "Open")
    inprog   = sum(1 for i in incidents if i["status"] == "In Progress")
    print(f"  Total Incidents Analyzed : {total}")
    print(f"  Resolved                 : {resolved}  ({round(resolved/total*100)}%)")
    print(f"  Open                     : {open_}")
    print(f"  In Progress              : {inprog}")

    # ── Data Quality
    print(f"\n{divider}")
    print("  DATA QUALITY CHECK")
    print(divider)
    if clean_issues:
        print(f"  ⚠  {len(clean_issues)} data issue(s) found and corrected:")
        for issue in clean_issues[:5]:
            print(f"     • {issue}")
    else:
        print("  ✓  No data quality issues found.")

    # ── SLA
    sla = sla_breach_summary(incidents)
    print(f"\n{divider}")
    print("  SLA PERFORMANCE")
    print(divider)
    print(f"  Resolved Incidents : {sla['total_resolved']}")
    print(f"  SLA Breaches       : {sla['sla_breaches']}")
    print(f"  Breach Rate        : {sla['breach_rate_pct']}%")
    target_met = "✓ TARGET MET" if sla['breach_rate_pct'] < 10 else "✗ ABOVE TARGET — Action Required"
    print(f"  Status             : {target_met} (target: <10%)")

    # ── Top Root Causes
    print(f"\n{divider}")
    print("  TOP ROOT CAUSES  (what's breaking things)")
    print(divider)
    for cause, count in count_by_field(incidents, "root_cause")[:5]:
        bar = "█" * (count // 4)
        print(f"  {cause:<28} {count:>3} incidents  {bar}")

    # ── Slowest to Resolve
    print(f"\n{divider}")
    print("  AVG RESOLUTION TIME BY ROOT CAUSE  (hours)")
    print(divider)
    avgs = avg_resolution_by_category(incidents, "root_cause")
    for cause, avg in list(avgs.items())[:5]:
        print(f"  {cause:<28} {avg:>5} hrs")

    # ── Most Affected Systems
    print(f"\n{divider}")
    print("  MOST AFFECTED SYSTEMS")
    print(divider)
    for system, count in count_by_field(incidents, "system_affected")[:5]:
        bar = "█" * (count // 3)
        print(f"  {system:<30} {count:>3}  {bar}")

    # ── Recurring Issues (RCA)
    print(f"\n{divider}")
    print("  ★  RECURRING ISSUES — Root Cause Analysis Targets")
    print("  (System + Cause combos appearing 5+ times)")
    print(divider)
    recurring = find_recurring_issues(incidents, threshold=5)
    if recurring:
        for (system, cause), count in list(recurring.items())[:6]:
            print(f"  [{count:>2}x]  {system}  →  {cause}")
        print()
        print("  RECOMMENDATION: These combinations should be escalated")
        print("  to Problem Management for permanent fix investigation.")
    else:
        print("  No recurring patterns above threshold found.")

    print(f"\n{'=' * 60}")
    print("  END OF REPORT")
    print(f"{'=' * 60}\n")


# ── 5. EXPORT TO CSV ──────────────────────────────────────────────────────────

def export_to_csv(incidents, filename="incident_analysis_export.csv"):
    """
    Save results to a CSV file that can be opened in Excel or Power BI.
    Think of CSV like a plain-text spreadsheet — rows and columns separated by commas.
    """
    output_path = os.path.join("/mnt/user-data/outputs", filename)

    fieldnames = [
        "incident_id", "created_date", "system_affected",
        "priority", "status", "root_cause",
        "resolution_hours", "sla_breached"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(incidents)

    print(f"  ✓  Data exported to: {output_path}")
    print(f"  ✓  {len(incidents)} rows written.\n")
    return output_path


def export_summary_csv(incidents, filename="rca_summary.csv"):
    """
    Export the RCA summary — recurring issues and their counts.
    This is the kind of report you'd hand to a manager.
    """
    output_path = os.path.join("/mnt/user-data/outputs", filename)
    recurring = find_recurring_issues(incidents, threshold=3)

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["System Affected", "Root Cause", "Occurrence Count", "Priority Flag"])
        for (system, cause), count in recurring.items():
            flag = "HIGH" if count >= 10 else "MEDIUM" if count >= 7 else "MONITOR"
            writer.writerow([system, cause, count, flag])

    print(f"  ✓  RCA Summary exported to: {output_path}")
    return output_path


# ── MAIN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  Generating incident dataset...")
    raw_data = generate_incidents(200)

    print("  Cleaning and validating data...")
    clean_incidents, data_issues = clean_data(raw_data)

    print("  Running analysis...\n")
    print_report(clean_incidents, data_issues)

    print("  Exporting data files...")
    export_to_csv(clean_incidents, "incident_analysis_export.csv")
    export_summary_csv(clean_incidents, "rca_summary.csv")

    print("  Done! Open the CSV files in Excel or Power BI to visualize further.")
    print("  ─────────────────────────────────────────────────────────────────\n")
