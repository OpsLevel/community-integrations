import json
import logging
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import boto3
from botocore.exceptions import BotoCoreError, ClientError

# -----------------------------------------------------------------------------
# Logging setup
# -----------------------------------------------------------------------------
logger = logging.getLogger()
logger.setLevel(os.getenv("LOG_LEVEL", "CRITICAL").upper())

OPSLEVEL_WEBHOOK_URL = os.getenv("OPSLEVEL_WEBHOOK_URL")
OPSLEVEL_EXTERNAL_KIND = os.getenv("OPSLEVEL_EXTERNAL_KIND", "aws_memorydb_cluster")
CLUSTER_FILTER = os.getenv("CLUSTER_FILTER")  # optional exact cluster name

# REGION_MODE:
# - "all"  => query all AWS regions where MemoryDB is available
# - "list" => query only regions in REGION_LIST
REGION_MODE = os.getenv("REGION_MODE", "all").strip().lower()
REGION_LIST = os.getenv("REGION_LIST", "").strip()


def get_memorydb_client(region_name):
    logger.debug(f"Creating MemoryDB client for region={region_name}")
    return boto3.client("memorydb", region_name=region_name)


def get_enabled_regions():
    logger.info(f"Resolving regions with REGION_MODE={REGION_MODE}")

    session = boto3.session.Session()

    if REGION_MODE == "list":
        regions = [r.strip() for r in REGION_LIST.split(",") if r.strip()]
        logger.info(f"Parsed REGION_LIST regions={regions}")

        if not regions:
            logger.error("REGION_MODE is 'list' but REGION_LIST is empty")
            raise ValueError("REGION_MODE is 'list' but REGION_LIST is empty.")

        return regions

    regions = session.get_available_regions("memorydb")
    logger.info(f"Discovered {len(regions)} MemoryDB-supported regions")
    logger.debug(f"All discovered regions={regions}")
    return regions


def get_all_clusters(memorydb_client, region_name):
    logger.info(f"Fetching MemoryDB clusters for region={region_name}")
    paginator = memorydb_client.get_paginator("describe_clusters")
    clusters = []

    for page_number, page in enumerate(paginator.paginate(), start=1):
        page_clusters = page.get("Clusters", [])
        logger.debug(
            f"Region={region_name} page={page_number} clusters_in_page={len(page_clusters)}"
        )
        clusters.extend(page_clusters)

    logger.info(f"Fetched {len(clusters)} total clusters for region={region_name}")
    return clusters


def get_cluster_tags(memorydb_client, cluster_arn):
    """
    Fetch AWS resource tags for a MemoryDB cluster via ListTags.
    Returns a list of dicts [{"Key": "...", "Value": "..."}] (JSON-serializable).
    On failure (e.g. missing permission), returns [] and logs the error.
    """
    if not cluster_arn:
        logger.debug("No cluster ARN provided for ListTags")
        return []

    try:
        response = memorydb_client.list_tags(ResourceArn=cluster_arn)
        tag_list = response.get("TagList", [])
        out = [
            {"Key": str(t.get("Key", "")), "Value": str(t.get("Value", ""))}
            for t in tag_list
        ]
        logger.debug(f"ListTags for {cluster_arn} returned {len(out)} tag(s)")
        return out
    except (BotoCoreError, ClientError) as e:
        logger.warning(
            f"ListTags failed for ARN={cluster_arn} error={e}. "
            "Ensure IAM allows memorydb:ListTags. Using empty tags."
        )
        return []
    except Exception as e:
        logger.exception(f"Unexpected error in ListTags for {cluster_arn}: {e}")
        return []


def get_account_id(context):
    """
    Resolve AWS account ID from the Lambda function ARN instead of calling STS.
    This avoids outbound network dependency on sts.amazonaws.com.
    """
    logger.info("Resolving AWS account ID from Lambda context ARN")

    try:
        function_arn = context.invoked_function_arn
        logger.debug(f"Lambda invoked_function_arn={function_arn}")

        account_id = function_arn.split(":")[4]
        logger.info(f"Resolved AWS account ID={account_id}")
        return account_id
    except Exception as e:
        logger.exception(f"Failed to resolve account ID from Lambda context: {str(e)}")
        raise


