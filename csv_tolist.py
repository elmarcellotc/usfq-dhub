# Name: csv_tolist.py
# Author: Marcello Coletti; USFQ Data Hub
# Contact: coletti.marcello@gmail.com +593939076444

# This code is to pass Data Bases from .csv files to python lists. It can detect detect the encoding automatically.

def sep_detector(csv_firt_line): # This detecs if the separator is comma or dot comma.

    for sep in csv_firt_line:
        if sep == ',' or sep == ';':
            break
        
    if sep != ',' and sep != ';':
        print("Error: Didn't find csv separator")
        exit()
        
    return sep

def rows_generator(file_lines): # This function transform lines into lists. 
                                # also detects the separator.
                                # It does not select a column as index.
    
    sep = sep_detector(file_lines[0])
    rows = [None]*len(file_lines)
    
    for j in range(len(rows)):
        rows[j] = file_lines[j].split(sep)
        if len(rows[j]) != len(rows[0]):
            print(f'csv_tolist.py >> rows_generator() >> line 30: error at row {j}')
            exit()
        for g in range(len(rows[j])):
            try:
                rows[j][g] = float(rows[j][g])
            except:
                if rows[j][g].isnumeric():
                    try:
                        rows[j][g] = int(rows[j][g])
                    except:
                        None
            if rows[j][g] == ' ':
                rows[j][g] = None
        
    return rows[1:], rows[0]  

def open_csv(file_dir, encoding): # This function open the csv but it doesn't choose a row of column names
    
    file = open(file_dir, "r", encoding=encoding)
    data = file.read()
    lines = data.split("\n")

    for i in range(len(lines)):
        lines[i] = lines[i].replace('ï»¿','')
            
    rows, var_names = rows_generator(lines)

    file.close()
    return rows, var_names

def get_csv_varnames(file_dir): # This function open the csv and choose the first row as column names
    
    import chardet    
    result = open(file_dir, "r", errors='ignore').read()
    result = chardet.detect(result.encode())
    result = result['encoding']

    file = open(file_dir, "r", encoding=result)       
    data = file.read()
    var_names = data.split("\n")[0]
    
    var_names = var_names.replace('ï»¿','')
    
    return var_names.split(sep_detector(var_names)), result