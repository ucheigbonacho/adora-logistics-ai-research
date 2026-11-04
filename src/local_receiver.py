"""Local-only receiver. Does not call external systems or operate vehicles."""
import hashlib
import json
import sqlite3


def fingerprint(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


class LocalDispatchReceiver:
    def __init__(self, path):
        self.path = str(path)
        with self._connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS received_actions (
                action_id TEXT PRIMARY KEY,
                payload_digest TEXT NOT NULL,
                receipt TEXT NOT NULL
            )''')

    def _connect(self):
        return sqlite3.connect(self.path, timeout=15)

    def receive(self, action_id, payload):
        if not isinstance(action_id, str) or not action_id.strip():
            raise ValueError('action_id required')
        if not isinstance(payload, dict) or not payload:
            raise ValueError('nonempty payload required')
        digest = fingerprint(payload)
        receipt = 'local-receipt:' + hashlib.sha256((action_id + ':' + digest).encode()).hexdigest()
        with self._connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT payload_digest, receipt FROM received_actions WHERE action_id=?', (action_id,)).fetchone()
            if row:
                return ('duplicate', row[1]) if row[0] == digest else ('conflict', None)
            db.execute('INSERT INTO received_actions VALUES (?, ?, ?)', (action_id, digest, receipt))
            return ('accepted', receipt)

    def lookup(self, action_id):
        with self._connect() as db:
            row = db.execute('SELECT receipt FROM received_actions WHERE action_id=?', (action_id,)).fetchone()
            return row[0] if row else None
