
#Подключаем модуль
import os
def GetFilesInDir(path_dir, file_format = ''):
    #Получаем список файлов в переменную files
    files = os.listdir(path_dir)

    #Фильтруем список
    res_files = filter(lambda x: x.endswith(file_format), files)

    return res_files