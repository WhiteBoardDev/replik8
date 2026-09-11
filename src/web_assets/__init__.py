from dataclasses import dataclass
import dataclasses
import urllib.request
import os
import pathlib


_asset_destination = "generated/assets"

@dataclass
class GeneratedAsset:
    name: str
    source_url: str
    integrity_hash: str


    def local_destination(self) -> str:
        file_name = self.name.split('/')[-1]
        return f"{_asset_destination}/{file_name}"

_generated_assets = (
    GeneratedAsset(
        name="bootstrap_5.3.8.min.css",
        source_url="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css",
        integrity_hash="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB"
    ),
    GeneratedAsset(
        name="htmx_2.0.10.min.js",
        source_url="https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js",
        integrity_hash="sha384-H5SrcfygHmAuTDZphMHqBJLc3FhssKjG7w/CeCpFReSfwBWDTKpkzPP8c+cLsK+V"
    ),
)

pathlib.Path(_asset_destination).mkdir(parents=True, exist_ok=True)



for asset in _generated_assets:
    if not os.path.isfile(asset.local_destination()):
        urllib.request.urlretrieve(asset.source_url, asset.local_destination())



css_assets = [
    x for x in _generated_assets if x.name.endswith('.css')
]

js_assets = [
    x for x in _generated_assets if x.name.endswith('.js')
]


all_known_asset_paths = set([ x.local_destination() for x in _generated_assets])

def main():
    print("assets synced")