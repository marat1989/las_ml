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

import re
import os
from scipy import interpolate

import numpy as np
def calc_stat(x_list):
    x_mean = np.mean(x_list)
    x_std = np.std(x_list)
    x_a0 = part_of_intersection(x_list, 0.)
    x_a_mean = part_of_intersection(x_list, x_mean)
    x_a_mean_std = part_of_intersection(x_list, x_mean + x_std)
    return [x_mean, x_std, x_a0, x_a_mean, x_a_mean_std]

def part_of_intersection(src_list, value):
    count_intersect = 0.
    for x in src_list:
        if (x >  value):
            count_intersect = count_intersect + 1
    if (count_intersect == 0):
        res = 0
    else:
        res = len(src_list)/count_intersect
    return res

def convert_list_to_diff(src_list):
    dst_list = []
    for i in range(1, len(src_list)):
        dst_list.append(src_list[i] - src_list[i - 1])
    return dst_list

def load_and_convert_to_interp(dev_path, well_name):
    # print('dev_path, is_exist = ', dev_path)
    is_exist = os.path.exists(dev_path + well_name + '.dev')
    f_spline = None
    if is_exist:
        f = open(dev_path + well_name + '.dev', 'r')
        well_num = 0
        md = []
        abs = []
        for line in f.readlines():
            if well_num > 16:
                # list = line.split(' ')
                # print(list)
                numbers = re.findall(r'[-]?[0-9]+.[0-9]+', line)
                md.append(float(numbers[0]))
                abs.append(float(numbers[3]))
            well_num = well_num +1
        f.close()
        f_spline = interpolate.interp1d(abs, md, kind = 'slinear', bounds_error=False)
    return [f_spline, is_exist]

from sklearn.preprocessing import MinMaxScaler

def ConvertDataToLearning(real_data_na, param_name, dev_path, min_count_val_in_data, count_val):
    well_name_list = real_data_na['WELL_NAME_UWI'].value_counts().index.tolist()
    x_values = []
    y_values = []
    y_names = []
    top_values = []
    bottom_values = []
    well_count = 0
    for well_name in well_name_list:
        if well_count % 20 == 0:
            print(well_count, ' of ', len(well_name_list))
        data_well = real_data_na[real_data_na['WELL_NAME_UWI'] == well_name]
        [f_spline, dev_is_exist] = load_and_convert_to_interp(dev_path, well_name)
        if (not dev_is_exist):
            continue
        bottom = f_spline(data_well['DEPTH_BOTTOM'].tolist()[0])
        top = f_spline(data_well['DEPTH_TOP'].tolist()[0])
        data_well_by_bound = data_well[(data_well['DEPT'] >= top) & (data_well['DEPT'] <= bottom)]
        x_arr = data_well_by_bound['DEPT']
        y_arr = data_well_by_bound[param_name]



        # print ('length of array depth', len(x_arr))
        # print(len(x_arr), len(y_arr))
        if (len(x_arr) < min_count_val_in_data):
            continue
        # масштабируем данные
        # scaler = MinMaxScaler()
        # y_arr = scaler.fit_transform(y_arr)

        # логорифмируем данные
        # y_arr = np.log(y_arr)

        top_values.append(top)
        bottom_values.append(bottom)
        f_spline = interpolate.interp1d(x_arr, y_arr, kind='quadratic')
        h_start = data_well_by_bound['DEPT'].min()
        h_end = data_well_by_bound['DEPT'].max()
        # print(h_start, h_end, top, bottom)
        h_step = (h_end - h_start) / count_val
        x_temp = []
        i = 0
        while (i < count_val):
            x_temp.append(float(f_spline(h_start + i * h_step)))
            i = i + 1
        x_values.append(x_temp)
        y_values.append(data_well['WC'].tolist()[0])
        y_names.append(data_well['WELL_NAME'].tolist()[0])

        #scaler = MinMaxScaler(feature_range=(0, 1))
        #data_well_by_bound[param_name] = scaler.fit_transform(data_well_by_bound[param_name])
        #x_val = data_well_by_bound[param_name].describe(percentiles=[0.05, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9, 0.95]).tolist()
        #x_values.append(x_val)
        #y_values.append(data_well['WC'].tolist()[0])
        #y_names.append(data_well['WELL_NAME'].tolist()[0])
        well_count = well_count + 1
    print('end ConvertDataToLearning')
    return [x_values, y_values, y_names, top_values, bottom_values]

