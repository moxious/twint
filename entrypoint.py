import sys
import twint
import json
import os
from datetime import date, datetime, timezone, timedelta
from google.cloud import storage
import tempfile

def setup_google():
    if not os.environ.get("KEY", None):
        raise Exception("You must define a KEY environment variable with service key JSON")
    
    temp = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
    temp.write(bytearray(os.environ.get("KEY"), 'utf-8'))
    print(os.environ.get("KEY"))
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp.name
    temp.close()
    print("Credentials staged to %s" % temp.name)
    return temp.name

REQUIRED_CONFIG = ['Bucket']
creds = setup_google()
storage_client = storage.Client()
os.unlink(creds)

def get_filename(args, suffix=''):
    copy = args.copy()
    for key in REQUIRED_CONFIG:
        copy.pop(key, None)
    
    name = ''
    parts = []
    for key in copy.keys():
        parts.append("%s=%s" % (key, copy[key]))
    
    base_directory = args.get("BaseDirectory") or 'twint'
    dataset = args.get('DataSet') or 'default'
    day_directory = datetime.utcnow().strftime("%Y-%m-%d")

    return base_directory + '/' + dataset + '/' + day_directory + '/' + ','.join(parts) + suffix + '.json'

def one_month_ago():
    today = date.today()
    lastMonth = today - timedelta(days=31)
    return lastMonth.strftime("%Y-%m-%d 00:00:00")

def get_twint_config(args):
    """Takes a dict of user-supplied overrides, and creates a twint config
    based on that"""
    options = twint.Config()

    # This section describes the allowed arguments into the container.
    # Default config is overridden with anything the user specified.
    # This can't be written as a subscripted loop because of how the twint Config
    # obj is written.
    options.Username = args.get('Username') or args.get('User') or options.Username
    options.Limit = args.get('Limit') or options.Limit
    options.Search = args.get('Search') or options.Search
    options.Lang = args.get('Lang') or options.Lang
    options.Translate = args.get('Translate') or options.Translate
    options.TranslateDest = args.get('TranslateDest') or options.TranslateDest
    options.Since = args.get('Since') or one_month_ago()

    # Fixed config that can't be overridden.
    options.Store_json = True
    options.Output = 'results.json'
    options.Database = None
    options.Pandas = False
    return options

def remote_exists(bucket_name, file):
    return storage.Blob(
        bucket=storage_client.bucket(bucket_name), 
        name=file).exists()

def do_upload(local_file, bucket_name, remote_file):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(remote_file)
    blob.upload_from_filename(local_file)

    print(
        "File {} uploaded to gs://{}/{}.".format(
            local_file, bucket_name, remote_file
        )
    )    

def get_configuration():
    config = os.environ.get('CONFIG', None)

    if not config:
        raise Exception("Must provide JSON in a CONFIG environment variable")

    args = json.loads(config)

    for key in REQUIRED_CONFIG:
        if not args.get(key):
            raise Exception("Missing required key %s in config" % key)

    return args

def main(argv):
    args = get_configuration()
    final_output_filename = get_filename(args)
    final_config_filename = get_filename(args, '-config')

    b = args['Bucket']
    if remote_exists(b, final_output_filename) and remote_exists(b, final_config_filename):
        raise Exception("Target recent-enough files already exist.  Not repeating")

    args['Start'] = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    print(args)
    options = get_twint_config(args)

    try:
        fp = open (options.Output, 'w')
        fp.truncate(0)
        fp.close()
    except Exception as err:
        print("Failed to truncate: %s" % err)

    try:
        twint.run.Search(options)
    except Exception as err:
        args.Error = "%s" % err

    args['End'] = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

    with open('run-config.json', 'w') as outfile:
        json.dump(args, outfile)

    do_upload(options.Output, args['Bucket'], final_output_filename)
    do_upload('run-config.json', args['Bucket'], final_config_filename)
    
if __name__ == "__main__":
   main(sys.argv[1:])