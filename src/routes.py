import urllib
import urllib

def _api(sub:str):
    return f"/api/{sub}"


api_download_file_path = _api('file')
def api_download_file(filepath: str):
    return api_download_file_path +"?"+urllib.parse.urlencode({'id': filepath})


index = ""