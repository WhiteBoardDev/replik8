import urllib
import urllib

def _api(sub:Path):
    return f"/api/{sub}"


api_download_file_path = _api('file')
def api_download_file(filepath: Path):
    return api_download_file_path +"?"+urllib.parse.urlencode({'path': filepath})

