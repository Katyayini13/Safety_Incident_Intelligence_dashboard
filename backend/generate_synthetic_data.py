"""Generate a clearly labeled, deterministic synthetic NLP development dataset."""
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "synthetic_development_incidents.csv"

SAFETY = [
    "A maintenance technician encountered a {hazard} while inspecting {asset}",
    "A contractor reported {hazard} during {task} at {asset}",
    "During a shift change, the crew identified {hazard} beside {asset}",
    "An operator observed {hazard} while accessing {asset} for routine work",
    "A work crew found {hazard} on the route to {asset}",
    "A supervisor recorded {hazard} during a planned inspection of {asset}",
    "A field team raised a safety report about {hazard} near {asset}",
    "While completing {task}, a worker identified {hazard} around {asset}",
    "A permit review found {hazard} before work began at {asset}",
    "A technician stopped work after noticing {hazard} at {asset}",
    "A subcontractor alerted the site lead to {hazard} near {asset}",
    "The operations team logged {hazard} during service activity at {asset}",
    "A night-shift inspection documented {hazard} beside {asset}",
    "A worker raised a near-miss report involving {hazard} at {asset}",
    "Before equipment startup, staff detected {hazard} around {asset}",
    "A safety walk identified {hazard} on the approach to {asset}",
    "The site coordinator reviewed a report of {hazard} during {task}",
    "A technician documented {hazard} after completing work at {asset}",
    "A crew member identified {hazard} while moving materials near {asset}",
    "A routine toolbox inspection recorded {hazard} around {asset}",
]
ENVIRONMENT = [
    "An environmental inspection found {event} near {asset}",
    "The site team recorded {event} during maintenance of {asset}",
    "A technician reported {event} beside {asset} during the morning round",
    "The environmental log noted {event} at {asset}",
    "A field inspection identified {event} around {asset}",
    "An operator observed {event} while servicing {asset}",
    "The shift team raised an environmental report for {event} near {asset}",
    "A contractor notified the supervisor about {event} at {asset}",
    "Routine monitoring detected {event} beside {asset}",
    "The site recorded {event} during a review of {asset}",
    "A maintenance crew isolated {event} while working on {asset}",
    "An environmental walkdown documented {event} around {asset}",
    "A site engineer investigated {event} near {asset}",
    "During a scheduled check, staff found {event} at {asset}",
    "The operations desk received a report describing {event} beside {asset}",
    "A field operator documented {event} while checking {asset}",
    "The environmental coordinator reviewed {event} reported at {asset}",
    "A routine site audit identified {event} around {asset}",
    "The maintenance record described {event} during work on {asset}",
    "A monitoring round logged {event} at {asset}",
]
ESG = [
    "An internal audit identified {issue} in records for {process}",
    "The compliance team documented {issue} during a review of {process}",
    "A governance review found {issue} in the {process} workflow",
    "The site compliance register recorded {issue} affecting {process}",
    "An auditor raised {issue} while sampling {process} evidence",
    "A documentation check identified {issue} across {process} records",
    "The ESG coordinator reported {issue} in the {process} submission",
    "A contractor audit noted {issue} related to {process}",
    "The assurance team reviewed {issue} found during {process}",
    "A scheduled compliance inspection recorded {issue} for {process}",
    "The site governance log noted {issue} in {process} documentation",
    "A regulatory readiness review identified {issue} involving {process}",
    "The reporting team escalated {issue} from the {process} evidence pack",
    "An evidence review found {issue} in files maintained for {process}",
    "A control owner disclosed {issue} during the {process} audit",
    "The compliance register flagged {issue} against {process} requirements",
    "A management review recorded {issue} in the {process} control record",
    "An assurance check found {issue} while verifying {process}",
    "The ESG review team documented {issue} affecting {process} reporting",
    "A site auditor observed {issue} in evidence supporting {process}",
]

