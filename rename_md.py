import os
import re
import shutil

def main():
    dir = "combine_files/files/journal-past"

    month_map = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05",
        "Jun": "06", "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10",
        "Nov": "11", "Dec": "12"
    }

    if not os.path.exists(dir):
        print(f"Dir not found: {dir}")
        return
    
    pattern = re.compile(r'(\d{4})-([A-Za-z]{3})-(\d{2}).*\.md')

    for file_name in os.listdir(dir):
        match = pattern.match(file_name)
        if match:
            year = match.group(1)
            month = match.group(2)
            day = match.group(3)

            month_num = month_map[month]
            new_file_name = f"{day}-{month_num}-{year}.md"

            source_path = os.path.join(dir, file_name)
            new_path = os.path.join(dir, new_file_name)
            shutil.move(source_path, new_path)

    print(f"Completed")

if __name__ == "__main__":
    main()