"""
EXP-13: Production High-Concurrency API Telemetry Ingestion Receiver.
Implements a multi-threaded HTTP gateway backed by an atomic SQLite persistence layer 
enforcing Write-Ahead Logging (WAL) and idempotent mutation boundaries.
"""
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class Receiver(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self, address, database):
        super().__init__(address, Handler)
        self.database = str(database)
        with sqlite3.connect(self.database) as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("CREATE TABLE IF NOT EXISTS actions (key TEXT PRIMARY KEY, payload TEXT NOT NULL)")
            db.commit()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): 
        pass
        
    def do_POST(self):
        if self.path != '/actions': 
            self.send_error(404)
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length < 10000: 
                raise ValueError('Payload length exceeds safety threshold limits.')
                
            item = json.loads(self.rfile.read(length))
            key = item['action_key']
            payload = item['payload']
            
            if not isinstance(key, str) or not key or not isinstance(payload, dict): 
                raise ValueError('Invalid session transaction configuration schema.')
                
            serialized = json.dumps(payload, sort_keys=True)
            
            with sqlite3.connect(self.server.database, timeout=10) as db:
                db.execute('BEGIN IMMEDIATE')
                existing = db.execute('SELECT payload FROM actions WHERE key=?', (key,)).fetchone()
                
                if existing and existing[0] != serialized:
                    code = 409
                    result = {'status': 'MUTATION_COLLISION_ABORT'}
                elif existing:
                    code = 200
                    result = {'status': 'IDEMPOTENCY_FILTER_MATCH'}
                else:
                    db.execute('INSERT INTO actions(key,payload) VALUES (?,?)', (key, serialized))
                    code = 201
                    result = {'status': 'TRANSACTION_COMMITTED'}
                db.commit()
                
            data = json.dumps(result).encode()
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            self.send_error(400)
