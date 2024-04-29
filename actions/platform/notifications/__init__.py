from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption

_SLOT_IS_ORG_ADMIN = "is_org_admin"
NOTIF_BUNDLE = "notifications_bundle"
NOTIF_BUNDLE_OPT = "notifications_bundle_option"
NOTIF_EVENT = "notifications_event"
NOTIF_EVENT_OPT = "notifications_event_option"
NOTIF_BEHAVIOR_OPT = "notifications_behavior_option"
NOTIF_CONTACT_ADMIN = "notifications_contact_admin"
NOTIF_TROUBLESHOOT_TO_INTEGRATIONS = "notifications_troubleshoot_to_integrations"
NOTIF_TROUBLESHOOT_TO_NOTIFICATIONS = "notifications_troubleshoot_to_notifications"

service_opt_match = FuzzySlotMatch(
    NOTIF_BUNDLE_OPT,
    [
        FuzzySlotMatchOption(
            "manage events",
            [
                "manage events",
                "Manage my organization's event settings",
                "event settings",
                "org events",
            ],
        ),
        FuzzySlotMatchOption(
            "manage preferences",
            [
                "manage preferences",
                "manage my own notification preferences",
                "manage preferences for my current notifications",
                "preferences",
                "pref",
            ],
        ),
        FuzzySlotMatchOption(
            "manage integrations",
            [
                "manage integrations",
                "manage my integrations",
                "webhooks",
                "splunk",
                "servicenow",
                "manage serviceNow integrations",
                "integration",
            ],
        ),
        FuzzySlotMatchOption(
            "contact admin",
            [
                "contact admin",
                "contact my org admin for me",
                "contact my organization's admin",
                "org admin",
                "admin",
            ],
        ),
        FuzzySlotMatchOption(
            "learn",
            [
                "learn more about notifications",
                "learn",
                "help",
                "docs",
                "documentation",
                "learn more",
                "learn about notifications",
                "learn about",
            ],
        ),
    ],
)
