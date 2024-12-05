from Bio import SeqIO
from datetime import date, datetime


def ofunc(fname, mode):
    '''
    custom file open that chooses between gzip and regular open
    '''
    if fname[-3:]=='.gz':
        import gzip
        return gzip.open(fname,mode)
    else:
        return open(fname,mode)

class filter:
    def __init__(self, 
                 filename : str, 
                 header_categories : dict[str,int] = {"name":0}, 
                 header_sep : str = "|"):
        self.input_filename : str = filename
        self.sep : str = header_sep
        self.cats : dict[str,int] = header_categories

    def set_input(self, filename : str):
        self.input_filename = filename

    def add_header_column(self, 
                          name, 
                          idx):
        self.cats[name]=idx
       
    def apply(self, 
              filter_fun, 
              output_filename : str):
        if filter_fun == None:
            print("no filtering fun, aborted apply")
            return
        with open(output_filename, "wt") as out_file:
            to_write = []
            with ofunc(self.input_filename, "rt") as in_file:
                for record in SeqIO.parse(in_file, 'fasta'):
                    if filter_fun(record.name):
                        to_write.append(record)
            SeqIO.write(to_write, out_file, "fasta")

    def filter_date(self, 
                    start_date : str, 
                    end_date : str, 
                    cat : str = "date"):
        if cat not in self.cats.keys():
            print(f"INIT/INPUT ERROR: no {cat} category index set")
            return None
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        date_getter = lambda s : datetime.fromisoformat(s.split(self.sep)[self.cats[cat]])
        return lambda s : start <= date_getter(s) and date_getter(s) < end
        
class flu_filter(filter):
    def __init__(self, 
                 filename : str, 
                 header_categories : dict[str,int] = {"name":0}, 
                 header_sep : str = "|",
                 season_start = "09-01",
                 season_end = "05-31"):
        super().__init__(filename, header_categories, header_sep)
        self.season_start = season_start
        self.season_end = season_end
    def filter_seasons(self, 
                       year_from : int, 
                       year_to : int, 
                       date_cat : str = "date"):
        if year_from>=year_to:
            print(f"INPUT ERROR: starting year {year_from} goes after ending year {year_to} or is equal to it")
            return None
        return self.filter_date(str(year_from-1)+"-"+self.season_start,
                                str(year_to-1)+"-"+self.season_end,
                                date_cat)
    
f = flu_filter("RF-2009-2024_noDup.fasta",
               {"name" : 0,
                "date" : 1,
                "EPI_ISL" : 2})

import os
for y in range(2010, 2025):
    if y!=2021 and y!=2023:
        f.apply(f.filter_seasons(2009, y), f"./FitnessInference/in/RF-2009-{y}.fasta")