from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import *
from .forms import addanimalform,addcameraform,addtaskform,addresearcherform
from background_task import background
import time
import subprocess
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pusher
from tensorflow import keras
import numpy as np
import datetime
import threading

# Use a service account

###########API##############
# from .models import Snippet
from .serializers import Task_serializer
from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json

def login(request):
    # fun()
    # back()
    # with open('/home/ravi/python projects/sih2020/server/app/process.sh', 'rb') as file:
    #     script = file.read()
    # rc = subprocess.call(script, shell=True)
    request.session.flush()
    # process = subprocess.Popen(['python', 'manage.py','process_tasks'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return render(request, "login.html", {})

def info(request):
    if request.method == 'POST':    
        user = request.POST.get('username')
        passw = request.POST.get('password')
        print(user,passw)
        if user =='admin' and passw=='admin123':
            return redirect('admin')
        else:
            try:
                data=Researcher.objects.get(username=user,password=passw)
                flag="r"
            except Researcher.DoesNotExist:
                try:
                    data=Forest_employee.objects.get(username=user,password=passw)
                    flag="f"
                except:
                    data = None
                    flag = None
            # data=Researcher.objects.get(username=user,password=passw)
            print(data,flag)
            if data==None:
                return redirect('login')
            if flag=="r":
                request.session['data']={'researcher_id':data.researcher_id}
                request.session['flag']="r"
                return redirect('researcher')
            else:
                request.session['data']={'area':data.area}
                if data.role=='employee':
                    request.session['flag']="e"
                else:
                    request.session['flag']="f"
                return redirect('forest_employee')
    # return render(request, "next.html", {})

def admin(request):
    ##ml model
    model=keras.models.load_model('main/static/hood_2')
    test=np.array([2020,197]).reshape(1,2)
    pred=model.predict(test)
    val=[]
    with open('main/static/Neighbourhoods.geojson', 'r') as openfile: 
  
    # Reading from json file 
        data = json.load(openfile) 
    # print(pred)
    for i in pred:
        # print(i)
        val=i
        ##x>=0.5 red,0.5>x>=0.2 yellow,x<0.2 green
    for i in range(len(val)):
        if val[i]>=0.5:
            data['features'][i]['properties']["AREA_SHORT_CODE"]=1
        elif val[i]<0.5 and val[i]>=0.2:
            data['features'][i]['properties']["AREA_SHORT_CODE"]=2
        else:
            data['features'][i]['properties']["AREA_SHORT_CODE"]=3
    # data['features']=sorted(data['features'], key=lambda k: k['properties'].get("AREA_SHORT_CODE",0))
    with open('main/static/Neighbourhoods.geojson', "w") as outfile: 
        json.dump(data, outfile) 

    animals=[]
    sdict={}
    slat={}
    slon={}
    x=Animal.objects.all()
    for y in x:
        animals.append(y.animal_info)
    animals=list(set(animals))
    for atype in animals:
        sdict[atype]=[]
        slat[atype]=[]
        slon[atype]=[]
        a=Animal.objects.filter(animal_info=atype)
        for i in a:
            sdict[atype].append(i.animal_id)
            slat[atype].append(i.latitude[-1])
            slon[atype].append(i.longitude[-1])
    print(sdict,slat,slon)
    return render(request,"admin.html",{"animals":animals,"sdict":sdict,"slat":slat,"slon":slon})
    
def researcher(request):
    data=request.session.get('data')
    print(data)
    r=Researcher.objects.get(researcher_id=data['researcher_id'])
    animals=r.animal
    print(animals)
    sdict={}
    slat={}
    slon={}
    for atype in animals:
        sdict[atype]=[]
        slat[atype]=[]
        slon[atype]=[]
        a=Animal.objects.filter(animal_info=atype)
        for i in a:
            sdict[atype].append(i.animal_id)
            slat[atype].append(i.latitude[-1])
            slon[atype].append(i.longitude[-1])
    print(sdict,slat,slon)
    return render(request,"researcher.html",{"animals":animals,"sdict":sdict,"slat":slat,"slon":slon})

def forest_employee(request):
    data=request.session.get('data')
    print(data)
    animals=[]
    sdict={}
    slat={}
    slon={}
    x=Animal.objects.all()
    for y in x:
        animals.append(y.animal_info)
    animals=list(set(animals))
    for atype in animals:
        sdict[atype]=[]
        slat[atype]=[]
        slon[atype]=[]
        a=Animal.objects.filter(animal_info=atype)
        for i in a:
            sdict[atype].append(i.animal_id)
            slat[atype].append(i.latitude[-1])
            slon[atype].append(i.longitude[-1])
    print(sdict,slat,slon)
    return render(request,"forest_employee.html",{"animals":animals,"sdict":sdict,"slat":slat,"slon":slon})
    
