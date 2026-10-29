import argparse
from process_projects import process_pdf_project_per_page

def main():
    parser = argparse.ArgumentParser(description="Process PDF files and extract AI/ML project information.")
    parser.add_argument("--pdf_files", nargs="+", help="List of PDF files to process.")
    parser.add_argument("--output", "-o", help="Output CSV file.")
    parser.add_argument("--markdown", "-m", help="Output Markdown file, with the keywords bolded in the project text.")

    args = parser.parse_args()

    for pdf_file in args.pdf_files:
        print(f"Processing {pdf_file}...")
        if not args.output:
            output_file = pdf_file.replace(".pdf", "_ai_ml_table.csv")
        else:
            output_file = args.output
        if not args.markdown:
            markdown_file = pdf_file.replace(".pdf", "_ai_ml_keywords.md")
        else:
            markdown_file = args.markdown
        process_pdf_project_per_page(pdf_file, output_file, markdown_file)


if __name__ == "__main__":
    # This will create a CSV file with each project title and, for each keyword, whether it contains the keyword, 
    # as well as a final column indicating if any AI/ML keyword was found.
    # This is a first pass at finding the AI/ML projects, and a human can review the results to identify any false positives or missed projects.
    # For example, a human could remove a project that creates a database and mentions that future work could involve ML applied to that 
    # database but doesn't actually involve ML in the current project.
    main()