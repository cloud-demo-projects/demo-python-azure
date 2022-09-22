import string


class Query:
    QueryName: string
    QueryVersion: string
    QueryDurationInMins: int
    Query: string
    DestinationStorageLocation: string

    def __init__(self, query_name, query_version, query_duration_minutes, query, destination_storage_location):
        self.QueryName = query_name
        self.QueryVersion = query_version
        self.QueryDurationInMins = int(query_duration_minutes) if query_duration_minutes is not None else 0
        self.Query = query
        self.DestinationStorageLocation = destination_storage_location