def task(request):
    for key, value in request.session.items():
        print('{} => {}'.format(key, value))
    flag=request.session.get("flag")
    if flag=="r":
        data=Tasks.objects.filter(task_from=request.session.get('data')['researcher_id'])
        return render(request,"task.html",{'data':data,'flag':flag})
    else:
        fn=request.session.get('data')['forest_name']
        data=[]
        d=Tasks.objects.filter(task_to=fn)
        s=Tasks.objects.filter(task_from=fn)
        print(s,d)
        for i in d:
            data.append(i)
        print(data,fn)
        for i in s:
            for j in range(len(data)):
                # print(data[j].task_id)
                if data[j]!=-1:
                    if i.task_id==data[j].task_id:
                        data[j]=-1
            data.append(i)
        data=list(filter(lambda a: a != -1, data))

        w=Forest_employee.objects.filter(forest_name=fn)
        print(w)
        # ind=0
        # for i in w:
        #     i.empid
    return render(request,"task.html",{'data':data,'flag':flag,"workers":w})# to be continued from forest officer

def addtask(request):
    for key, value in request.session.items():
        print('{} => {}'.format(key, value))
    if request.method == 'POST':
        print(request.POST)
        t=Tasks()
        count=Tasks.objects.count()
        t.task_id='id_'+(str(count+1))
        t.task_from=request.session.get('data')['researcher_id']
        t.task_info=request.POST.get("task_info")
        t.task_to=request.POST.get("task_to")
        t.status='incomplete'
        t.deadline=request.POST.get("deadline")
        print(t)
        t.save()
        # form = addtaskform(request.POST or None)
        # if form.is_valid():
        #     form.save()  
        return render(request,"done.html",{})
        # else:
        #     # form.errors.as_data()
        #     print('error',form.errors.as_data())
    forest_name=[]
    data=Forest_employee.objects.all()
    for i in data:
        forest_name.append(i.forest_name)
    forest_name=list(set(forest_name))
    return render(request,"addtask.html",{'forest_name':forest_name})

def assigntask(request):
    # for key, value in request.session.items():
    #     print('{} => {}'.format(key, value))
    if request.method == 'POST':
        print(request.POST)
        task=Tasks.objects.get(task_id=request.POST['task_id'])
        Tasks.objects.filter(task_id=request.POST["task_id"]).update(status="assigned")
        t={}
        t["task_id"]=task.task_id
        t["task_from"]=task.task_to
        t["task_info"]=task.task_info
        t["task_to"]=request.POST['task_to']
        t["status"]='assigned'
        t["deadline"]=task.deadline.strftime('%Y-%m-%d')
        print(t)
        # t.save()
        if not firebase_admin._apps:
            data = open('main/static/serviceAccount.json').read() #opens the json file and saves the raw contents
            jsonData = json.loads(data) #converts to a json structure

            cred = credentials.Certificate(jsonData)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
        db = firestore.client()
        doc_ref = db.collection(u'task').document(u'assign')
        temp=doc_ref.get()
        temp=temp.to_dict()
        print(temp)
        if request.POST['task_to'] in temp:
            temp[request.POST['task_to']].append(t)
        else:
            temp[request.POST['task_to']]=[t]
        print(temp)
        doc_ref.set(temp)
    return HttpResponse(status=200)

