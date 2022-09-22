import json
import logging
from datetime import datetime, timedelta
from dateutil.parser import parse

from Helper import Helper
from Configuration import Configuration
from LogAnalyticsHandler import LogAnalyticsHandler
from BlobHandler import BlobHandler


def export_data(la_handler, blob_handler, table_name, base_la_query, query_version, start_export_time, start_time, end_time, helper, configuration, logger):
    """Export a LA table Query in local file and then upload it to blob
    Args:
        la_handler (LogAnalyticsHandler): A handler to execute a KQL query
        blob_handler (BlobHandler): A handler to interact with blobs
        table_name (str): logical/actual table name where data needs to be exported ( container name )
        base_la_query (str): Kusto query, excluding the table name
        query_version: version of the Query
        start_export_time: starting time of this export process
        start_time: query start timestamp
        start_end: query end timestamp
        helper: instance of helper class
        configuration: instance of configuration class to get all configuration data
        logger: instance of logger class to log
    """
    blob_path = helper.build_directory_path(table_name, query_version)
    logger.info(
        f"getting data for time range {start_time} and {end_time}")
    df = la_handler.run_query(
        base_la_query, start_time, end_time)

    if df is not None and df.size > 0:
        json_result = df.to_json(orient="records")

        logger.info("Result of query is")
        logger.info(json_result)
        # Write results to local file
        try:
            with open(configuration.LOCAL_FILE_NAME, "w") as json_export:
                json.dump(json_result, json_export)
            logger.info(
                f"{configuration.LOCAL_FILE_NAME} created succefully")
        except Exception as e:
            logger.error(
                f"Unable to create the local files for the export:{e}")
            raise (e)
        # Upload the local results to the Azure Blob Storage
        try:
            blob_handler.upload_blob(
                configuration.LOCAL_FILE_NAME, f"{blob_path}/{configuration.LOCAL_FILE_NAME}")
            logger.info(
                f"{blob_path}/{configuration.LOCAL_FILE_NAME} uploaded")

            # only update state file if export was successfull
            helper.generate_state_file(blob_handler, start_export_time)
        except Exception as e:
            logger.error(e)
    else:
        logger.info("skipping blob upload as there is no data returned by query")


def main():

    configurations = Configuration()
    logger = logging.getLogger(__name__)
    helper = Helper(configurations, logger)

    start_export_time = datetime.now(helper.get_current_timezone_info())
    logger.info(
        f"Started job to export data at {start_export_time}")
    logger.info("Loading environment variables")
    logger.info(configurations.environment)
    logger.info(configurations.keyvault_name)

    # Load all credentials
    az_credentials = helper.get_azcredentials()
    la_workspace_id = helper.get_keyvault_secret(
        configurations.keyvault_name, configurations.log_analytics_secret_name, az_credentials
    )

    # Init LA handler
    la_handler = LogAnalyticsHandler(
        workspace_id=la_workspace_id, credential=az_credentials, logger=logger
    )

    logger.info(f"LA Workspace Id,{la_workspace_id}")

    # get data for each query and store it in its container
    for query_info in helper.get_queries():
        isFirstTimeExport = False
        #reset storage account name everytime to default one
        storageAccountName = configurations.storage_account_name
        # this duration is in mins
        time_delta = query_info.QueryDurationInMins
        logger.info(
            f"Processing table : {query_info.QueryName}, Query: {query_info.Query}")
        # allow exports to different storage account based on config
        if query_info.DestinationStorageLocation:
            storageAccountName = helper.replace_tokens(query_info.DestinationStorageLocation)
            logger.info(
                    f'custom storage account destination is set {storageAccountName}')

        # check for custom duration. default is 1 hr
        if (time_delta == 0):
            time_delta = 60

        # each table is a container to handle RBAC properly for external teams
        container_name = f'export-{query_info.QueryName.lower()}'
        # create blob handler
        blob_handler = BlobHandler(
            storage_account=storageAccountName,
            container=container_name,
            credentials=az_credentials,
            logger=logger
        )

        try:
            # check if container exists else create one
            if blob_handler.container_client.exists():
                logger.info(
                    f'Container {container_name} exists already. Nothing to do.')
            else:
                blob_handler.container_client.create_container()
                logger.info(
                    f'creating container {container_name}')
        except Exception as err:
            logger.error(err)

        try:
            # get last run timestamp
            last_time_ran = helper.get_last_run_timestamp(blob_handler)

            start_time = datetime.now(
                helper.get_current_timezone_info()) - timedelta(minutes=int(60))

            # handle if somehow we get last run as blank
            if last_time_ran is not None:
                if last_time_ran == "":
                    start_time = None
                else:
                    start_time = parse(last_time_ran.split(";")[1])
            else:
                isFirstTimeExport = True
                logger.info(f"setting flag isFirstTimeExport=True export for {container_name}")

            end_time = datetime.now(helper.get_current_timezone_info())

            # if you sepcify FIRST_BACKFILL flag then it should start from that duration
            if configurations.first_backfill == True:
                start_time = datetime.now(
                    helper.get_current_timezone_info()) - timedelta(days=configurations.FIRST_BACKFILL_DURATION)

            time_difference = (end_time - start_time).total_seconds() / 60.0

            # if query has specific time duration and if that does not match then skip the run
            if (time_difference >= time_delta or isFirstTimeExport):
                # TODO: parallelize this export, this can run parallely
                export_data(la_handler=la_handler,
                            blob_handler=blob_handler,
                            table_name=query_info.QueryName,
                            base_la_query=query_info.Query,
                            query_version=query_info.QueryVersion,
                            start_export_time=start_export_time,
                            start_time=start_time,
                            end_time=end_time,
                            helper=helper,
                            configuration=configurations,
                            logger=logger
                            )
            else:
                logger.info(
                    f"Skipping export for {query_info.QueryName} as still time delta does not match, still {time_delta - time_difference} mins left for next run")
        except Exception as err:
            logger.error(err)
        finally:
            logger.info(f"Finished Exporting data for {query_info.QueryName}")

    logger.info("Finished Exporting all queries")


if __name__ == "__main__":
    main()
