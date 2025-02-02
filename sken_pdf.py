import os
import hashlib
import logging
import requests
import pyclamd
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

# Setup logging supaya gampang debugging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class PDFScanner:
    def __init__(self, vt_api_key):
        self.vt_api_ = vt_api_key  # API key VirusTotal

    # 🔹 1. Hash file sebelum scan
    def get_file_hash(self, file_path):
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                hasher.update(chunk)
        return hasher.hexdigest()

    # 🔹 2. Cek hash ke VirusTotal sebelum upload
    def check_virustotal_hash(self, file_hash):
        url = "https://www.virustotal.com/vtapi/v2/file/report"
        params = {"apikey": self.vt_api_, "resource": file_hash}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            result = response.json()
            if result["response_code"] == 1:
                logging.info(f"🔍 File sudah di-scan sebelumnya! Hasil: {result}")
                return result
        return None

    # 🔹 3. Scan file pakai ClamAV
    def check_clamav(self, file_path):
        try:
            cd = pyclamd.ClamdAgnostic()
            if not cd.ping():
                logging.error("⚠️ ClamAV tidak berjalan! Pastikan sudah diaktifkan.")
                return False

            scan_result = cd.scan_file(file_path)
            if scan_result:
                logging.warning(f"⚠️ File terdeteksi virus oleh ClamAV: {scan_result}")
                return True
        except Exception as e:
            logging.error(f"❌ Error saat scanning dengan ClamAV: {e}")
        return False

    # 🔹 4. Cek apakah PDF mengandung JavaScript (potensi malware)
    def check_pdf_javascript(self, file_path):
        try:
            with open(file_path, "rb") as f:
                parser = PDFParser(f)
                doc = PDFDocument(parser)
                if hasattr(doc, "js"):
                    logging.warning("⚠️ PDF ini mengandung JavaScript! Bisa berbahaya.")
                    return True
        except Exception as e:
            logging.error(f"❌ Gagal membaca PDF: {e}")
        return False

    # 🔹 5. Upload file ke VirusTotal kalau belum ada di database
    def upload_to_virustotal(self, file_path):
        try:
            url = "https://www.virustotal.com/vtapi/v2/file/scan"
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f)}
                params = {"apikey": self.vt_api_}
                response = requests.post(url, files=files, params=params)

            if response.status_code == 200:
                result = response.json()
                logging.info(f"📤 File di-upload ke VirusTotal! Cek hasilnya: {result}")
                return result
            else:
                logging.error(f"❌ Gagal upload ke VirusTotal: {response.text}")
        except Exception as e:
            logging.error(f"❌ Error saat upload ke VirusTotal: {e}")
        return None

    # 🔹 6. Scan PDF dengan semua metode
    def scan_pdf(self, file_path):
        logging.info(f"🔍 Mulai scanning PDF: {file_path}")

        # 1️⃣ Cek hash di VirusTotal dulu
        file_hash = self.get_file_hash(file_path)
        vt_result = self.check_virustotal_hash(file_hash)
        if vt_result:
            return vt_result

        # 2️⃣ Cek apakah ada JavaScript tersembunyi
        if self.check_pdf_javascript(file_path):
            logging.warning("⚠️ PDF ini punya JavaScript, hati-hati!")

        # 3️⃣ Scan pakai ClamAV
        if self.check_clamav(file_path):
            return "⚠️ File terdeteksi virus oleh ClamAV!"

        # 4️⃣ Upload ke VirusTotal kalau belum ada hasilnya
        return self.upload_to_virustotal(file_path)


# 🔹 7. Contoh Pemakaian
if __name__ == "__main__":
    API_KEY = "ISI_API_KEY_KAMU_DI_SINI"  # Ganti dengan API key VirusTotal kamu
    scanner = PDFScanner(API_KEY)

    pdf_file = "contoh.pdf"  # Ganti dengan path PDF yang mau kamu scan
    result = scanner.scan_pdf(pdf_file)

    print("\n📌 Hasil Scan PDF:", result)