def addanimal(request):
    if request.method == 'POST':
        print((request.POST['animal_id']))
        a=Animal()
        count=Animal.objects.count()
        # print(count)
        a.animal_id='id_'+(str(count+1))
        a.animal_name=request.POST['animal_name']
        a.animal_info=request.POST['animal_info']
        a.latitude=[0]
        a.longitude=[0]
        a.save()
        # form = addanimalform(request.POST or None)
        # if(False):
        # if form.is_valid():
        # form.save()
        #firebase#
        if not firebase_admin._apps:
            data = open('main/static/serviceAccount.json').read() #opens the json file and saves the raw contents
            jsonData = json.loads(data) #converts to a json structure

            cred = credentials.Certificate(jsonData)
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        print(db,'id_'+(str(count+1)))

        map_alert=db.collection(u'map_alert').document('animal')
        tem=map_alert.get()
        if tem.exists:
            an=tem.to_dict()
            if request.POST['animal_info'] in an:
                an[request.POST['animal_info']].append('id_'+(str(count+1)))
            else:
                an[request.POST['animal_info']]=['id_'+(str(count+1))]
            map_alert.update(an)
            
        an_loc=db.collection(u'map_alert').document('location')
        tem=an_loc.get()
        if tem.exists:
            lo=tem.to_dict()
            lo['id_'+(str(count+1))]=[0,0]
            an_loc.update(lo)

        animal = db.collection(u'animals').document('id_'+(str(count+1)))
        animal.set({
            u'latitude': 0,
            u'longitude': 0,
        })

        animal = db.collection(u'animals_update').document('new')
        animal.set({
            u'animal_id': 'id_'+(str(count+1)),
            u'animal_type': request.POST['animal_info'],
        })

        ##animal list##
        animals_list = db.collection(u'animals_list').document(request.POST['animal_info'])
        temp=animals_list.get()
        if temp.exists:
            print("yes")
            sel=temp.to_dict()
            print(sel['id'])
            tem=sel['id']
            tem.append('id_'+(str(count+1)))
            animals_list.update({'id':tem})
        else:
            print("no")
            animals_list.set({
                u'id':['id_'+(str(count+1))]
            })

        docs = db.collection(u'animals').stream()

        for doc in docs:
            print(f'{doc.id} => {doc.to_dict()}')
        #######
        
        return render(request,"done.html",{})  
    return render(request,"addanimal.html",{})

def addcamera(request):
    if request.method == 'POST':
        # form = addcameraform(request.POST or None)
        # if form.is_valid():
        #     form.save()  
        c=Camera()
        count=Camera.objects.count()
        c.camera_id='id_'+(str(count+1))
        c.latitude=request.POST['latitude']
        c.longitude=request.POST['longitude']
        c.status=request.POST['status']
        c.save()
        return render(request,"done.html",{})
    return render(request,"addcamera.html",{})

def addresearcher(request):
    if request.method == 'POST':
        # print(request.body)
        # form = addresearcherform(request.POST or None)
        r=Researcher()
        count=Researcher.objects.count()
        r.researcher_id='id_'+(str(count+1))
        r.researcher_name=request.POST['researcher_name']
        r.experience=request.POST['experience']
        r.qualification=request.POST['qualification']
        r.animal=request.POST['animal'].split(",")
        r.username=request.POST['username']
        r.password=request.POST['password']
        r.save()
        # if (False):
            # form.save() 
        return render(request,"done.html",{})
        # else:
        #     # form.errors.as_data()
        #     print('error',form.errors.as_data())
    data=Animal.objects.all()
    al=[]
    for i in data:
        al.append(i.animal_info)
    al=list(set(al))
    return render(request,"addresearcher.html",{"animal":al})

def addforest_employee(request):
    if request.method == 'POST':
        temp=Forest_employee()
        count=Forest_employee.objects.count()
        temp.empid='id_'+(str(count+1))
        temp.name=request.POST['name']
        temp.forest_name=request.POST['forest_name']
        temp.role=request.POST['role']
        temp.username=request.POST['username']
        temp.password=request.POST['password']
        temp.save()
        return render(request,"done.html",{})

    return render(request,"addforest_employee.html",{})

def researcherlist(request):
    data=Researcher.objects.all()
    return render(request,"researcherlist.html",{'data':data})

def location(request):
    print(request.POST['animals'])
    animals=request.POST['animals'].split(",")
    sdict={}
    slat={}
    slon={}
    for atype in animals:
        sdict[atype]=[]
        slat[atype]=[]
        slon[atype]=[]
        a=Animal.objects.filter(animal_info=atype)
        for i in a:
            sdict[atype].append(i.animal_id)
            slat[atype].append(i.latitude[-1])
            slon[atype].append(i.longitude[-1])
    print(sdict,slat,slon)
    return JsonResponse({"sdict":sdict,"slat":slat,"slon":slon})
    # return HttpResponse({"sdict":sdict,"slat":slat,"slon":slon},content_type="application/json")

def geojson(request):
    data = open('main/static/Neighbourhoods.geojson').read() #opens the json file and saves the raw contents
    data = json.loads(data)
    # data['features']=sorted(data['features'], key=lambda k: k['properties'].get("AREA_SHORT_CODE",0))
    return JsonResponse(data, safe=False)

