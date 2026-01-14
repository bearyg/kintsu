import os
import datetime
from .pdf_generator import PdfGenerator
from .csv_generator import CsvGenerator
from .zip_generator import ZipGenerator

class ReportExporter:
    """
    Orchestrates the generation of reporting artifacts.
    """
    def __init__(self, drive_service):
        self.drive = drive_service

    async def generate_report(self, folder_id: str, report_name: str, formats: list[str]) -> dict:
        """
        Generates requested report formats and saves them to a 'Reports' folder in Drive.
        """
        results = {}
        
        # 1. Fetch Data from Hopper (Mocked for now)
        data = await self._fetch_hopper_data(folder_id)
        
        # 2. Create Reports Folder
        reports_folder_id = await self.drive.ensure_folder("Reports", parent_id=folder_id)
        
        # 3. Generate Formats
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{report_name}_{timestamp}"

        if 'pdf' in formats:
            pdf_path = PdfGenerator.generate(data, base_filename)
            file_id = await self.drive.upload_file(pdf_path, reports_folder_id)
            results['pdf'] = file_id
            os.remove(pdf_path) # Cleanup

        if 'csv' in formats:
            csv_path = CsvGenerator.generate(data, base_filename)
            file_id = await self.drive.upload_file(csv_path, reports_folder_id)
            results['csv'] = file_id
            os.remove(csv_path)

        if 'zip' in formats:
            zip_path = await ZipGenerator.generate(data, base_filename, self.drive)
            file_id = await self.drive.upload_file(zip_path, reports_folder_id)
            results['zip'] = file_id
            os.remove(zip_path)

        return results

    async def _fetch_hopper_data(self, folder_id: str):
        # TODO: Implement actual recursive fetch logic
        # For now, return dummy data
        return {
            "title": "Claim Inventory",
            "items": [
                {"name": "Living Room TV", "value": 1200.00, "category": "Electronics"},
                {"name": "Sofa", "value": 800.00, "category": "Furniture"},
            ]
        }
