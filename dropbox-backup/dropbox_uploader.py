import sys
import dropbox
import os
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
import ntpath
import argparse
    
def get_dropbox_invidual_space_used():
    return dbx.users_get_space_usage().used / dbx.users_get_space_usage().allocation.get_individual().allocated
    
def get_dropbox_available_space():
    return dbx.users_get_space_usage().allocation.get_individual().allocated - dbx.users_get_space_usage().used
    
def dropbox_file_exists(path):
    try:
        dbx.files_get_metadata(path)
        return True
    except:
        return False

def get_filename(file_path):
    return ntpath.basename(file_path)
    
def get_file_size(file_path):
    return os.path.getsize(file_path)
    
def upload_file(file_path, dropbox_path, retries=1):
    f = open(file_path, 'rb')
    file_size = os.path.getsize(file_path)
        
    if (file_size < 1024):
        print("Uploading " + file_path + " (" + str(round(file_size)) + " Bytes)", flush=True)
    elif (file_size < (1024 * 1024)):
        print("Uploading " + file_path + " (" + str(round(file_size/(1024))) + " KB)", flush=True)
    else:
        print("Uploading " + file_path + " (" + str(round(file_size/(1024 * 1024))) + " MB)", flush=True)
    
    if (dropbox_file_exists(dropbox_path) is False):
        CHUNK_SIZE = 4 * 1024 * 1024

        for i in range(retries):
            try:
                if file_size <= CHUNK_SIZE:
                    dbx.files_upload(f.read(), dropbox_path)
                    print(str(f.tell()) + " bytes uploaded! (" + str((f.tell()/file_size) * 100) + "% complete!)")
                else:
                    upload_session_start_result = dbx.files_upload_session_start(f.read(CHUNK_SIZE))
                    cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
                                                               offset=f.tell())
                    commit = dropbox.files.CommitInfo(path=dropbox_path)

                    while f.tell() < file_size:
                        if ((file_size - f.tell()) <= CHUNK_SIZE):
                            dbx.files_upload_session_finish(f.read(CHUNK_SIZE),
                                                            cursor,
                                                            commit)
                        else:
                            dbx.files_upload_session_append(f.read(CHUNK_SIZE),
                                                            cursor.session_id,
                                                            cursor.offset)
                            cursor.offset = f.tell()
                            
                        print(str(f.tell()) + " bytes uploaded! (" + str(round((f.tell()/file_size) * 100)) + "% complete)", flush=True)
                return
            except:
                print("Upload attempt (" + str(i) + ") failed.", flush=True)
            
        print("Upload failed!!!", flush=True)
    else:
        print("File already exists. Skipping...", flush=True)
   
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload snapshots to dropbox.')
    parser.add_argument('snapshot_files', type=str, help='Path to snapshot file.', nargs='+')
    parser.add_argument('dropbox_token', type=str, help='Dropbox API token.')
    parser.add_argument('dropbox_path', type=str, help='Path in dropbox.')
    parser.add_argument('-r', '--retries', type=int, default=3, help='Number of upload retries before giving up. Default: 3')
    parser.add_argument('-d', '--debug', type=bool, default=False, help='Debug printout. Default: False')
    args = parser.parse_args()
    token = args.dropbox_token
    dropbox_folder = args.dropbox_path
    upload_file_paths = args.snapshot_files
    retries = args.retries
    debug = args.debug

    if debug:
        print("INPUT_ARGUMENTS")
        print("  " + str(args.snapshot_files))
        print("  " + str(args.dropbox_token))
        print("  " + str(args.dropbox_path))
        print("  " + str(args.retries))

    # Check for an access token
    if (len(token) == 0):
        sys.exit("ERROR: Looks like you didn't add your access token. "
            "Open up backup-and-restore-example.py in a text editor and "
            "paste in your token in line 14.")

    # Create an instance of a Dropbox class, which can make requests to the API.
    #print("Creating a Dropbox object...")
    dbx = dropbox.Dropbox(token)

    # Check that the access token is valid
    try:
        dbx.users_get_current_account()
    except AuthError:
        sys.exit("ERROR: Invalid access token; try re-generating an "
            "access token from the app console on the web.")

    for upload_file_path in upload_file_paths:
    
        dropbox_path = dropbox_folder + "/" + get_filename(upload_file_path)
        
        if (dropbox_file_exists(dropbox_path)):
            print(str(get_filename(dropbox_path)) + " already exists. Skipping...", flush=True)
        else:
            if (get_dropbox_available_space() >= get_file_size(upload_file_path)):
                upload_file(upload_file_path, dropbox_path, retries=retries)
            else:
                print("Dropbox storage full! Deleting oldest files...", flush=True)
                filelist = dbx.files_list_folder(dropbox_folder).entries
                filelist.sort(key=lambda x: x.server_modified, reverse=False)
                for file in filelist:
                    print("Deleting: " + file.path_lower, flush=True)
                    dbx.files_delete(file.path_lower);
                    
                    if (get_dropbox_available_space() >= get_file_size(upload_file_path)):
                        break
                        
                upload_file(upload_file_path, dropbox_path, retries=retries)
 
