import re
from typing import Tuple, List

def extract_provider_name_and_version(uri: str) -> Tuple[str, str, str]:
    # registry://providers/<provider_namespace>/namespace/<provider_name>/version/<provider_version>
    parts = uri.split("/")
    if len(parts) < 5:
        raise ValueError("invalid provider URI format")
    return parts[-5], parts[-3], parts[-1]

def contains_slug(source_name: str, slug: str) -> bool:
    pattern = f".*{re.escape(slug)}.*"
    return bool(re.search(pattern, source_name, re.IGNORECASE))

def is_valid_provider_version_format(version: str) -> bool:
    semver_regex = r"^v?(\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?)$"
    return bool(re.match(semver_regex, version))

def is_valid_provider_document_type(doc_type: str) -> bool:
    valid_types = ["resources", "data-sources", "functions", "guides", "overview", "actions", "list-resources"]
    return doc_type in valid_types

def is_v2_provider_document_type(doc_type: str) -> bool:
    v2_categories = ["guides", "functions", "overview", "actions", "list-resources"]
    return doc_type in v2_categories

def extract_readme(readme: str) -> str:
    if not readme:
        return ""
    
    lines = readme.split("\n")
    header_found = False
    result = []
    header_regex = r"^#+\s?"
    
    for line in lines:
        if re.match(header_regex, line):
            if header_found:
                break
            header_found = True
        result.append(line)
        
    return "\n".join(result).strip()
