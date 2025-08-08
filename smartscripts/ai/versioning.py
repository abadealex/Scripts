# versioning.py
# Git-style hashing and change tracking

import hashlib
import json
import time

class VersionControl:
    def __init__(self):
        self.versions = []

    def create_version(self, data):
        """
        Creates a version hash from data (dict or string)
        """
        if isinstance(data, dict):
            serialized = json.dumps(data, sort_keys=True)
        else:
            serialized = str(data)
        version_hash = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
        timestamp = time.time()
        self.versions.append({'hash': version_hash, 'timestamp': timestamp, 'data': data})
        return version_hash

    def get_latest_version(self):
        return self.versions[-1] if self.versions else None

    def rollback(self, version_hash):
        for v in self.versions:
            if v['hash'] == version_hash:
                return v['data']
        return None

