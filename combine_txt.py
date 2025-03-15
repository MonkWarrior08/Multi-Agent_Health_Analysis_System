import os 
import re
from datetime import datetime

def main():
    dir = "files/journal-app"
    output = "combine/journal-app.txt"

    if not os.path.isdir(dir):
        print("Dir not found: {dir}")
        return
    
    txt_files = [f for f in os.listdir(dir)]

    file_date = []
    for file_name in txt_files:
        match = re.match(r'(\d{2})-(\d{2})-(\d{4})', file_name)
        if match:
            day, month, year = match.groups()
            date_obj = datetime(int(year), int(month), int(day))
            file_date.append((date_obj, file_name))
    
    file_date.sort()

    with open(output, 'w', encoding='utf-8') as outfile:
        outfile.write("===Journal-app entries===\n\n")
        
        for date_obj, file_name in file_date:
            file_path = os.path.join(dir, file_name)
            date = date_obj.strftime("%B %d, %Y")
            outfile.write(f"=={date}==\n\n")

            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    outfile.write(content)
                
                outfile.write("\n\n")
            except Exception as e:
                print(f"Error reading {file_name}: {e}")
    print(f"combine {len(file_date)} into {output}")

if __name__ == "__main__":
    main()
