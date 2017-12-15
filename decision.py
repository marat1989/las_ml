import csv
import lasio
import os
import numpy as np
import pandas as pd
from scipy import interpolate

kid_well = 0
kid_depth = 2
kid_aps = 3
kid_kgl = 4
kid_gz5 = 5

kid_wc_str = 'WC'
kid_top_str = 'DEPTH_TOP'
kid_bottom_str = 'DEPTH_BOTTOM'

keys_dict_temp = {kid_well:"WELL_NAME", kid_depth: "DEPT", kid_kgl: "KGL", kid_aps: "APS",
                  kid_gz5: "GZ5"}

ext_format = '.las'
input_csv_data = 'input_data.csv'
input_csv_data_for_model = 'input_data_for_model.csv'
input_csv_top = 'top.csv'
input_csv_bottom = 'bottom.csv'
input_csv_wc = 'wc.csv'

def GetFilesInDir(path_dir, file_format = ''):
    #Получаем список файлов в переменную files
    files = os.listdir(path_dir)
    lower_files = []
    for file in files:
        lower_files.append(str(file.lower()))
    #Фильтруем список
    res_files = filter(lambda x: x.endswith(file_format), lower_files)
    return res_files


def get_curve_value(las, curve_name, row_idx):
    if las[curve_name] is None:
        if las[curve_name.lower()] is None:
            return None
        else:
            return las[curve_name.lower()][row_idx]
    else:
        return las[curve_name][row_idx]

def create_csv_from_las(las_dir, keys_dict_temp):
    """Загружает данные (LAS) из папки и формирует csv файл """
    csv_out_file = las_dir + '\\' + input_csv_data
    las_files = GetFilesInDir(las_dir, ext_format)
    keys_list = keys_dict_temp.values()
    csv_out_stream = open(csv_out_file, "w", newline="")
    dict_writer = csv.DictWriter(csv_out_stream, keys_list, delimiter=";")
    dict_writer.writeheader()

    for las_file_name in las_files:
        dict_list = []
        # инициализируем словарь и заполняем в соответсви с ласом
        l = lasio.read(las_dir + "\\" + las_file_name)
        # получить список кривых и их описание

        n = 0
        if l[keys_dict_temp[kid_depth]] is None:
            n = len(l[keys_dict_temp[kid_depth].lower()])
        else:
            n = len(l[keys_dict_temp[kid_depth]])

        for i in range(n):
            d = dict.fromkeys(keys_list)
            d[keys_dict_temp[kid_well]] = las_file_name[:-4]
            d[keys_dict_temp[kid_depth]] = get_curve_value(l, keys_dict_temp[kid_depth], i)
            d[keys_dict_temp[kid_aps]] = get_curve_value(l, keys_dict_temp[kid_depth], i)
            d[keys_dict_temp[kid_kgl]] = get_curve_value(l, keys_dict_temp[kid_depth], i)
            d[keys_dict_temp[kid_gz5]] = get_curve_value(l, keys_dict_temp[kid_depth], i)
            dict_list.append(d)
        dict_writer.writerows(dict_list)
    csv_out_stream.close()
    return csv_out_file


def to_scale_interpolate_data(full_data, analized_curve_name, dev_path, scale_value_count = 100,
                              is_have_target_value = False):
    well_name_list = full_data[keys_dict_temp[kid_well]].value_counts().index.tolist()
    x_values = []
    y_values = []
    well_names = []
    count_val = scale_value_count
    well_count = 0
    min_count_val_in_data = 10
    print(' loop start')
    for well_name in well_name_list:
        if well_count % 500 == 0:
            print(' ', well_count, ' of ', len(well_name_list))
        data_well = full_data[full_data[keys_dict_temp[kid_well]] == well_name]
        f_spline = load_and_convert_to_interp(dev_path, well_name)
        if f_spline is None:
            continue
        bottom = f_spline(data_well[kid_bottom_str].tolist()[0])
        top = f_spline(data_well[kid_top_str].tolist()[0])
        data_well_by_bound = data_well[(data_well[keys_dict_temp[kid_depth]] >= top)
                                       & (data_well[keys_dict_temp[kid_depth]] <= bottom)]
        x_arr = data_well_by_bound[keys_dict_temp[kid_depth]]
        y_arr = data_well_by_bound[analized_curve_name]

        if (len(x_arr) < min_count_val_in_data):
            continue

        f_spline = interpolate.interp1d(x_arr, y_arr, kind='slinear')
        h_start = data_well_by_bound[keys_dict_temp[kid_depth]].min()
        h_end = data_well_by_bound[keys_dict_temp[kid_depth]].max()

        h_step = (h_end - h_start) / count_val
        x_temp = []
        i = 0
        while(i<count_val):
            x_temp.append(float(f_spline(h_start + i * h_step)))
            i = i + 1
        x_values.append(x_temp)
        well_names.append(well_name)
        if (is_have_target_value):
            y_values.append(data_well[kid_wc_str].tolist()[0])
        well_count = well_count + 1
    print(' loop end')
    return x_values, well_names, y_values

