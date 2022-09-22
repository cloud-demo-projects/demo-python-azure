ALL_QUERIES = [
    {
        "QueryName": "SecurityAlert",
        "QueryVersion": "v001",
        "Query": """
            StorageBlobLogs
        """
    }
    # },
    # {
    #     "QueryName": "SecurityIncident",
    #     "QueryVersion": "v001",
    #     "Query": """
    #         SecurityIncident
    #         | where TimeGenerated between (todatetime('START_TIME')..todatetime('END_TIME'))
    #         | order by TimeGenerated desc
    #     """
    # }
]
