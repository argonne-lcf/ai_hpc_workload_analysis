# HPC-AI Workload Analysis

## Motivation/Summary
AI/ML workloads are increasingly part of what users want to do on HPC systems. Some common questions are:
- For a given set of projects (like INCITE projects in a particular year), approximately how many involve AI/ML?
- Of those involving AI/ML, what do the users want to do more specifically? For example, are they using transformers? Graph neural networks? Also running simulations? 

Since multiple groups have similar questions across multiple facilities, this repo contains a small amount of helper code to make it easier to skim project summaries or proposals (pdfs).
- It enumerates a set of keywords that suggest an AI/ML component, such as "neural network" or a particular kind of AI/ML, like "GNN."
- It outputs the number of projects processed and how many of them contain at least one of the keywords. (This is a very rough estimate of how many projects contain an AI/ML component.)
- It optionally creates a CSV file with one row per project and one column per keyword. The entries are boolean: does the project document contain this keyword? A final column, "AI/ML," is also boolean: does this project document contain any of the keywords?
- It optionally outputs a markdown file with the text extracted from the pdf(s) with the keywords bolded. This makes it easier for a human to skim the projects and decide how they want to categorize them. Note: this could include skimming for more specific categories, like how many involve natural language data.  


## Example Usage
This code was written for and tested on the public fact sheets announcing the projects selected for the [INCITE](https://doeleadershipcomputing.org/) and [ALCC](https://science.osti.gov/ascr/Facilities/Accessing-ASCR-Facilities/ALCC) allocation programs. There is one pdf per year for INCITE and one per year for ALCC. Each selected project is summarized within one page. The fact sheets are available at:
- [INCITE awardees](https://doeleadershipcomputing.org/awardees/) 
- [ALCC current awardees](https://science.osti.gov/ascr/Facilities/Accessing-ASCR-Facilities/ALCC/ALCC-Current-Awards) 
- [ALCC past awardees](https://science.osti.gov/ascr/Facilities/Accessing-ASCR-Facilities/ALCC/ALCC-Past-Awards) 

Example:
```
python example_script.py --pdf_files ./data/2026INCITEFactSheets.pdf
```
The code will need to be adapted for scenarios other than the INCITE and ALCC fact sheets. For example, this code makes assumptions about how to extract the title of a project in `extract_project_title`, and the function `process_pdf_project_per_page` assumes that there is one project per page of a pdf. 

## Testing

There is a test in `test_process_projects.py` that assumes you have downloaded the recent public factsheets for INCITE and ALCC. It runs `process_pdf_project_per_page` on a set of PDFs and checks the number of projects found and the number of projects labeled as AI/ML. 
This can be run with just pytest on the command line:
```
pytest
```

NOTE: the "expected" output for each PDF in this test is not some kind of ground truth. It is just the numbers returned by the current version of the code. If you tweak the code in a way that shouldn't change the counts, then the test should pass. However, if, for example, you tweak the code in a way that should remove a false positive, then you should update the test. 