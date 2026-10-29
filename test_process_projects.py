import process_projects

EXPECTED = {
    "2020INCITEFactSheets_rev.pdf": {
        "projects": 47,       
        "ai_ml_projects": 2,   
    },
    "ALCC_2020-2021_Fact_Sheets.pdf": {
            "projects": 60,       
            "ai_ml_projects": 16,   
        },
    "2021INCITEFactSheets.pdf": {
            "projects": 51,       
            "ai_ml_projects": 8,   
        },
    "ALCC_2021-2022_Fact_Sheets.pdf": {
            "projects": 44,       
            "ai_ml_projects": 12,   
        },
    "2022INCITEFactSheets.pdf": {
            "projects": 51,       
            "ai_ml_projects": 10,   
        },
    "2023INCITEFactSheets.pdf": {
            "projects": 56,       
            "ai_ml_projects": 11,   
        },
    "ALCC_2023-2024_Factsheets.pdf": {
            "projects": 39,       
            "ai_ml_projects": 11,   
        },
    "2024INCITEFactSheets.pdf": {
            "projects": 75,       
            "ai_ml_projects": 23,   
        },
    "ALCC_Factsheets_2024-2025.pdf": {
            "projects": 48,       
            "ai_ml_projects": 21,   
        },
    "2025INCITEFactSheets.pdf": {
            "projects": 81,       
            "ai_ml_projects": 25,   
        },
    "ALCC_Factsheets_2025_v2.pdf": {
            "projects": 56,       
            "ai_ml_projects": 23,   
        },
    "2026INCITEFactSheets.pdf": {
            "projects": 75,       
            "ai_ml_projects": 30,   
        }
}

def test_process_pdf():
    for pdf_file, expected in EXPECTED.items():
        pdf_file = "./data/" + pdf_file
        projects, ai_ml_projects = process_projects.process_pdf_project_per_page(pdf_file)
        assert projects == expected["projects"], f"Expected {expected['projects']} projects in {pdf_file}, but got {projects}"
        assert ai_ml_projects == expected["ai_ml_projects"], f"Expected {expected['ai_ml_projects']} AI/ML projects in {pdf_file}, but got {ai_ml_projects}"