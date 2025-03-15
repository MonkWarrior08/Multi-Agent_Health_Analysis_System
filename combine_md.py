import os
from datetime import datetime
import re

def main():
    dir = "combine_files/files/journal-past"
    output = "combine_files/combine/journal-past.md"

    if not os.path.isdir(dir):
        print(f"Dir not exist: {dir}")
        return

    pattern = re.compile(r'(\d{2})-(\d{2})-(\d{4})\.md')

    file_date = []
    for file_name in os.listdir(dir):
        match = re.match(pattern, file_name)
        if match:
            day, month, year = match.groups()
            date_obj = datetime(int(year), int(month), int(day))
            file_date.append((date_obj, file_name))
    
    file_date.sort()

    with open(output, 'w', encoding='utf-8') as outfile:
        for date_obj, file_name in file_date:
            file_path = os.path.join(dir, file_name)
            date_str = date_obj.strftime("%B %d %Y")
            outfile.write(f"=={date_str}==\n\n")
                
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    outfile.write(content)
                outfile.write("\n\n")
            
            except Exception as e:
                print(f"Error reading {file_name}: {e} ")
        
        print(f"combine {len(file_date)} into {output}")

if __name__ == "__main__":
    main()
            

    
