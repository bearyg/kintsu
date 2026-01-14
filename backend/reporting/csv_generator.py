import csv
import os

class CsvGenerator:
    @staticmethod
    def generate(data, filename_base: str) -> str:
        filepath = f"/tmp/{filename_base}.csv"
        
        items = data.get("items", [])
        if not items:
            return filepath
            
        keys = items[0].keys()
        
        with open(filepath, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(items)
            
        return filepath
