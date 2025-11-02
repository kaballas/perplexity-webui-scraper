"""Shared constant values for the Perplexity harness."""

SENTINEL_TEXT = "1. No verified limitations found within the specified scope."

DEFAULT_MIN_ITEMS = 3
DEFAULT_OBJECT_OF_ANALYSIS = "the requirement under evaluation"
DEFAULT_IN_SCOPE_MODULES = (
    "RCM, EC, ECP, ONB, RBP, RMK, BTP(Workflow/Ext), Integration Suite/IC, OData APIs, "
    "Stories/Reporting, Data Sphere, ALM, OpenText xECM/InfoArchive, "
    "S/4HANA Finance(if interfaced), "
    "Microsoft Fabric HR RG, DataHub, Purview, Azure DevOps, Terraform, Sentinel/Splunk"
)
DEFAULT_IN_SCOPE_MODULES_SAP = (
    "RCM, EC, ECP, ONB, RBP, RMK, BTP (Workflow/Ext), Integration Suite/IC, OData APIs, "
    "Stories/Reporting, Data Sphere, ALM, OpenText xECM/InfoArchive, S/4HANA Finance"
)
DEFAULT_IN_SCOPE_MODULES_AZURE = (
    "Microsoft Fabric HR RG, DataHub, Purview, Azure DevOps, Terraform, Sentinel/Splunk, EDP"
)
DEFAULT_CONSTRAINT_FILTER = "only constraints that directly affect meeting the stated requirement"

ALLOWED_CONTROLS = {
    "record-keeping",
    "audit-trail",
    "privacy",
    "data-retention",
    "equal-opportunity",
    "merit-selection",
    "conflict-of-interest",
    "notification-content",
    "access-control",
    "provenance",
    "reporting-disclosure",
    "localization",
    "jurisdiction-mapping",
    "appeals-review",
    "governance",
}

ALLOWED_MODULES_ORDERED = (
    "RCM",
    "EC",
    "ECP",
    "ONB",
    "RBP",
    "RMK",
    "BTP",
    "Integration Suite",
    "IC",
    "OData APIs",
    "Stories/Reporting",
    "Data Sphere",
    "ALM",
    "OpenText xECM",
    "OpenText InfoArchive",
    "S/4HANA Finance",
    "Microsoft Fabric HR RG",
    "DataHub",
    "Purview",
    "Azure DevOps",
    "Terraform",
    "Sentinel",
    "Splunk",
)

AUTHORITATIVE_SUFFIXES = (
    ".help.sap.com",
    ".support.sap.com",
    ".userapps.support.sap.com",
    ".launchpad.support.sap.com",
    ".me.sap.com",
    "help.sap.com",
    "support.sap.com",
    "userapps.support.sap.com",
    "launchpad.support.sap.com",
    "me.sap.com",
)

__all__ = [
    "ALLOWED_CONTROLS",
    "ALLOWED_MODULES_ORDERED",
    "AUTHORITATIVE_SUFFIXES",
    "DEFAULT_CONSTRAINT_FILTER",
    "DEFAULT_IN_SCOPE_MODULES",
    "DEFAULT_IN_SCOPE_MODULES_AZURE",
    "DEFAULT_IN_SCOPE_MODULES_SAP",
    "DEFAULT_MIN_ITEMS",
    "DEFAULT_OBJECT_OF_ANALYSIS",
    "SENTINEL_TEXT",
]
