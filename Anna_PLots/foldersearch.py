import os


folders = []
filenames = {}
#
#
# for root, subfolders, files in os.walk(r'\\dtu-storage\annawi\Desktop\Data Testfolder'):
#     folders=[subfolders]
#
#     for subfolder, file in (subfolders, files):
#         filenames[subfolder] = [files]
#         print(files)
#
#     # for file in files:
#     #     if file.endswith(".mpt"):
#     #         #filenames[subfolder].append(file)
#     #         print(filenames[subfolder])
#     #         #print(os.path.join(root, file))
#
# print(folders)
# print(filenames)

for root, subfolders, files in os.walk(r'\\dtu-storage\annawi\Desktop\Propene oxidation\Experiments\Pd electrodes\EC and product analysis'):
    if len(files)==0: continue
    #folders.append(root[-8:])
    folders.append(root[-15:])
    files_this_folder = []
    for filename in files:
        if filename.endswith(".mpt"):
            files_this_folder.append(filename)
            #print(root)
#    filenames[root[-8:]] = files_this_folder
    filenames[root[-15:]] = files_this_folder

print(folders)
print(filenames)



# for root, _, files in os.walk(r'\\dtu-storage\annawi\Desktop\Data Testfolder'):
#     if len(files)==0: continue
#     folders.append(root)
#     files_this_folder = []
#     for filename in files:
#         if filename.endswith(".mpt"):
#             files_this_folder.append(filename)
#     filenames[root] = files_this_folder
#
# print(folders)
# print(filenames)

# for f in folders:
#     print(f)
# for i in filenames.items():
#     print(i)