# Ковертирует в расчет по данным перцентилей, максимальному и минимальному
def ConvertDataToLearningByStdParams(real_data_na, param_name, dev_path, min_count_val_in_data):
    well_name_list = real_data_na['WELL_NAME_UWI'].value_counts().index.tolist()
    x_values = []
    y_values = []
    y_names = []
    well_count = 0
    for well_name in well_name_list:
        if well_count % 20 == 0:
            print(well_count, ' of ', len(well_name_list))
        data_well = real_data_na[real_data_na['WELL_NAME_UWI'] == well_name]
        [f_spline, dev_is_exist] = load_and_convert_to_interp(dev_path, well_name)
        if (not dev_is_exist):
            continue
        bottom = f_spline(data_well['DEPTH_BOTTOM'].tolist()[0])
        top = f_spline(data_well['DEPTH_TOP'].tolist()[0])
        data_well_by_bound = data_well[(data_well['DEPT'] >= top) & (data_well['DEPT'] <= bottom)]
        x_arr = data_well_by_bound['DEPT']

        if (len(x_arr) < min_count_val_in_data):
            continue

        #scaler = MinMaxScaler(feature_range=(0, 1))
        #data_well_by_bound[param_name] = scaler.fit_transform(data_well_by_bound[param_name])
        x_val = data_well_by_bound[param_name].describe(percentiles=[0.05, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9, 0.95]).tolist()

        x_values.append(x_val)
        y_values.append(data_well['WC'].tolist()[0])
        y_names.append(data_well['WELL_NAME'].tolist()[0])
        well_count = well_count + 1
    print('end ConvertDataToLearning')
    print('x_values_length = ', len(x_values))
    return [x_values, y_values, y_names]

def ConvertDataToLearningStatParamsWithDiff(real_data_na, param_name, dev_path, min_count_val_in_data, count_val):
    well_name_list = real_data_na['WELL_NAME_UWI'].value_counts().index.tolist()
    x_values = []
    y_values = []
    y_names = []
    well_count = 0
    for well_name in well_name_list:
        if well_count % 20 == 0:
            print(well_count, ' of ', len(well_name_list))
        data_well = real_data_na[real_data_na['WELL_NAME_UWI'] == well_name]
        [f_spline, dev_is_exist] = load_and_convert_to_interp(dev_path, well_name)
        if (not dev_is_exist):
            continue
        bottom = f_spline(data_well['DEPTH_BOTTOM'].tolist()[0])
        top = f_spline(data_well['DEPTH_TOP'].tolist()[0])
        data_well_by_bound = data_well[(data_well['DEPT'] >= top) & (data_well['DEPT'] <= bottom)]
        x_arr = data_well_by_bound['DEPT']
        y_arr = data_well_by_bound[param_name]



        # print ('length of array depth', len(x_arr))
        # print(len(x_arr), len(y_arr))
        if (len(x_arr) < min_count_val_in_data):
            continue
        # масштабируем данные
        # scaler = MinMaxScaler()
        # y_arr = scaler.fit_transform(y_arr)

        # логорифмируем данные
        # y_arr = np.log(y_arr)

        f_spline = interpolate.interp1d(x_arr, y_arr, kind='slinear')
        h_start = data_well_by_bound['DEPT'].min()
        h_end = data_well_by_bound['DEPT'].max()
        # print(h_start, h_end, top, bottom)
        h_step = (h_end - h_start) / count_val
        x_stat = []
        x_temp = []
        x_temp_diff = []
        x_temp_diff_abs = []
        i = 0
        while (i < count_val):
            x_temp.append(float(f_spline(h_start + i * h_step)))
            i = i + 1

        x_temp_diff = convert_list_to_diff(x_temp)
        x_temp_diff_abs = list(np.abs(x_temp_diff))

        [x_mean, x_std, x_a_0, x_a_std, x_a_mean_std] = calc_stat(x_temp)
        [x_mean_d, x_std_d, x_a_0_d, x_a_std_d, x_a_mean_std_d] = calc_stat(x_temp_diff)
        [x_mean_abs, x_std_abs, x_a_0_abs, x_a_std_abs, x_a_mean_std_abs] = calc_stat(x_temp_diff_abs)

        x_stat.append(x_mean)
        x_stat.append(x_std)
        x_stat.append(x_a_0)
        x_stat.append(x_a_std)
        x_stat.append(x_a_mean_std)

        x_stat.append(x_mean_d)
        x_stat.append(x_std_d)
        x_stat.append(x_a_0_d)
        x_stat.append(x_a_std_d)
        x_stat.append(x_a_mean_std_d)

        x_stat.append(x_mean_abs)
        x_stat.append(x_std_abs)
        x_stat.append(x_a_0_abs)
        x_stat.append(x_a_std_abs)
        x_stat.append(x_a_mean_std_abs)



        x_values.append(x_stat)
        y_values.append(data_well['WC'].tolist()[0])
        y_names.append(data_well['WELL_NAME'].tolist()[0])

        #scaler = MinMaxScaler(feature_range=(0, 1))
        #data_well_by_bound[param_name] = scaler.fit_transform(data_well_by_bound[param_name])
        #x_val = data_well_by_bound[param_name].describe(percentiles=[0.05, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9, 0.95]).tolist()
        #x_values.append(x_val)
        #y_values.append(data_well['WC'].tolist()[0])
        #y_names.append(data_well['WELL_NAME'].tolist()[0])
        well_count = well_count + 1
    print('end ConvertDataToLearning')
    return [x_values, y_values, y_names]

