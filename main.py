import lasio # http://pythonhosted.org/lasio/
import pandas
import work_with_dir
import csv
import math
import numpy as np
import os

def CheckIsNan(x, default):
    # if math.isnan(x):
    #     return default
    # else:
    #   return x
    return x


# Сохранение Las файлов в виде csv, для дальнейшей обработки в pandas

# Имя скважины
kid_well = 0
# Кодовой имя (для того чтобы объединить сперфорациями )
kid_well_dop_id = kid_well + 1
# Глубина начала анализа
kid_start = kid_well_dop_id + 1
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
            kid_sat: "satur", kid_well_dop_id: 'UWI'}

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
            d[keys_dict[kid_well_dop_id]] = l.well[keys_dict[kid_well_dop_id]].value
            d[keys_dict[kid_start]] = l.well[keys_dict[kid_start]].value
            d[keys_dict[kid_end]] = l.well[keys_dict[kid_end]].value

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

    print("end save csv")
    csv_out_stream.close()

def cut_data_frame_by_satur(well_las_data):
    cutted = well_las_data[well_las_data['satur'] > 0]
    if cutted.empty:
        return [], False
    h_start = cutted.iloc[0]['DEPT']
    h_end = cutted.iloc[len(cutted) - 1]['DEPT']
    res = well_las_data[(well_las_data['DEPT'] >= h_start) & (well_las_data['DEPT'] <= h_end)]
    return res, True


def check_nan_in_data_frame(well_las_data, check_columns, limit=10):
    rows_count = well_las_data.count().max()
    for col in check_columns:
        jd = well_las_data[[col]].isnull()
        nan_cnt = 0
        is_bad_data = False
        for i in range(0, rows_count):
            if (jd.iloc[i, 0]) and (well_las_data.iloc[i, 12] > 0):
                nan_cnt = nan_cnt + 1
            else:
                nan_cnt = 0
            if nan_cnt / rows_count > limit / 100.0:
                return [], False

    return well_las_data, True


def convert_las_to_dev(well_las_data, path, ext, column_name):
    if os.path.exists(path) == False:
        os.mkdir(path)

    if well_las_data.empty:
        return
    first_row = well_las_data.iloc[0]
    filename = path + column_name + "_" + first_row['well_name'] + "." + ext
    f = open(filename, 'w')
    f.write("# WELL TRACE FROM PETREL")
    f.write("\n# WELL NAME:  ")
    f.write(first_row['well_name'])
    f.write("\n# WELL HEAD X-COORDINATE: ")
    f.write(str(first_row['X']))
    f.write(" (m)")
    f.write("\n# WELL HEAD Y-COORDINATE: ")
    f.write(str(first_row['Y']))
    f.write(" (m)")

    f.write("\n# WELL DATUM (KB, Kelly bushing, from MSL): 115.89000000 (m)")
    f.write("\n# WELL TYPE:              UNKNOWN")
    f.write("\n# MD AND TVD ARE REFERENCED (=0) AT WELL DATUM AND INCREASE DOWNWARDS")
    f.write("\n# ANGLES ARE GIVEN IN DEGREES")
    f.write("\n# XYZ TRACE IS GIVEN IN COORDINATE SYSTEM Urmanskoe [DBX,600001]")
    f.write("\n# AZIMUTH REFERENCE TRUE NORTH")
    f.write("\n# DX DY ARE GIVEN IN GRID NORTH IN m-UNITS")
    f.write("\n# DEPTH (Z, tvd_z) GIVEN IN m-UNITS")

    f.write(
        "\n#======================================================================================================================================")
    f.write(
        "\n       MD              X              Y             Z           TVD           DX           DY          AZIM          INCL          DLS")
    f.write(
        "\n#======================================================================================================================================")
    for idx, row in well_las_data.iterrows():
        if str(row[column_name]) != "nan":
            f.write("\n " + str(row['DEPT']))
            f.write("   " + str(row['X']))
            f.write(" " + str(row['Y']))
            f.write(" " + str(row[column_name]))
            f.write(" 0 0 0 0 0 0 ")
    f.close

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
