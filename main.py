import lasio # http://pythonhosted.org/lasio/
import pandas
import work_with_dir
import csv

# Сохранение Las файлов в виде csv, для дальнейшей обработки в pandas

kid_well = 0
kid_start = 1
kid_end = 2

keys_dict = {kid_well:"well_name", kid_start:"start_m", kid_end:"stop_m"}

main_dir = "D:\\NIPI\\machine learning\\tasks\\task 6\\Data\\las"
format = ".LAS"
res_files = work_with_dir.GetFilesInDir(main_dir, format)


file = open(main_dir + "\\" + "example.csv", "w", newline="")
keys = keys_dict.values()

dict_writer = csv.DictWriter(file, keys, delimiter = ";")
dict_writer.writeheader()


for file_name in res_files:
    print("From file" + file_name)

    dict_list = []
    # инициализируем словарь и заполняем в соответсви с ласом
    d = dict.fromkeys(keys)
    l = lasio.read(main_dir + "\\" + file_name)
    d[keys_dict[kid_well]] = file_name[:-4]
    d[keys_dict[kid_start]] = l.well["STRT"].value
    d[keys_dict[kid_end]] = l.well["STOP"].value

    dict_list.append(d)
    dict_writer.writerows(dict_list)


print("end save csv")
file.close()


# получить список кривых и их описание
# for curve in l.curves:
#    print("%s\t[%s]\t%s\t%s" % (
#    curve.mnemonic, curve.unit, curve.value, curve.descr))
