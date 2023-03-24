class Column:
    def __init__(self, name):
        self.name = name
        self.data = []
        self.dtype = 'numeric'
        self.length = 0
        self.missing_value_indexes = []

    def add_data(self, value):
        try:
            value = (float)(value)
        except ValueError:
            if len(value) == 0:
                value = None
                self.missing_value_indexes.append(self.length)
            else: self.dtype = 'categorical'

        self.length += 1
        self.data.append(value)

    # get mean or median or mode, based on method and data type
    def get_mmm(self, method=None):
        filtered = [value for value in self.data if value is not None]
        if not filtered:
            return 0

        if self.dtype == 'numeric':
            if method is None or method == 'median':
                filtered.sort()
                half = len(filtered) // 2
                if len(filtered) % 2 == 0:
                    return (filtered[half-1] + filtered[half]) / 2
                else:
                    return filtered[half]
            elif method == 'mean':
                return sum(filtered) / len(filtered)
        counter = {}
        max_value = 0
        modes = []
        
        for value in filtered:
            if value not in counter:
                counter[value] = 1
            else:
                counter[value] += 1
            if counter[value] > max_value:
                max_value = counter[value]
                modes = [value]
            elif counter[value] == max_value:
                modes.append(value)
        return modes

    def normalize(self, method):
        # remove None type elements and store to a temp list
        tmp = [val for val in self.data if val is not None]
        if len(tmp) == 0:
            # do nothing with column with full of Nones
            return

        # calculate min, max, mean, and standard deviation once
        minimum = min(tmp)
        maximum = max(tmp)
        mean = sum(tmp) / len(tmp)
        stdev = (sum((val - mean) ** 2 for val in tmp) / (len(tmp) - 1)) ** 0.5

        # normalize data in-place based on method min-max and Z-score
        if method == 'min-max':
            if minimum != maximum:
                for i in range(len(self.data)):
                    if self.data[i] is not None:
                        self.data[i] = (self.data[i] - minimum) / (maximum - minimum)
        elif method == 'Z-score':
            if stdev != 0:
                for i in range(len(self.data)):
                    if self.data[i] is not None:
                        self.data[i] = (self.data[i] - mean) / stdev
        else:
            raise ValueError('Invalid normalization method')
        return

    # define operators between columns
    # e.g. column = column+column as below
    def __add__(self, other):
        result = Column('')
        for i in range(self.length):
            if self.data[i] is None or other.data[i] is None:
                result.add_data('')
            else: result.add_data(self.data[i]+other.data[i])
        return result

    def __sub__(self, other):
        result = Column('')
        for i in range(self.length):
            if self.data[i] is None or other.data[i] is None:
                result.add_data('')
            else: result.add_data(self.data[i]-other.data[i])
        return result

    def __mul__(self, other):
        result = Column('')
        for i in range(self.length):
            if self.data[i] is None or other.data[i] is None:
                result.add_data('')
            else: result.add_data(self.data[i]*other.data[i])
        return result
    
    def __truediv__(self, other):
        result = Column('')
        for i in range(self.length):
            try:
                result.add_data(self.data[i]/other.data[i])
            except: result.add_data('')
        return result

