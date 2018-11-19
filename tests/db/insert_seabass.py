import os
import sys

from eocdb.core.seabass.sb_file_reader import SbFileReader
from eocdb.db.mongo_db_driver import MongoDbDriver


class InsertSeabass():

    @staticmethod
    def main():
        db_url = sys.argv[1]
        db_collection = sys.argv[2]

        input_dir = sys.argv[3]
        if not os.path.isdir(input_dir):
            raise IOError("input directory does not exist: " + input_dir)

        reader = SbFileReader()
        db_driver = MongoDbDriver()
        db_driver.init(**{'url' : db_url + '/' + db_collection})

        document_count = 0
        record_count = 0

        for root, dirs, files in os.walk(input_dir):
            if not 'archive' in root:
                continue

            for name in files:
                full_path = os.path.join(root, name)

                if os.path.getsize(full_path) > 8500000:
                    print("SKIPPING - too large:" + full_path)
                    continue

                to_ingest = False
                # we need to ignore errors here to prevent Python to use unicode decoders on binary files tb 2018-09-20
                with open(full_path, errors='ignore') as file:
                    line_start = file.read(16)
                    if '/begin_header' in line_start:
                        to_ingest = True

                if to_ingest:
                    print(full_path)
                    document = reader.read(full_path)

                    document_count += 1
                    record_count += document.record_count

                    db_driver.insert(document.to_dict())

        print("Number of docs: " + str(document_count))
        print("Number of recs: " + str(record_count))
        db_driver.close()


if __name__ == "__main__":
    sys.exit(InsertSeabass.main())