def ConvertDataToLearningPerforation(real_data_na, param_name, min_count_val_in_data, count_val):
    well_name_list = real_data_na['WELL_NAME_UWI'].value_counts().index.tolist()
    x_values = []
    y_values = []
    y_names = []
    well_count = 0
    for well_name in well_name_list:
        if well_count % 20 == 0:
            print(well_count, ' of ', len(well_name_list))
        data_well = real_data_na[real_data_na['WELL_NAME_UWI'] == well_name]

        bottom = data_well['DEPTH_BOTTOM'].tolist()[0]
        top = data_well['DEPTH_TOP'].tolist()[0]
        data_well_by_bound = data_well[(data_well['DEPT'] >= top) & (data_well['DEPT'] <= bottom)]
        # data_well_by_bound.sort(['DEPT'], ascending=[False])
        x_arr = data_well_by_bound['DEPT'].tolist()
        y_arr = data_well_by_bound[param_name].tolist()



        # print ('length of array depth', len(x_arr))

        if (len(x_arr) < min_count_val_in_data):
            print('for well = ', well_name, ' len = ', len(x_arr))
            continue

        #print(x_arr)
        #print('well_name_uwi: ', well_name)
        f_spline = interpolate.interp1d(x_arr, y_arr, kind='slinear')
        h_start = data_well_by_bound['DEPT'].min()
        h_end = data_well_by_bound['DEPT'].max()
        # print(h_start, h_end, top, bottom)
        h_step = (h_end - h_start) / count_val
        x_temp = []
        i = 0
        while (i < count_val):
            x_temp.append(float(f_spline(h_start + i * h_step)))
            i = i + 1
        x_values.append(x_temp)
        y_values.append(data_well['WC'].tolist()[0])
        y_names.append(data_well['WELL_NAME'].tolist()[0])
        well_count = well_count + 1
    print('end ConvertDataToLearning')
    return [x_values, y_values, y_names]




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

def create_csv_from_las_modeling(las_dir, out_file_name):
    """Загружает данные (LAS) из папки и формирует csv файл """
    csv_out_file = data_dir + "\\" + out_file_name

    las_files = work_with_dir.GetFilesInDir(las_dir, ext_format)
    print('las_files:', las_files)
    print('las_dir:', las_dir)

    keys_list = ['well_name', 'DEPT', 'APS']
    csv_out_stream = open(csv_out_file, "w", newline="")
    dict_writer = csv.DictWriter(csv_out_stream, keys_list, delimiter=";")
    dict_writer.writeheader()

    for las_file_name in las_files:
        print("Convert " + las_file_name)

        dict_list = []
        # инициализируем словарь и заполняем в соответсви с ласом
        l = lasio.read(las_dir + "\\" + las_file_name)
        # получить список кривых и их описание
        count_keys = len(l.curves.keys())
        print(l.curves.keys())
        if (count_keys > 12):
            n = int(len(l['DEPT:1']))
            default = l.well["NULL"].value
            for i in range(n):
                d = dict.fromkeys(keys_list)
                d['well_name'] = las_file_name[:-4]
                d['DEPT'] = l['DEPT:1'][i]
                d['APS'] = l['aps:2'][i]
                dict_list.append(d)
            dict_writer.writerows(dict_list)

    print("end save csv")
    csv_out_stream.close()