def editresearcher(request,id="0"):
    print(id)
    if request.method == 'POST':
        d=Researcher.objects.get(researcher_id=id).delete()
        r=Researcher()
        r.researcher_id=id
        r.researcher_name=request.POST['researcher_name']
        r.experience=request.POST['experience']
        r.qualification=request.POST['qualification']
        r.animal=request.POST['animal'].split(",")
        r.username=request.POST['username']
        r.password=request.POST['password']
        r.save()
        # if (False):
            # form.save() 
        return render(request,"done.html",{})
    r=Researcher.objects.get(researcher_id=id)
    ra=set(r.animal)
    data=Animal.objects.all()
    al=[]
    for i in data:
        if i.animal_info not in ra: 
            al.append(i.animal_info)
    al=list(set(al))
    ra=list(ra)
    resa=ra[0]
    for i in range(1,len(ra)):
        resa+=","+ra[i]
    return render(request,"editresearcher.html",{"r":r,"animal":al,"resa":resa})

def report(request):
    return render(request,"report.html",{})

def reportlist(request):
    rep=Report.objects.all()
    data=request.session.get('data')
    print(data)
    lrange=Division_range.objects.filter(division_id=data['area'])
    return render(request,"reportlist.html",{"rep":rep})

######BACK GROUND TASK########
@background(schedule=2)
def back():
    if not firebase_admin._apps:
        data = open('main/static/serviceAccount.json').read() #opens the json file and saves the raw contents
        jsonData = json.loads(data) #converts to a json structure

        cred = credentials.Certificate(jsonData)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    a=0
    print("in back new","ravi")
    # while(a<10):
    a+=1
    print(a)
    l=[]
    lon={}
    lat={}
    time={}
    c=Camera.objects.all()
    l=set(l)
    
    for i in c:
        l.add(str(i.camera_id))
        lon[str(i.camera_id)]=i.longitude
        lat[str(i.camera_id)]=i.latitude
    s=[]
    temp=Status.objects.all()
    s=set(s)
    now = datetime.datetime.now()
    for i in temp:
        # time[str(i.camera_id)]=i.time
        s.add(str(i.camera_id))
    ans=l-s
    if (len(ans)!=0):
        xyz=list(ans)
        print(time)
        for i in xyz:
            c = db.collection(u'camera').document('status')
            c.set({
                u'camera_id': i,
                u'latitude': lat[i],
                u'longitude': lon[i],
                u'time': now
            })

            pusher_client = pusher.Pusher(
            app_id='1038724',
            key='ed4d3bfd7a2e6650c539',
            secret='d87ae9e5262f74360a37',
            cluster='ap2',
            ssl=True
            )
            pusher_client.trigger('my-channel', 'my-event', {'message': i})
    else:
        c = db.collection(u'camera').document('status')
        c.set({
            
        })
    
    d=Status.objects.all().delete()
    # time.sleep(30)


def fun():
    print('call')
    return

###############firestore##################
callback_done = threading.Event()
if not firebase_admin._apps:
    data = open('main/static/serviceAccount.json').read() #opens the json file and saves the raw contents
    jsonData = json.loads(data) #converts to a json structure

    cred = credentials.Certificate(jsonData)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
db = firestore.client()

def on_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:    
        dic=doc.to_dict()
        if dic:
            # print(dic)
            r=Report()
            r.empid=dic['empid']
            res = bytes(dic['image'], 'utf-8')
            r.image=res
            r.description=dic['description']
            r.latitude=dic['latitude']
            r.longitude=dic['longitude']
            r.save()
            print(dic['description'])
        # print(dic['image'])
    callback_done.set()

# Create a callback on_snapshot function to capture changes

doc_ref = db.collection(u'report').document(u'animal_report')

# Watch the document
doc_watch = doc_ref.on_snapshot(on_snapshot)

###TASK####
callback_done_task = threading.Event()
def on_snapshot_task(doc_snapshot, changes, read_time):
    tid=''
    for doc in doc_snapshot:    
        dic=doc.to_dict()
        if dic:
            # print(dic)
            t=Tasks.objects.filter(task_id=dic['task_id']).update(status='complete')
            rep=Task_Description()
            rep.task_id=dic['task_id']
            tid=dic['task_id']
            rep.description=dic['description']
            res = bytes(dic['image'], 'utf-8') 
            rep.image=res
            rep.save()
            # print(dic)
        # print(dic['image'])
            e = db.collection(u'task').document(u'assign')
            di = e.get().to_dict()
            # print(di,dic['empid'])
            for i in range(len(di[dic['empid']])):
                print(i)
                if di[dic['empid']][i]['task_id']==tid:
                    print(di[dic['empid']][i])
                    del(di[dic['empid']][i])
                    break
            e.set(di)

    callback_done_task.set()

