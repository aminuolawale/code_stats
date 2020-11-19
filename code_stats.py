import os
import re
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()



def get_stats(project_root: str = os.getcwd(), entry_point: str = "api.py", route_function:str ="register_api") -> dict:
    # todo: handle wild card imports
    data = {}
    work_dir = project_root
    api_file = os.path.join(work_dir, entry_point)
    with open(api_file, "r") as a:
        api_txt = a.read()
        print(api_txt)
    raw_url_paths = re.findall(re.compile(f"{route_function}\([^)]+\)"), api_txt)
    print(raw_url_paths)
    url_paths = []
    for rpath in raw_url_paths:
        path_list = re.findall(re.compile('[\'\"][^\)]+prefix'), rpath)[0]
        path_list = path_list.replace("prefix","").strip()
        base_path = path_list.split(",")[0]
        base_path = base_path.replace('"', "")
        base_path = base_path.replace("'", "")
        url_paths.append(base_path)
    data.update(url_paths=url_paths)
    pprint(url_paths)
    resource_assignment_regex = re.compile("\w+\s*=\s*\w+Resource\([^\)]+\)")
    resource_assignments = re.findall(resource_assignment_regex, api_txt)
    for r in resource_assignments:
        resource_assignment_split_regex = re.compile("^\w+\s*=\s*")
        resource_initialization = re.split(resource_assignment_split_regex, r)[-1]
        resource = resource_initialization.split("(")[0]
        service_class = resource_initialization.split("(")[-1].split(",")[0].strip()
        resource_entry = data.get("resource", {})
        resource_entry.update({"service": service_class})
        data.update({resource: resource_entry})
        resource_import_regex = re.compile(f"resources.\w*\s+import[^\)\.]*{resource}")
        import_statement = re.findall(resource_import_regex, api_txt)[0]
        res_file_name = import_statement.split(" import ")[0].split(".")[-1].strip()
        resource_file = os.path.join(
            work_dir, "discovery", "resources", f"{res_file_name.lower()}.py")
        with open(resource_file, "r") as opened_resource_file:
            resource_file_string = opened_resource_file.read()
            class_definition = re.findall(re.compile("class %s\(\w+\):[\n\s^}]" % resource), resource_file_string)
            print(class_definition)
    return data


if __name__ == "__main__":
    ans = get_stats(os.getenv("PROJECT_DIR")
        )
    pprint(ans)