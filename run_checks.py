import sys

def check():
    import app.main
    from app.components.report_generator import generate_pdf_report
    from src.constants import CLASSES, SEVERITIES, LOCATIONS
    print("All core web application imports succeeded!")

if __name__ == "__main__":
    check()
