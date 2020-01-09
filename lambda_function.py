import boto3
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection
import curator
import time
import json
import re
import base64
import requests

# The minimum allowed percetage usage for our storage. If the current value
# is greater than the one informed here then we will delete indexes
STORAGE_USAGE_MIN_THRESHOLD=75.0

# Max age in days, if storage is low, everything over will be deleted
MAX_AGE = 365

# Min age in days, if storage is low, this is the minimum amount of days kept
MIN_AGE = 30

# Nunber of days to check between iterations starting from MAX_AGE to MIN_AGE (should be a negative number)
DAY_STEP = -30

# Information used to build the URL used to access the ElasticSearch API 
PROXY_HOST='' # For example, search-my-domain.region.es.amazonaws.com
PROXY_REGION = '' # For example, us-west-1
PROXY_PATH_GET_STORAGE='_cluster/stats?human&pretty'

# The date/time string for the indexes names
TIME_STRING='%Y.%m.%d'

# #############################################################################

service = 'es'
PROXY_PROTO='https'
PROXY_PORT=443
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, PROXY_REGION, service, session_token=credentials.token)

# The actual URL we will use in order to get storage usages
PROXY_URL_GET_STORAGE='%s://%s:%s/%s' % (
    PROXY_PROTO,
    PROXY_HOST,
    PROXY_PORT,
    PROXY_PATH_GET_STORAGE
)

# Lambda execution starts here.
def lambda_handler(event, context):

    main()


# #############################################################################

def get_storage_usage():
    print( 'INFO: Getting storage size')
    print( 'INFO: URL=%s' % PROXY_URL_GET_STORAGE)

    headers = {
        'Content-Type': 'application/json',
    }

    try:
        req = requests.get(
            PROXY_URL_GET_STORAGE,
            headers=headers,
            auth=awsauth
        )
    except requests.exceptions.ConnectionError as e:
        print( 'ERROR: Not able to connect to URL')
        return -1
    except requests.exceptions.Timeout as e:
        print( 'ERROR: ElasticSearch Timeout')
        return -1
    except requests.exceptions.HTTPError as e:
        print( 'ERROR: HTTP Error')
        return -1
    else:
        print( 'INFO: ElasticSearch Response Code = %s' % req.status_code)

        if req.status_code != 200:
            return -1
        else:
            data = req.json()['nodes']['fs']
            free_storage  = float(data['free_in_bytes'])
            total_storage = float(data['total_in_bytes'])

            return 100.0 - ((free_storage / total_storage) * 100.0)

# #############################################################################

def clean(es = None):

    for i in range(MAX_AGE, MIN_AGE, DAY_STEP):

        current_storage = get_storage_usage()
        print( 'INFO: Current storage is %s%%' % current_storage)
        if current_storage == -1:
            print( 'WARN: It was not able to retrieve current storage size')
        elif current_storage >= STORAGE_USAGE_MIN_THRESHOLD:
            print( 'INFO: Current storage is above the threshold')
            
            index_list = curator.IndexList(es)
            
            # Filters by age, anything with a time stamp older than 30 days in the index name.
            index_list.filter_by_age(source='name', direction='older', timestring=TIME_STRING, unit='days', unit_count=i)

            # Filters by naming prefix.
            # index_list.filter_by_regex(kind='prefix', value='my-logs-2017')

            # Filters by age, anything created more than one month ago.
            # index_list.filter_by_age(source='creation_date', direction='older', unit='months', unit_count=1)

            print("Finding indices older than %s days" % i)
            print("Found %s indices to delete" % len(index_list.indices))

            for index in index_list.indices:
                print("  %s" % index)

            # If our filtered list contains any indices, delete them.
            if index_list.indices:
                curator.DeleteIndices(index_list).do_action()
            
        else:
            print( 'INFO: Storage is fine, no index will be deleted')
            break

def main():
    print( 'INFO: Starting task')
    # Build the Elasticsearch client.
    es = Elasticsearch(
        hosts = [{'host': PROXY_HOST, 'port': PROXY_PORT}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    clean(es)
    print( 'INFO: Completed')

# #############################################################################

if __name__ == "__main__":
    main()