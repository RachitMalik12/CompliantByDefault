"""
Expertise mapping configuration for SOC 2 controls.
Maps control IDs to GitHub usernames for automatic issue assignment.
"""

CONTROL_EXPERTISE_MAPPING = {
    # RachitMalik12: CC1-CC3
    "CC1": "RachitMalik12",  # Control Environment
    "CC2": "RachitMalik12",  # Communication and Information
    "CC3": "RachitMalik12",  # Risk Assessment
    
    # AdilFayyaz: CC3-CC5 (CC3 overlap with RachitMalik12)
    # Since CC3 appears in both ranges, we'll use the first assignment (RachitMalik12)
    "CC4": "AdilFayyaz",     # Monitoring Activities
    "CC5": "AdilFayyaz",     # Control Activities
    
    # swassingh: CC5-CC9 (CC5 overlap with AdilFayyaz)
    # Since CC5 appears in both ranges, we'll use the first assignment (AdilFayyaz)
    "CC6": "swassingh",      # Logical and Physical Access Controls
    "CC7": "swassingh",      # System Operations
    "CC8": "swassingh",      # Change Management
    "CC9": "swassingh",      # Risk Mitigation
}


def get_assignee_for_control(control: str) -> str:
    """
    Get the GitHub username to assign for a given SOC 2 control.
    
    Args:
        control: SOC 2 control ID (e.g., "CC1", "CC2")
        
    Returns:
        GitHub username to assign the issue to
    """
    return CONTROL_EXPERTISE_MAPPING.get(control, "RachitMalik12")  # Default to RachitMalik12


def get_all_experts():
    """Get list of all expert GitHub usernames."""
    return list(set(CONTROL_EXPERTISE_MAPPING.values()))
