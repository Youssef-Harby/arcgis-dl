# reference: https://github.com/darrenjs/howto/blob/master/python/metadata_with_pandas.py
import pyarrow.json as paj
import pyarrow.parquet as pq
import json
import typing


# example metadata, and our custom key at which it will be stored.
META_KEY = 'metakey'


def write_metadata(json_path: str, 
                   time: str,
                   meta_key: str = META_KEY) -> None:
    # TODO: add more metadata
    custom_meta_content = {
        'user': 'youssef',
        'time': time
    }
    ext = "." + json_path.split(".")[-1]
    save_path = json_path.replace(ext, ".parquet")
    table = paj.read_json(json_path)
    # Arrow metadata can only be byte strings, so we must encode our metadata into
    # such a format (we will also do the same for custom_meta_key). This returns a
    # pure ASCII string, which means UTF characters will be appear like: \u0103
    custom_meta_json = json.dumps(custom_meta_content)
    # Build the new global metadata by merging together our custom metadata and the
    # existing metadata; it is because of this merge that we need to choose a unique
    # namespace key for our custom metadata.
    existing_meta = table.schema.metadata
    if existing_meta is None:
        combined_meta = {meta_key.encode(): custom_meta_json.encode()}
    else:
        combined_meta = {
            meta_key.encode(): custom_meta_json.encode(),
            **existing_meta
        }
    # Create a new Arrow table by copying existing table but with the metadata
    # replaced, Store the new table in the reused `table` variable.
    table = table.replace_schema_metadata(combined_meta)
    # write the file
    pq.write_table(table, save_path, compression='GZIP')


def check_metadata(metadata_path: str, meta_key: str = META_KEY) -> typing.Tuple:
    # now load it back in
    restored_table = pq.read_table(metadata_path)
    # to get our custom metadata, we first retrieve from the global namespace
    restored_meta_json = restored_table.schema.metadata[meta_key.encode()]
    # since we stored as an encoded string, we need to decode it
    restored_meta = json.loads(restored_meta_json)
    return restored_table, restored_meta


if __name__ == "__main__":
    print(
        check_metadata(r"E:\dataFiles\github\arcgis-dl\layers\sampleserver6.arcgisonline.com\Energy\Geology\Fabric(Point).parquet")
    )