def serialize_for_json(value):
    """
    Recursively convert boto/datetime-like values into JSON-safe values.
    """
    if isinstance(value, dict):
        return {k: serialize_for_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [serialize_for_json(v) for v in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def enrich_cluster(cluster, region_name, account_id, tags):
    """
    Return the raw cluster object plus tags and lightweight metadata fields
    that are useful for OpsLevel mapping.
    """
    cluster_name = cluster.get("Name")
    logger.info(f"Enriching raw cluster payload for cluster={cluster_name} region={region_name}")

    enriched = serialize_for_json(cluster.copy())
    enriched["Tags"] = tags
    enriched["region"] = region_name
    enriched["accountId"] = account_id

    logger.debug(
        f"Enriched raw cluster={cluster_name} region={region_name} payload="
        f"{json.dumps(enriched, default=str)}"
    )
    return enriched


def collect_clusters_across_regions(context, regions):
    logger.info("Starting multi-region MemoryDB collection")

    account_id = get_account_id(context)

    all_clusters = []
    region_errors = []

    logger.info(f"Beginning scan across {len(regions)} region(s)")

    for region_name in regions:
        logger.info(f"Scanning MemoryDB in region={region_name}")
        client = get_memorydb_client(region_name)

        try:
            clusters = get_all_clusters(client, region_name)

            if CLUSTER_FILTER:
                logger.info(
                    f"Applying CLUSTER_FILTER={CLUSTER_FILTER} in region={region_name}"
                )
                pre_filter_count = len(clusters)
                clusters = [c for c in clusters if c.get("Name") == CLUSTER_FILTER]
                logger.info(
                    f"Region={region_name} clusters before_filter={pre_filter_count} "
                    f"after_filter={len(clusters)}"
                )

            enriched_clusters = []
            for cluster in clusters:
                cluster_name = cluster.get("Name")
                cluster_arn = cluster.get("ARN")
                tags = get_cluster_tags(client, cluster_arn)

                logger.debug(
                    f"Attached {len(tags)} tag(s) to cluster={cluster_name} region={region_name}"
                )

                enriched_clusters.append(
                    enrich_cluster(cluster, region_name, account_id, tags)
                )

            all_clusters.extend(enriched_clusters)
            logger.info(
                f"Completed region={region_name} raw_clusters={len(enriched_clusters)}"
            )

        except (BotoCoreError, ClientError) as e:
            error_text = str(e)
            if "Connect timeout on endpoint URL" in error_text:
                logger.error(
                    f"Network connectivity failure for region={region_name}. "
                    f"Check Lambda VPC/NAT/egress settings. error={error_text}"
                )
            logger.exception(f"Region scan failed for region={region_name}: {error_text}")
            region_errors.append({
                "region": region_name,
                "error": error_text
            })
        except Exception as e:
            logger.exception(
                f"Unexpected error during region scan for region={region_name}: {str(e)}"
            )
            region_errors.append({
                "region": region_name,
                "error": str(e)
            })

    logger.info(
        f"Finished multi-region collection total_clusters={len(all_clusters)} "
        f"region_errors={len(region_errors)}"
    )
    return all_clusters, region_errors


def post_to_opslevel(payload):
    if not OPSLEVEL_WEBHOOK_URL:
        logger.warning("OPSLEVEL_WEBHOOK_URL not set; skipping OpsLevel POST")
        return {"posted": False, "reason": "OPSLEVEL_WEBHOOK_URL not set"}

    url = f"{OPSLEVEL_WEBHOOK_URL}?external_kind={OPSLEVEL_EXTERNAL_KIND}"
    body = json.dumps(payload).encode("utf-8")

    logger.info(
        f"Posting payload to OpsLevel external_kind={OPSLEVEL_EXTERNAL_KIND} "
        f"cluster_count={len(payload.get('clusters', []))}"
    )
    logger.debug(f"OpsLevel URL={url}")
    logger.debug(f"OpsLevel payload={json.dumps(payload, default=str)}")

    req = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(req, timeout=30) as resp:
            response_body = resp.read().decode("utf-8", errors="replace")
            logger.info(f"OpsLevel POST succeeded status_code={resp.status}")
            logger.debug(f"OpsLevel response body={response_body}")
            return {
                "posted": True,
                "status_code": resp.status,
                "response_body": response_body,
            }
    except HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        logger.exception(
            f"OpsLevel POST failed with HTTPError status_code={e.code} body={error_body}"
        )
        return {
            "posted": False,
            "status_code": e.code,
            "error": error_body,
        }
    except URLError as e:
        logger.exception(f"OpsLevel POST failed with URLError error={str(e)}")
        return {
            "posted": False,
            "error": str(e),
        }
    except Exception as e:
        logger.exception(f"Unexpected OpsLevel POST failure error={str(e)}")
        return {
            "posted": False,
            "error": str(e),
        }


def lambda_handler(event, context):
    logger.info("Lambda invocation started")
    logger.debug(f"Incoming event={json.dumps(event, default=str)}")

    try:
        regions_requested = get_enabled_regions()
        clusters, region_errors = collect_clusters_across_regions(context, regions_requested)
    except Exception as e:
        logger.exception(f"Lambda execution failed before payload creation: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }

    payload = {
        "clusters": clusters
    }

    result = {
        "cluster_count": len(clusters),
        "region_mode": REGION_MODE,
        "regions_requested": regions_requested,
        "region_errors": region_errors,
        "payload": payload,
    }

    logger.info(
        f"Payload ready cluster_count={len(clusters)} "
        f"region_errors={len(region_errors)}"
    )

    if OPSLEVEL_WEBHOOK_URL:
        result["opslevel"] = post_to_opslevel(payload)

    logger.info("Lambda invocation completed successfully")
    logger.debug(f"Lambda result={json.dumps(result, default=str)}")

    return {
        "statusCode": 200,
        "body": json.dumps(result, default=str),
    }