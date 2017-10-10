import lasio # http://pythonhosted.org/lasio/
import pandas
import work_with_dir
import csv
import math
import numpy as np

def CheckIsNan(x, default):
    # if math.isnan(x):
    #     return default
    # else:
    #   return x
    return x


# Сохранение Las файлов в виде csv, для дальнейшей обработки в pandas

# Имя скважины
kid_well = 0
# Глубина начала анализа
kid_start = kid_well + 1
# Конечная глубина
kid_end = kid_start + 1
# Шаг по глубине
kid_depth = kid_end + 1
# Альфа ПС
kid_aps = kid_depth + 1
# Удельное электрическое сопротивление
kid_rp = kid_aps + 1
# Коэфициент пористости
kid_kp = kid_rp + 1
# Коэфициент глинистости
kid_kgl = kid_kp + 1
# Коэфициент проницаемости
kid_kpr = kid_kgl + 1
# Коэфициент водонасыщенности
kid_kvo = kid_kpr + 1
# Коэфициент нефтегазонаысщенности
kid_kng = kid_kvo + 1
# Литология
kid_lit = kid_kng + 1
# Насыщение
kid_sat = kid_lit + 1


keys_dict = {kid_well:"well_name", kid_start:"STRT", kid_end:"STOP", kid_depth: "DEPT", kid_aps: "aps",
            kid_rp: "rp", kid_kp: "kp", kid_kgl: "kgl", kid_kpr: "kpr", kid_kvo: "kvo", kid_kng: "kng", kid_lit: "lit",
            kid_sat: "satur"}

data_dir = "..\\tasks\\task 6\\Data"
#las_dir = data_dir + "\\las"
ext_format = '.las'


def create_csv_from_las(las_dir, out_file_name):
    """Загружает данные (LAS) из папки и формирует csv файл """
    csv_out_file = data_dir + "\\" + out_file_name

    las_files = work_with_dir.GetFilesInDir(las_dir, ext_format)
    print('las_files:', las_files)
    print('las_dir:', las_dir)

    keys_list = keys_dict.values()
    csv_out_stream = open(csv_out_file, "w", newline="")
    dict_writer = csv.DictWriter(csv_out_stream, keys_list, delimiter=";")
    dict_writer.writeheader()

    for las_file_name in las_files:
        print("Convert " + las_file_name)

        dict_list = []
        # инициализируем словарь и заполняем в соответсви с ласом
        l = lasio.read(las_dir + "\\" + las_file_name)
        # получить список кривых и их описание
        n = int(len(l["DEPT"]))
        default = l.well["NULL"].value
        for i in range(n):
            # print("%s\t[%s]\t%s\t%s" % (
            # curve.mnemonic, curve.unit, curve.value, curve.descr))
            #for curve in l.curves:
            d = dict.fromkeys(keys_list)
            d[keys_dict[kid_well]] = las_file_name[:-4]
            d[keys_dict[kid_start]] = l.well[keys_dict[kid_start]].value
            d[keys_dict[kid_end]] = l.well[keys_dict[kid_end]].value

            d[keys_dict[kid_depth]] = CheckIsNan(l[keys_dict[kid_depth]][i], default)
            d[keys_dict[kid_aps]] = CheckIsNan(l[keys_dict[kid_aps]][i], default)
            d[keys_dict[kid_rp]] = CheckIsNan(l[keys_dict[kid_rp]][i], default)
            d[keys_dict[kid_kp]] = CheckIsNan(l[keys_dict[kid_kp]][i], default)
            d[keys_dict[kid_kgl]] = CheckIsNan(l[keys_dict[kid_kgl]][i], default)
            d[keys_dict[kid_kpr]] = CheckIsNan(l[keys_dict[kid_kpr]][i], default)
            d[keys_dict[kid_kvo]] = CheckIsNan(l[keys_dict[kid_kvo]][i], default)
            d[keys_dict[kid_kng]] = CheckIsNan(l[keys_dict[kid_kng]][i], default)
            d[keys_dict[kid_lit]] = CheckIsNan(l[keys_dict[kid_lit]][i], default)
            d[keys_dict[kid_sat]] = CheckIsNan(l[keys_dict[kid_sat]][i], default)
            dict_list.append(d)
        dict_writer.writerows(dict_list)

    print("end save csv")
    csv_out_stream.close()

petrel_out_file_name = "petrel_out.csv"
csv_petrel_out_full_path = data_dir + "\\" + petrel_out_file_name

las_out_file_name = "las_out.csv"
csv_las_out_full_path = data_dir + "\\" + las_out_file_name

if __name__ == "__main__":

    # Для ковертации папки petrel
    # print('start create csv from petrel')
    # petrel_dir = data_dir + "\\" + 'petrel'
    # create_csv_from_las(petrel_dir, petrel_out_file_name)

    # для конвертации папки las
    print('start create_csv from las')
    las_dir = data_dir + "\\" + 'las'
    create_csv_from_las(las_dir, las_out_file_name)



    # получить список кривых и их описание
    # for curve in l.curves:
    #    print("%s\t[%s]\t%s\t%s" % (
    #    curve.mnemonic, curve.unit, curve.value, curve.descr))
