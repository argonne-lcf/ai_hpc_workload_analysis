import re
import csv
import os
from pypdf import PdfReader

# NOTE: "learn" on its own is too general, so including various phrases that include "learn"

# List of keywords to check (whole word, case-insensitive)
# \s+: matches one or more whitespace characters (spaces, tabs, newlines) (but not zero). Used for multi-word phrases while allowing for newlines between words.
whole_word_keywords = [
    r"AI", # might also want case-sensitive AI as subword allowed
    r"GenAI",
    r"reinforcement\s+learning",
    r"AlphaFold",
    r"training\s+data",
    r"federated\s+learning",
    r"computer\s+vision",
    r"scikit-learn",
    r"random\s+forest",
    r"xgboost",
    r"oneDAL",
    r"sklearn",
    r"Sci.?ML" # sciML, SciML, Sci-ML, etc.
]

subword_case_sensitive_keywords = [# allow, for example, plural but not lower-case
    r"LLM",
    r"\bML", # \b: allows "ML-based", "ML-enabled", etc., but not an acronym with letters before ML
    r"cuML",
    r"RAPIDS",
    r"GNN",
    r"GAN",
    r"BERT",
    r"GPT",
    r"NLP",
    r"MLIP",
    r"SVM",
    r"K.?NN",
    r"k.?NN", #kNN or k-NN
    r"MLP",
    r"RNN",
    r"DBSCAN",
    r"CNN",
    r"PINN"
]

# \s*.?\s*: allows any amount of white space (\s*) and one optional non-whitespace character between the words (.?), so it will match hyphenated, spaced, or concatenated versions of the words. For example, "machine learning", "machine-learning", "machinelearning", "machine  learning", etc.
subword_keywords = [ # allow plural, etc.
    r"artificial\s*.?\s*intelligence",
    r"foundation\s+model", 
    r"language\s+model",
    r"transformer",
    r"neural\s+network",
    r"graph\s+neural\s+network",
    r"transfer\s+learn",
    r"machine\s*.?\s*learn", # allows "machine learning", "machine-learned", etc. 
    r"physics.?informed", # not sure if this phrase is used in other contexts - could be false positives
    r"pre\s*.?\s*train", # allows "pre-trained", "pretraining", etc.
    r"post\s*.?\s*train", 
    r"instruct\s*.?\s*tun", # instruct-tuned, instruct tuning, etc.
    r"instruction\s*.?\s*tun",
    r"fine\s*.?\s*tun",
    r"prompt\s*.?\s*tun",
    r"training\s+data",
    r"deep\s+learn",
    r"learning\s+machine",
    r"natural\s+language",
    r"diffusion\s+model",
    r"active\s*.?\s*learn",
    r"ensemble\s*.?\s*learn",
    r"generative\s+model",
    r"generative\s+learn",
    r"representation\s+learn",
    r"supervised\s+learn", # covers unsupervised, semi-supervised, self-supervised, etc. because of the subword matching
    r"adversarial\s+network",
    r"decision\s+tree",
    r"gradient\s+boost",
    r"support\s+vector\s+machine",
    r"k.?nearest\s*.?\s*neighbor",
    r"statistical\s+learn",
    r"k\s*.?\s*means",
    r"PyTorch",
    r"TensorFlow",
    r"Bayesian\s*.?\s*learn", # might help to add some other Bayesian keywords, but need to avoid false positives, e.g., "Bayesian optimization" is not necessarily AI/ML
    r"operator\s*.?\s*learn"
]

# NOTE: could consider how to cover more "clustering" and "inference" without false positives - too general of terms

# Every keyword, in the order the results are reported in
all_keywords = whole_word_keywords + subword_case_sensitive_keywords + subword_keywords


def find_spans(text, word, whole_word=False, case_sensitive=False):
    # Return the (start, end) offsets of every match of word in text.
    pattern = r'\b{}\b' if whole_word else r'{}'
    flags = 0 if case_sensitive else re.IGNORECASE
    return [m.span() for m in re.finditer(pattern.format(word), text, flags)]