def create_well_names_key(las_dir, out_file_name):
    """Загружает данные (LAS) из папки и формирует csv файл,
       с well_name и uwi"""
    csv_out_file = data_dir + "\\" + out_file_name

    las_files = work_with_dir.GetFilesInDir(las_dir, ext_format)
    print('las_files:', las_files)
    print('las_dir:', las_dir)

    keys_list = ['well_name', 'well_name_uwi']
    csv_out_stream = open(csv_out_file, "w", newline="")
    dict_writer = csv.DictWriter(csv_out_stream, keys_list, delimiter=";")
    dict_writer.writeheader()

    for las_file_name in las_files:
        print("Convert " + las_file_name)

        dict_list = []
        # инициализируем словарь и заполняем в соответсви с ласом
        l = lasio.read(las_dir + "\\" + las_file_name)
        # получить список кривых и их описание
        d = {}
        d['well_name'] = las_file_name[:-4]
        d['well_name_uwi'] = l.well[keys_dict[kid_well_dop_id]].value
        dict_list.append(d)
        dict_writer.writerows(dict_list)

    print("end save csv")
    csv_out_stream.close()


def revert_format(src_las_dir, dst_las_dir, save_names):
    """Загружает данные (LAS) из папки и формирует csv файл """
    las_files = work_with_dir.GetFilesInDir(src_las_dir, ext_format)
    print('las_files:', las_files)
    print('las_dir:', src_las_dir)

    keys_list = keys_dict.values()

    for las_file_name in las_files:
        src_las_file = src_las_dir + "\\" + las_file_name
        l = lasio.read(src_las_file)
        dst_las_file = dst_las_dir + "\\" + l.well['WELL'].value

        print("Convert " + las_file_name + " to " + l.well['WELL'].value)
        csv_out_stream = open(dst_las_file, "w", newline="")
        delete_list = []
        for curve in l.curves:
            # print ('Curve =', curve.mnemonic)
            name_exist = False
            for save_name in save_names:
                if (save_name == curve.mnemonic):
                    name_exist = True
            if name_exist == False:
                delete_list.append(curve.mnemonic)

        for del_elem in delete_list:
            l.delete_curve(del_elem)
        l.write(csv_out_stream, version=2.0, fmt="%10.5g")
        csv_out_stream.close
        # break


    print("end save new las format")

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

def convert_trace_to_dev(well_trace_data, path, ext):
    if os.path.exists(path) == False:
        os.mkdir(path)

    if well_trace_data.empty:
        return

    first_row = well_trace_data.iloc[0]
    filename = path + first_row['well_name'] + "." + ext
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

    f.write("\n#=====================================================")
    f.write("\n       MD              X              Y             Z ")
    f.write("\n#=====================================================")
    for idx, row in well_trace_data.iterrows():
        if ((str(row['MD']) != 'nan') and (str(row['X']) != 'nan') and (str(row['Y']) != 'nan')
            and (str(row['Z']) != 'nan')):
            f.write("\n " + str(row['MD']))
            f.write("   " + str(row['X']))
            f.write(" " + str(row['Y']))
            f.write(" " + str(row['Z']))
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
    src_las_dir = data_dir + "\\" + 'las'
    dst_las_dir = data_dir + "\\" + 'las_v_2'
    # create_csv_from_las(src_las_dir, las_out_file_name)
    # revert_format(src_las_dir, dst_las_dir)
    # create_well_names_key(src_las_dir, 'well_name_key.csv')

    src_las_dir = data_dir + '/gis_data/LAS'
    dst_las_dir = data_dir + '/gis_data/LAS_CORRECT'

    params_name = ['DEPT', 'CILD', 'GZ7', 'KINT', 'APS']
    revert_format(src_las_dir, dst_las_dir, params_name)

    # получить список кривых и их описание
    # for curve in l.curves:
    #    print("%s\t[%s]\t%s\t%s" % (
    #    curve.mnemonic, curve.unit, curve.value, curve.descr))
