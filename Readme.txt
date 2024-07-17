Исходники для образа Docker: Dockerfile, exporterfull.py, requirements.txt. 
Делаете докер билд, если все ок, из созданного образа запускаете контейнер. Предварительно меняете настройки подключения к SQL в файле exporterfull.py.
P.S. Возможно кому-то нужно: 
1. docker build -t <image_name> <path to files Dockerfile, exporterfull.py, requirements.txt>
2. docker run -d -p 8000:8000 --name <container_name> image_name
