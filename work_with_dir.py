
#Подключаем модуль
import os
def GetFilesInDir(path_dir, file_format = ''):
    #Получаем список файлов в переменную files
    files = os.listdir(path_dir)
    lower_files = []
    for file in files:
        lower_files.append(str(file.lower()))


    #Фильтруем список
    res_files = filter(lambda x: x.endswith(file_format), lower_files)

    return res_files