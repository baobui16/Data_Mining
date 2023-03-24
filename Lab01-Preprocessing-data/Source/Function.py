import csv
from Column import Column

# this dataframe is based on a list of columns
class Function:
    def __init__(self, filename):
        self.filename = filename
        csv_file = open(filename,"r")
        reader = csv.reader(csv_file)

        # Read header row as column names
        self.names = reader.__next__()
        self.width = len(self.names)

        #Store data by a list of columns
        self.cols = list()
        for i in range(self.width):
            col = Column(self.names[i])
            self.cols.append(col)

        # Read data by lines
        for line in reader:
            for index, value in enumerate(line):
                self.cols[index].add_data(value)

        self.height = reader.line_num - 1
        csv_file.close()

    
    # save to file
    def save_file(self, filename):
        if filename is None:
            # modify the opened file by default
            filename = self.filename

        csv_file = open(filename,"w")
        writer = csv.writer(csv_file)
        writer.writerow(self.names) # write header of csv file

        for row in range(self.height):
            line = []
            for column in self.cols:
                line.append(column.data[row])
            writer.writerow(line)
        csv_file.close()
        print('Saved result in', filename)

    # Function 1 : Extract columns with missing values
    def list_missing(self, args):
        print("There are missing values in columns: ")
        for cols in self.cols:
            if len(cols.missing_value_indexes) != 0:
                print(cols.name)

    # Function 2: Count the number of lines with missing data.
    def count_missing(self, args):
        indexes = set()
        for col in self.cols:
            for row_index in col.missing_value_indexes:
                indexes.add(row_index)
        print('The number of rows with missing value:', len(indexes))

    # check column is valid and return the corresponding column
    def check_valid(self, names):
        if names is None:                     
            return self.cols
        valid_columns = list()
        for name in names:
            try:
                index = self.names.index(name)
            except: continue
            valid_columns.append(self.cols[index])
        return valid_columns

    #Function 3
    def impute(self, args):
        # check the value of method: median, mean, or none
        if args.method not in [None, 'median', 'mean']:
            print("Invalid method")
            return
        valid_columns = self.check_valid(args.columns)
        # impute
        for column in valid_columns:
            impute_value = column.get_mmm(args.method)
            if isinstance(impute_value, list):
                # when attribute is categorical, the value can be modes 
                step = 0
                for position in column.missing_value_indexes:
                    column.data[position] = impute_value[step]
                    # alternate between the modes
                    step += 1
                    step = step % len(impute_value)
            else:
                # the impute value can be mean or median here
                for position in column.missing_value_indexes:
                    column.data[position] = impute_value
            column.missing_value_indexes = []

        self.save_file(args.outfile)

    #Function 4: Deleting rows containing more than a particular number of missing values
    def remove_row(self, args):
        threshold = (float)(args.threshold)/100
        counter = dict()
         # Count missing values by row index       
        for col in self.cols:
            for i in col.missing_value_indexes:
                counter[i] = counter.get(i, 0) + 1

        for index in range(self.height-1, -1, -1):
            if counter[index]/self.width > threshold:
                for col in self.cols:
                  del col.data[index]
                try:
                    col.missing_value_indexes.remove(index)
                except: pass
                self.height -= 1
        self.save_file(args.outfile)

    #Function 5: Deleting columns containing more than a particular number of missing values
    def remove_col(self, args):
        threshold = (float)(args.threshold)/100
        for index in range(self.width -1, -1, -1):
            if len(self.cols[index].missing_value_indexes)/self.height > threshold:
                del self.cols[index]
                del self.names[index]

        self.width = len(self.names)
        self.save_file(args.outfile)

    # Checking if ith row and jth row are the same
    def are_same(self, i, j):
        for col in self.cols:
            if col.data[i] != col.data[j]:
                return False
        return True

    #Function 6: Delete duplicate samples.
    def remove_duplicate(self, args):
        for i in range(self.height-1, -1, -1):
            for j in range(i-1, -1, -1):
                if self.are_same(i, j):
                #    self.remove_a_row(i)
                #    break
                    for col in self.cols:
                        del col.data[i]
                        try:
                            col.missing_value_indexes.remove(i)
                        except: pass
                    self.height -= 1
                    break
        
        self.save_file(args.outfile)

    #Function 7: Normalize a numeric attribute using min-max and Z-score methods
    def normalize(self, args):
        if args.method not in [None, 'min-max', 'Z-score']:
            print('Invalid method')
            return
        # Check if method is none => min-max
        if args.method is None:
            method = 'min-max' 
        else: 
            method = args.method
        valid_columns = self.check_valid(args.columns)

        for col in valid_columns:
            if col.dtype == 'numeric':
                col.normalize(method)
        self.save_file(args.outfile)

    #Function 8: Performing addition, subtraction, multiplication, and division between two numerical attributes.
    def calculate(self, args):
        new_col, formula = args.formula.split('=')
        # list attribute names from expression
        attrs = list()
        attr = ''
        for char in formula:
            if char in '()+-*/':
                if attr != '':
                    attrs.append(attr)
                attr = ''
            else: attr += char
        if attr != '':
            attrs.append(attr)
        # Get the corresponding column object
        cols = self.check_valid(attrs)
        # check the validity
        if len(cols) != len(attrs):
            print('There are invalid attributes in the expression')
            return
        for col in cols:
            if col.dtype == 'categorical':
                print('There are categorical attributes in the expression')
                return
        # Calulate
        for ind, entry in enumerate(attrs):
            formula = formula.replace(entry, 'cols['+str(ind)+']')
        result = eval(formula)
        # Add new returned column to dataframe and save
        self.names.append(new_col)
        self.cols.append(result)
        self.width += 1

        self.save_file(args.outfile)
        


            




        




        



    









    



        






    




