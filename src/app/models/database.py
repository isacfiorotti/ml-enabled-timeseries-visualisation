import sqlite3
import os
import re

class SQLiteDB():
    def __init__(self, file_path, data_processor):
        self.data_processor = data_processor
        self.db_directory = os.path.dirname(file_path)
        self.prefix = self._get_db_prefix(file_path)  # Takes input data file path
        self._connect_to_db()
        if not self._check_for_existing_db():
            self._create_tables()
            self._insert_cells()
            self._insert_data()

    def _check_for_existing_db(self):
        '''Check if the database already exists. If it does, return True.'''
        return os.path.exists(f'{self.db_directory}/{self.prefix}.db')

    def _connect_to_db(self):
        db_name = f'{self.db_directory}/{self.prefix}.db'
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def _get_db_prefix(self, file_path):
        return os.path.splitext(os.path.basename(file_path))[0]

    def _create_tables(self):
        headers = self.data_processor.get_headers()

        for header in headers:
            header = self.sanitise(header)
            self.node_table = f'{header}_node_table'
            self.signal_table = f'{header}_signal_table'
            self.cell_table = f'{header}_cell_table'

            # Node table
            self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.node_table} (
                node_id VARCHAR(255) PRIMARY KEY,
                signals_in_node TEXT,
                signal_count INT
            )''')

            # Signal table
            self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.signal_table} (
                signal_id VARCHAR(255) PRIMARY KEY,
                signal_start FLOAT,
                signal_end FLOAT,
                node_id VARCHAR(255),
                FOREIGN KEY (node_id) REFERENCES {self.node_table}(node_id)
            )''')

            # Cell table
            self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.cell_table} (
                cell_id VARCHAR(255) PRIMARY KEY,
                cell_id_start FLOAT,
                cell_id_end FLOAT,
                signal_id VARCHAR(255),
                FOREIGN KEY (signal_id) REFERENCES {self.signal_table}(signal_id)
            )''')

            self._create_data_tables()
            self.conn.commit()

    def sanitise(self, header):
        sanitised = re.sub(r'[^a-zA-Z0-9]', '_', header)
        if re.match(r'^\d', sanitised):
            sanitised = 't_' + sanitised
        return sanitised

    def _insert_cells(self):
        for header in self.data_processor.get_headers():
            sanitised = self.sanitise(header)
            cell_table = f'{sanitised}_cell_table'
            cell_ids, cell_id_starts, cell_id_ends, signal_ids = self.data_processor.get_cells_data(header)
            for cell_id, cell_id_start, cell_id_end, signal_id in zip(cell_ids, cell_id_starts, cell_id_ends, signal_ids):
                try:
                    self.cursor.execute(f'''
                    INSERT INTO {cell_table} (cell_id, cell_id_start, cell_id_end, signal_id)
                    VALUES (?, ?, ?, ?)
                    ''', (cell_id, cell_id_start, cell_id_end, signal_id))
                    self.conn.commit()
                except sqlite3.IntegrityError:
                    print(f"Skipping insert for cell {cell_id} as it violates unique constraint")

    def _create_data_tables(self):
        for header in self.data_processor.get_headers():
            header = self.sanitise(header)
            self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {header}_data_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time FLOAT,
                value FLOAT
            )''')

    def _insert_data(self):
        for header in self.data_processor.get_headers():
            sanitised = self.sanitise(header)
            data = self.data_processor.read_data()
            time = data['Time(s)']
            values = data[header]
            data_table = f'{sanitised}_data_table'
            batch_data = [(t, v) for t, v in zip(time, values)]
            try:
                self.cursor.executemany(f'''
                INSERT INTO {data_table} (time, value)
                VALUES (?, ?)
                ''', batch_data)
                self.conn.commit()
            except sqlite3.IntegrityError as e:
                print(f"An integrity error occurred: {e}. Skipping problematic entries.")

    def insert_groups(self, header, groups):
        pass

    def close(self):
        self.cursor.close()
        self.conn.close()

    def connect(self):
        conn = sqlite3.connect(f'{self.db_directory}/{self.prefix}.db')
        cursor = conn.cursor()
        return conn, cursor
