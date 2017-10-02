import lasio
import pandas
import work_with_dir
import csv
keys_tuple = ("well_name", "start_m", "stop_m")

main_dir = "D:\\NIPI\\machine learning\\tasks\\task 6\\Data\\las"
format = ".LAS"
res_files = work_with_dir.GetFilesInDir(main_dir, format)
file = open(main_dir + "\\" + "example.csv", "w", newline="")
for file_name in res_files:
    dict_list = []
    # инициализируем словарь
    d = dict.fromkeys(keys_tuple)
    dict_list.append(d)
    l = lasio.read(main_dir + "\\" + file_name)
    print("In file" + file_name)
    # получить список кривых и их описание
    #for curve in l.curves:
    #    print("%s\t[%s]\t%s\t%s" % (
    #    curve.mnemonic, curve.unit, curve.value, curve.descr))
    d["well_name"] = file_name[:-4]
    d["start_m"] = l.well["STRT"].value
    d["stop_m"] = l.well["STOP"].value

    keys = d.keys()
    print(d.keys())
    dict_writer = csv.DictWriter(file, keys_tuple, delimiter = ";")
    dict_writer.writeheader()
    dict_writer.writerows(dict_list)
    print("\n\n")
    break
file.close()


