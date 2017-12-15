import main
import csv
import lasio

kid_well = 0
kid_uwi = 1
kid_depth = 2
kid_calc = 3


# keys_dict_temp = {kid_well:"WELL_NAME", kid_depth: "DEPT", kid_calc: "CILD", kid_uwi:"WELL_NAME_UWI"}
def exist_val_in_list(val, list):
    val_exist = False
    for list_v in list:
        if list_v == val:
            val_exist = True
            break
    return val_exist


def create_csv_from_las(las_dir, out_file_name, keys_dict, wc_well_names=[]):
    """Загружает данные (LAS) из папки и формирует csv файл """
    csv_out_file = out_file_name

    las_files = main.work_with_dir.GetFilesInDir(las_dir, main.ext_format)
    # print('las_files:', las_files)
    # print('las_dir:', las_dir)

    keys_list = keys_dict.values()
    csv_out_stream = open(csv_out_file, "w", newline="")
    dict_writer = csv.DictWriter(csv_out_stream, keys_list, delimiter=";")
    dict_writer.writeheader()

    i_well = 0
    convert_well = 0
    for las_file_name in las_files:

        if (i_well % 50 == 0):
            print("Number ", i_well)
            print("Convert ", convert_well)

        # инициализируем словарь и заполняем в соответсвии с ласом
        dict_list = []
        well_name = las_file_name[:-4]
        print(well_name)
        is_well_wc = 0
        if wc_well_names == []:
            is_well_wc = 1
        else:
            is_well_wc = len(list(filter(lambda x: well_name in x, wc_well_names)))
        if is_well_wc == 1:

            l = lasio.read(las_dir + "\\" + las_file_name)
            # print(well_name)
            # получить список кривых и их описание

            exist_val = False
            exist_values = dict()
            for cur_id in range(kid_calc, len(keys_list)):
                # print('cur_id = ', cur_id)
                exist_val = exist_val_in_list(keys_dict[cur_id], l.keys())
                exist_values[keys_dict[cur_id]] = exist_val
                if exist_val == False:
                    exist_val = exist_val

            # print(exist_values)

            if exist_val:
                n = int(len(l["DEPT"]))
                for i in range(n):
                    d = dict.fromkeys(keys_list)
                    d[keys_dict[kid_well]] = well_name
                    d[keys_dict[kid_uwi]] = l.well['WELL'].value
                    d[keys_dict[kid_depth]] = l[keys_dict[kid_depth]][i]
                    for param_id in range(kid_calc, len(keys_list)):
                        if exist_values[keys_dict[param_id]] == True:
                            d[keys_dict[param_id]] = l[keys_dict[param_id]][i]
                        else:
                            d[keys_dict[param_id]] = float('NaN')


                    dict_list.append(d)
                dict_writer.writerows(dict_list)
                # print(dict_list)
                convert_well = convert_well + 1
                #         else:
                #             print(l.keys())
            i_well = i_well + 1
            

    print("create_csv_from_las end, i_well = ", i_well, ', convert_well = ', convert_well)
    csv_out_stream.close()