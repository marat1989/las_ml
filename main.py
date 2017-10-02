import lasio # http://pythonhosted.org/lasio/
import pandas
import work_with_dir
import csv

# Сохранение Las файлов в виде csv, для дальнейшей обработки в pandas

kid_well = 0
kid_start = kid_well + 1
kid_end = kid_start + 1
kid_depth = kid_end + 1
kid_aps = kid_depth + 1
kid_rp = kid_aps + 1
kid_kp = kid_rp + 1
kid_kgl = kid_kp + 1
kid_kpr = kid_kgl + 1
kid_kvo = kid_kpr + 1
kid_kng = kid_kvo + 1
kid_lit = kid_kng + 1
kid_sat = kid_lit + 1


keys_dict = {kid_well:"well_name", kid_start:"start_m", kid_end:"stop_m", kid_depth: "DEPT", kid_aps: "aps",
            kid_rp: "rp", kid_kp: "kp", kid_kgl: "kgl", kid_kpr: "kpr", kid_kvo: "kvo", kid_kng: "kng", kid_lit: "lit",
            kid_sat: "satur"}

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
    l = lasio.read(main_dir + "\\" + file_name)



    # получить список кривых и их описание
    n = int(len(l["DEPT"]))
    print(n)
    for i in range(n):

        # print("%s\t[%s]\t%s\t%s" % (
        # curve.mnemonic, curve.unit, curve.value, curve.descr))
        #for curve in l.curves:
        d = dict.fromkeys(keys)
        d[keys_dict[kid_well]] = file_name[:-4]
        d[keys_dict[kid_start]] = l.well["STRT"].value
        d[keys_dict[kid_end]] = l.well["STOP"].value

        d[keys_dict[kid_depth]] = l[keys_dict[kid_depth]][i]
        d[keys_dict[kid_aps]] = l[keys_dict[kid_aps]][i]
        d[keys_dict[kid_rp]] = l[keys_dict[kid_rp]][i]
        d[keys_dict[kid_kp]] = l[keys_dict[kid_kp]][i]
        d[keys_dict[kid_kgl]] = l[keys_dict[kid_kgl]][i]
        d[keys_dict[kid_kpr]] = l[keys_dict[kid_kpr]][i]
        d[keys_dict[kid_kvo]] = l[keys_dict[kid_kvo]][i]
        d[keys_dict[kid_kng]] = l[keys_dict[kid_kng]][i]
        d[keys_dict[kid_lit]] = l[keys_dict[kid_lit]][i]
        d[keys_dict[kid_sat]] = l[keys_dict[kid_sat]][i]
        dict_list.append(d)
    dict_writer.writerows(dict_list)
    break

print("end save csv")
file.close()


# получить список кривых и их описание
# for curve in l.curves:
#    print("%s\t[%s]\t%s\t%s" % (
#    curve.mnemonic, curve.unit, curve.value, curve.descr))