def mark_keywords(text, marker="**"):
    # Wrap every keyword occurrence in marker, so the keywords show up bolded in Markdown.
    # Returns the marked-up text and a list of booleans, one per keyword in all_keywords.
    all_spans = []
    results = []
    for kw in whole_word_keywords:
        spans = find_spans(text, kw, whole_word=True)
        results.append(bool(spans))
        all_spans += spans
    for kw in subword_case_sensitive_keywords:
        spans = find_spans(text, kw, case_sensitive=True)
        results.append(bool(spans))
        all_spans += spans
    for kw in subword_keywords:
        spans = find_spans(text, kw)
        results.append(bool(spans))
        all_spans += spans

    # Merge overlapping matches so the markers never nest: 
    # "neural network" sits inside "graph neural network". It's nice to include "graph" in the bolding, 
    # but we don't want "**graph **neural network****"
    merged = []
    for start, end in sorted(all_spans):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])

    out = []
    prev = 0
    for start, end in merged:
        out.append(text[prev:start])
        out.append(marker + text[start:end] + marker)
        prev = end
    out.append(text[prev:])
    return "".join(out), results

def extract_project_title(page_text):
    # Extract the project title from page_text.
    # Note: this function works on the INCITE and ALCC fact sheets, but may need to be modified for other formats.
    # Extract string after "Title:" and before "Principal". The title might span multiple lines, so we need to handle that case.
    title_match = re.search(r"Title:\s*(.*?)(?=Principal|$)", page_text, re.DOTALL)
    if title_match:
        title = title_match.group(1).strip()
        # replace newlines with spaces
        title = re.sub(r'\s+', ' ', title)
    else:
        title = "Unknown Title"
    return title

def process_pdf_project_per_page(pdf_path, output_csv=None, output_md=None):
    # This function assumes that each page of the PDF corresponds to one project. 
    # It extracts the project title and checks for the presence of keywords in the text of each page.
    reader = PdfReader(pdf_path)
    rows = []
    sections = []
    
    tmp = reader.pages
    print("Total pages:", len(tmp))  # Debug: Print total number of pages
    count_projects = 0
    count_ai_ml_projects = 0

    for page in reader.pages:
        text = page.extract_text()
        if not text:
            continue
        count_projects += 1
        title = extract_project_title(text)
        #print(title)

        # Check every keyword in one pass, and bold the matches in the page text
        marked_text, results = mark_keywords(text)

        # If any keyword is found, mark the project as an AI/ML project.
        ai_ml = any(results)
        if ai_ml:
            count_ai_ml_projects += 1
        row = [title] + results + [ai_ml]
        rows.append(row)

        found = [kw for kw, hit in zip(all_keywords, results) if hit]

        # Adds one more section for this project to the Markdown output, with the keywords bolded in the project text.
        sections.append((title, found, marked_text))

    percent_ai_ml = (count_ai_ml_projects / count_projects * 100) if count_projects else 0
    print(f"Total projects processed: {count_projects}")
    print(f"AI/ML projects found: {count_ai_ml_projects} ({percent_ai_ml:.2f}%)")

    # Optionally write table to CSV - one boolean column per keyword, plus a final column indicating if *any* AI/ML keyword was found.
    if output_csv:
        header = ["Project Title"] + all_keywords + ["AI/ML"]
        with open(output_csv, "w", newline='', encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)

    # Optionally write the project text to Markdown, one section per project, keywords bolded. This makes it easier to skim 
    # the results and identify any false positives or missed projects.
    if output_md:
        with open(output_md, "w", encoding="utf-8") as f:
            f.write("# Keyword matches in {}\n\n".format(os.path.basename(pdf_path)))
            for title, found, marked_text in sections:
                f.write("## {}\n\n".format(title))
                f.write("Keywords found: {}\n\n".format(", ".join(found) if found else "none"))
                f.write(marked_text + "\n\n")
    return count_projects, count_ai_ml_projects