import lasio
import re
def load_and_convert_to_interp(dev_path, well_name):
    if os.path.exists(dev_path + well_name + '.dev') == False:
        return None

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
    return f_spline

def generate_x_values(las_dir, curve_name):
    full_input_data_file_name = las_dir + '\\' + input_csv_data
    output_data_file_name =  las_dir + '\\' + input_csv_data_for_model
    full_input_data = pd.read_csv(full_input_data_file_name, delimiter=';')

    bottom = pd.read_csv(las_dir + '\\' + input_csv_bottom, delimiter=';')
    top = pd.read_csv(las_dir + '\\' + input_csv_top, delimiter=';')

    is_have_wc = False
    if os.path.exists(las_dir + '\\' + input_csv_wc):
        is_have_wc = True
        data_wc = pd.read_csv(las_dir + '\\' + input_csv_wc, delimiter=';')

    if is_have_wc:
        full_input_data = pd.merge(data_wc, full_input_data, on=keys_dict_temp[kid_well])
    full_input_data = pd.merge(full_input_data, top, on=keys_dict_temp[kid_well])
    full_input_data = pd.merge(full_input_data, bottom, on=keys_dict_temp[kid_well])

    x_vals, well_names, y_vals = to_scale_interpolate_data(full_input_data, curve_name,
                                                           dev_path=las_dir + '\\dev\\',
                                                           is_have_target_value=is_have_wc)
    save_x = pd.DataFrame(x_vals, columns=[curve_name + str(z) for z in range(0, len(x_vals[0]))])
    save_y = pd.DataFrame(y_vals, columns=[kid_wc_str])
    save_wells = pd.DataFrame(well_names, columns=[keys_dict_temp[kid_well]])

    if is_have_wc:
        output_data = pd.merge(save_wells, save_y, left_index=True, right_index=True)
        output_data = pd.merge(output_data, save_x, left_index=True, right_index=True)
        output_data.to_csv(output_data_file_name, sep=';', index=False)
    else:
        output_data = pd.merge(save_wells, save_x, left_index=True, right_index=True)
        output_data.to_csv(output_data_file_name, sep=';', index=False)
    return output_data_file_name

def classify_neural(las_dir, input_df):
    from keras.models import model_from_json
    # Загружаем данные об архитектуре сети из файла json
    json_file = open("fake_aps_model.json", "r")
    loaded_model_json = json_file.read()
    json_file.close()
    # Создаем модель на основе загруженных данных
    model = model_from_json(loaded_model_json)
    # Загружаем веса в модель
    model.load_weights("fake_aps_model.h5")
    # Компилируем модель
    model.compile(loss="mse", optimizer="adam", metrics=['mae'])

    wells = input_df[keys_dict_temp[kid_well]]
    del input_df[keys_dict_temp[kid_well]]
    x_values = input_df
    x_values = np.array(x_values)
    print(x_values.shape)

    y_predict = model.predict(x_values)

    pred_data_filename = las_dir + '\\result_classify_neural.csv'
    pred_data = pd.DataFrame({keys_dict_temp[kid_well]: wells, 'y_predict': y_predict[:, 0]})
    pred_data.to_csv(pred_data_filename, index=False, sep=';')
    return pred_data_filename


def classify(path):

    # print('Start convert las to csv. Path:' + path)
    # res_file = create_csv_from_las(path, keys_dict_temp)
    # print('End convert las to csv. Result: ' + res_file)

    print('Generate train/test data')
    res_file = generate_x_values(path, keys_dict_temp[kid_aps])
    print('End generate train\test data. Result: ' + res_file)

    input_data = pd.read_csv(res_file, delimiter=';')

    print('neural network start')
    res_file = classify_neural(path, input_data)
    print('neural network end. Result: ' + res_file)


if __name__ == "__main__":
    classify('C:\\WORK\\ML\\result')
