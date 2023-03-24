import json
file = {
                "path": "/home/shaoshenxu/toolsdev/Agent/etc",
                "fileQuantity": 7,
                "files": [{
                    "fileName": "/home/shaoshenxu/toolsdev/Agent/etc/aggs",
                    "fileOnlyName": "aggs",
                    "fileMODTime": "2021-12-17 19:47:18",
                    "fileType": "dir"
                }, {
                    "fileName": "/home/shaoshenxu/toolsdev/Agent/etc/input",
                    "fileOnlyName": "input",
                    "fileMODTime": "2021-12-15 15:53:34",
                    "fileType": "dir"
                }, {
                    "fileName": "/home/shaoshenxu/toolsdev/Agent/etc/main",
                    "fileOnlyName": "main",
                    "fileMODTime": "2021-12-07 19:37:24",
                    "fileType": "dir"
                }, {
                    "fileName": "/home/shaoshenxu/toolsdev/Agent/etc/output",
                    "fileOnlyName": "output",
                    "fileMODTime": "2021-12-17 19:46:37",
                    "fileType": "dir"
                }, {
                    "fileName": "/home/shaoshenxu/toolsdev/Agent/etc/processor",
                    "fileOnlyName": "processor",
                    "fileMODTime": "2021-12-17 19:47:02",
                    "fileType": "dir"
                }, {
                    "fileName": "/home/shaoshenxu/toolsdev/Agent/etc/host.yaml",
                    "fileOnlyName": "host.yaml",
                    "fileMODTime": "2021-12-15 11:56:34",
                    "fileType": "file"
                }, {
                    "fileName": "/home/shaoshenxu/toolsdev/Agent/etc/main.yaml",
                    "fileOnlyName": "main.yaml",
                    "fileMODTime": "2021-12-19 13:50:40",
                    "fileType": "file"
                }]
            }


f1 = json.dumps(file)
print(f1)

f2 = json.loads(f1)
print(f2)