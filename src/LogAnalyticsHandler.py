from azure.core.exceptions import HttpResponseError
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
import pandas as pd
from cyberwolveslogger.logger import Logger

class LogAnalyticsHandler:
    """A handler to executes a KQL on a Azure Log Analytics Workspace

    Args:
        workspace_id (str): Workspace ID of LA
    """

    def __init__(self, workspace_id, credential, logger: Logger):
        self.workspace_id = workspace_id
        self.client = LogsQueryClient(credential)
        self.logger = logger

    def run_query(self, query, start_time, end_time):
        """Executes a KQL query on an Azure Log Analytics Workspace

        Args:
            query (str): Kusto query, example:
                'ossem_custom_sec_events_CL
                | top 10 by TimeGenerated
                | sort by TimeGenerated desc'
            start_time: start_time of query from where data needs to be exported
            end_time: end_time of query from where data needs to be exported
        """
        query = str(query).replace("START_TIME", str(start_time))
        query = str(query).replace("END_TIME", str(end_time))

        self.logger.info(f"Executing this Query: {query}")
        try:
            response = self.client.query_workspace(
                self.workspace_id, query,  timespan=(start_time, end_time))
            if response.status == LogsQueryStatus.PARTIAL:
                error = response.partial_error
                data = response.partial_data
                self.logger.error(error.message)
            elif response.status == LogsQueryStatus.SUCCESS:
                self.logger.info("got response from log analytics workspace")
                data = response.tables
            for table in data:
                df = pd.DataFrame(data=table.rows, columns=table.columns)
                return df
        except HttpResponseError as err:
            self.logger.error(f"something fatal happened {err}")