ASSETS = ["a turbine service platform", "the battery storage enclosure", "a solar inverter station", "the cable trench crossing", "a water treatment skid", "the workshop lifting bay", "a contractor access road", "the module cleaning line", "a substation maintenance area", "the materials storage yard", "the fire pump room", "a wind gearbox service bay", "the wastewater collection sump", "the site perimeter gate", "the electrical switch room", "a waste handling station", "the loading area", "a generator enclosure", "the drainage channel", "a rooftop access ladder"]
TASKS = ["panel cleaning", "filter replacement", "cable inspection", "lifting operations", "vehicle reversing", "pump maintenance", "confined-area inspection", "equipment isolation", "material handling", "routine servicing", "electrical testing", "waste transfer", "valve replacement", "ladder access", "drain cleaning", "commissioning checks", "contractor onboarding", "toolbox preparation", "night patrol", "fire system maintenance"]
SAFETY_HAZARDS = ["an unguarded rotating coupling", "a wet walkway", "a missing handrail", "a damaged extension cable", "a vehicle reversing near pedestrians", "an unsecured load", "a loose access cover", "a blocked emergency exit", "a worker without required eye protection", "an unprotected cable trench", "a faulty lifting sling", "an exposed electrical conductor", "a slippery ladder landing", "poorly stacked materials", "a failed isolation check", "a dropped tool near a coworker", "a fire alarm during maintenance", "a damaged harness connector", "a pedestrian and forklift near miss", "a pressure hose under strain"]
ENV_EVENTS = ["hydraulic oil seepage", "a contained coolant spill", "an increase in process-water use", "a small diesel leak", "dust emissions above the site alert level", "a blocked stormwater drain", "wastewater discolouration", "a chemical container leak", "a solvent odour near storage", "an overflowing waste skip", "a grease release at a bearing", "a sediment plume in runoff", "a refrigerant leak indication", "mixed waste in the recycling bay", "a minor effluent overflow", "a lubricant drip beneath a pump", "a damaged chemical transfer line", "elevated noise at the boundary", "a leaking cleaning-fluid container", "an unlabelled waste drum"]
ESG_ISSUES = ["a missing approval signature", "incomplete contractor training evidence", "an overdue corrective-action closure", "inconsistent waste transfer records", "a missing permit reference", "an unreconciled emissions figure", "an outdated compliance register", "an incomplete incident disclosure", "a missing inspection record", "a duplicated supplier declaration", "an unverified environmental data entry", "a late regulatory submission", "an undocumented policy exception", "a missing management review", "an expired contractor certificate", "an incomplete audit trail", "a control owner mismatch", "an unsupported ESG metric", "a record retention gap", "a delayed grievance log update"]
PROCESSES = ["environmental reporting", "contractor assurance", "permit-to-work", "waste tracking", "emissions disclosure", "corrective action", "supplier due diligence", "incident reporting", "training records", "regulatory submissions", "energy monitoring", "water stewardship", "audit evidence", "policy control", "grievance handling", "management review", "safety inspection", "risk register", "document retention", "governance approval"]
SEVERITY_CONTEXT = {
    "low": ["The issue was an observation only; no injury or release occurred.", "The record was corrected during the routine review with no operational impact.", "No exposure or loss was reported, and the condition was logged for follow-up."],
    "medium": ["A minor exposure occurred and first aid was provided; the condition was contained.", "A small release was promptly contained and the area was checked for impact.", "A near miss or control gap was confirmed and corrective action was assigned."],
    "high": ["A serious injury required emergency treatment and the work area was isolated.", "An active fire or electrical danger prompted immediate site emergency escalation.", "A major uncontrolled release required emergency containment and HSE response."],
}


def generate_rows():
    rows = []
    category_specs = [
        ("safety", SAFETY, SAFETY_HAZARDS, ASSETS, "hazard"),
        ("environment", ENVIRONMENT, ENV_EVENTS, ASSETS, "event"),
        ("esg_compliance", ESG, ESG_ISSUES, PROCESSES, "issue"),
    ]
    for category_index, (category, templates, values, contexts, slot) in enumerate(category_specs):
        for index, template in enumerate(templates):
            for severity_index, severity in enumerate(("low", "medium", "high")):
                value_index = (index + severity_index * 7) % len(values)
                context_index = (index * 3 + category_index + severity_index * 5) % len(contexts)
                task_index = (index * 2 + category_index + severity_index * 7) % len(TASKS)
                story = template.format(**{slot: values[value_index], "asset": contexts[context_index], "task": TASKS[task_index], "process": contexts[context_index]})
                narrative = f"{story}. {SEVERITY_CONTEXT[severity][(index + severity_index) % 3]}"
                rows.append({"incident_id": f"DEV{len(rows)+1:03d}", "scenario_group": f"DEV-SCENARIO-{len(rows)+1:03d}", "narrative": narrative, "target_category": category, "target_severity": severity})
    return rows


if __name__ == "__main__":
    rows = generate_rows()
    assert len(rows) == 180
    assert len({row["narrative"].casefold() for row in rows}) == len(rows)
    assert len({row["scenario_group"] for row in rows}) == len(rows)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("incident_id", "scenario_group", "narrative", "target_category", "target_severity"))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} synthetic development records to {OUT}")