doc_ref_task = db.collection(u'task').document(u'complete')

# Watch the document
doc_watch_task = doc_ref_task.on_snapshot(on_snapshot_task)




###############API#################
class give_task(APIView):
    def post(self,request,format=json):
        print(request.data)
        snippets = Tasks.objects.filter(task_to=request.data[0],status='assigned')
        serializer = Task_serializer(snippets, many=True)
        # return render(request,"appdata.html",{'data':serializer.data})
        return Response(serializer.data)
        # print(serializer.data)
        # return Response({"data":[{"id":10},{"id":103}]})

class manage_task(APIView):
    # def get(self,request,format=None):
    #     print(request.data)
    #     snippets = Tasks.objects.filter(task_to=request.data)
    #     serializer = Task_serializer(snippets, many=True)
    #     # return render(request,"appdata.html",{'data':serializer.data})
    #     # return Response(serializer.data)
    #     return Response({'data':['a','b','asd']})

    def post(self, request, format=None):
        print(type(request.data))
        if type(request.data) is list:
            print(len(request.data))
            for i in range(len(request.data)):
                serializer = Task_serializer(data=request.data[i])
                print("posting",serializer)
                if serializer.is_valid():
                    print("valid",request.data[i]['task_id'])
                    Tasks.objects.get(task_id=request.data[i]['task_id'],task_to=request.data[i]['task_to']).delete()
                    Tasks.objects.filter(task_id=request.data[i]['task_id'],task_to=request.data[i]['task_from']).update(status='complete')
                    serializer.save()

            return Response([], status=status.HTTP_201_CREATED)
        else:
            serializer = Task_serializer(data=request.data)
            print("posting",serializer)
            if serializer.is_valid():
                print("valid",request.data['task_id'])
                Tasks.objects.get(task_id=request.data['task_id'],task_to=request.data['task_to']).delete()
                Tasks.objects.filter(task_id=request.data['task_id'],task_to=request.data['task_from']).update(status='complete')
                serializer.save()
                
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class manage_login(APIView):
    # def get(self,request,format=None):
    #     print(request.data)
    #     data={"id":10}
    #     print("get")
    #     return Response(data,status=status.HTTP_201_CREATED)

    def post(self,request,format=None):
        print(request.data)
        try:
            d=Forest_employee.objects.get(username=request.data['username'],password=request.data['password'])
            st=d.empid+'-'+d.name
            data={"id":st}
            print("post")
        except Forest_employee.DoesNotExist:
            data={"id":"-1"}
        return Response(data,status=status.HTTP_201_CREATED)

class alert(APIView):
    # count=set([])
    def post(self,request,format=None):
        # print(self.count)
        now = datetime.datetime.now()
        if not firebase_admin._apps:
            data = open('main/static/serviceAccount.json').read() #opens the json file and saves the raw contents
            jsonData = json.loads(data) #converts to a json structure

            cred = credentials.Certificate(jsonData)
            firebase_admin.initialize_app(cred)
        db = firestore.client()

        if(request.data['type']=="working"):
            x=Status()
        elif (request.data['type']=="hunter"):
            pusher_client = pusher.Pusher(
                app_id='1038724',
                key='ed4d3bfd7a2e6650c539',
                secret='d87ae9e5262f74360a37',
                cluster='ap2',
                ssl=True
                )
            pusher_client.trigger('my-channel', 'my-event', {'message': 'Hunter detected'})
            x=Logs()
            x.latitude=float(request.data['latitude'])
            x.longitude=float(request.data['longitude'])

            c = db.collection(u'camera').document('hunter')
            c.set({
                u'camera_id': request.data['value'],
                u'latitude': request.data['latitude'],
                u'longitude': request.data['longitude'],
                u'time' : request.data['timestamp']
            })
            time.sleep(5)
            c.set({
                
            })

        x.camera_id=request.data['value']
        x.action=request.data['type']
        # self.count.remove(request.data['value'])
        # x.time=
        x.time=str(request.data['timestamp'])
        x.save()
        return Response(status=status.HTTP_201_CREATED)

class backtask(APIView):
    def post(self,request,format=None):
        back(repeat=5,repeat_until=datetime.datetime.now()+datetime.timedelta(0,600))
        process = subprocess.Popen(['python', 'manage.py','process_tasks'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return Response(status=status.HTTP_201_CREATED)