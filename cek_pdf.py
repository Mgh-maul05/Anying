import os
import hashlib
import requests
from PyPDF2 import PdfReader
import pdfminer.high_level
import pyclamd
from datetime import datetime

class PDFScanner:
    def __init__(self):
        self.cd = self._init_clamav()
        self.vt_api_key = 'YOUR_VIRUSTOTAL_API_KEY'  # Daftar di VirusTotal untuk mendapatkan API key

    def _init_clamav(self):
        try:
            return pyclamd.ClamdAgnostic()
        except Exception as e:
            print(f"Peringatan: ClamAV tidak terpasang atau tidak berjalan - {e}")
            return None

    def _scan_clamav(self, file_path):
        if self.cd:
            try:
                scan_result = self.cd.scan_file(file_path)
                return scan_result is None
            except Exception as e:
                print(f"Kesalahan pemindaian ClamAV: {e}")
                return False
        return True

    def _check_virustotal(self, file_path):
        try:
            url = 'https://www.virustotal.com/vtapi/v2/file/scan'
            files = {'file': (os.path.basename(file_path), open(file_path, 'rb'))}
            params = {'apikey': self.v
