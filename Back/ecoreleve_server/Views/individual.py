from pyramid.view import view_config
from ..Models import (
    Individual,
    IndividualType,
    IndividualDynPropValue,
    IndividualDynProp,
    Individual_Location,
    Sensor,
    SensorType,
    Equipment,
    IndividualList,
    Base,
    IndivLocationList,
    Station
    )
from ..GenericObjets.FrontModules import FrontModules
from ..GenericObjets import ListObjectWithDynProp
import transaction
import json, itertools
from datetime import datetime
import datetime as dt
import pandas as pd
import numpy as np
from sqlalchemy import select, and_,cast, DATE,func,desc,join,asc
from sqlalchemy.orm import aliased
from pyramid.security import NO_PERMISSION_REQUIRED
from traceback import print_exc
from collections import OrderedDict
from ..utils.distance import haversine
from ..utils.generator import Generator
import io
from pyramid.response import Response ,FileResponse
from pyramid import threadlocal


prefix = 'individuals'

# ------------------------------------------------------------------------------------------------------------------------- #
@view_config(route_name= prefix+'/action', renderer='json', request_method = 'GET', permission = NO_PERMISSION_REQUIRED)
@view_config(route_name= prefix+'/id/history/action', renderer='json', request_method = 'GET', permission = NO_PERMISSION_REQUIRED)
@view_config(route_name= prefix+'/id/equipment/action', renderer='json', request_method = 'GET', permission = NO_PERMISSION_REQUIRED)
def actionOnIndividuals(request):
    dictActionFunc = {
    'count' : count_,
    'forms' : getForms,
    '0' : getForms,
    'getFields': getFields,
    'getFilters': getFilters,
    'getType': getIndividualType
    }
    actionName = request.matchdict['action']
    return dictActionFunc[actionName](request)

def count_ (request = None,listObj = None) :
    session = request.dbsession
    ModuleType = 'IndivFilter'
    moduleFront  = session.query(FrontModules).filter(FrontModules.Name == ModuleType).one()
    if request is not None : 
        data = request.params
        if 'criteria' in data: 
            data['criteria'] = json.loads(data['criteria'])
            if data['criteria'] != {} :
                searchInfo['criteria'] = [obj for obj in data['criteria'] if obj['Value'] != str(-1) ]
        else : 
            searchInfo = {'criteria':[]}
        searchInfo['criteria'].append({'Column':'FK_IndividualType','Operator': '=', 'Value':1})
        listObj = ListObjectWithDynProp(Individual,moduleFront)
        count = listObj.count(searchInfo = searchInfo)
    else : 
        count = listObj.count()
    return count 

def getFilters (request):
    session = request.dbsession
    if 'typeObj' in request.params :
        objType = request.params['typeObj']
    else : 
        objType = 1

    ModuleType = 'IndivFilter'
    filtersList = Individual(FK_IndividualType = objType).GetFilters(ModuleType)
    filters = {}
    for i in range(len(filtersList)) :
        filters[str(i)] = filtersList[i]
    return filters

def getForms(request) :
    session = request.dbsession
    typeIndiv = request.params['ObjectType']
    ModuleName = 'IndivForm'
    Conf = session.query(FrontModules).filter(FrontModules.Name==ModuleName ).first()
    newIndiv = Individual(FK_IndividualType = typeIndiv)
    newIndiv.init_on_load()
    schema = newIndiv.GetDTOWithSchema(Conf,'edit')
    return schema

def getFields(request) :
    session = request.dbsession

    if 'typeObj' in request.params :
        objType = request.params['typeObj']
    else : 
        objType = 1

    ModuleType = request.params['name']
    if ModuleType == 'default' :
        ModuleType = 'IndivFilter'
    cols = Individual(FK_IndividualType = objType).GetGridFields(ModuleType)
    return cols

def getIndividualType(request):
    session = request.dbsession

    query = select([IndividualType.ID.label('val'), IndividualType.Name.label('label')])
    response = [ OrderedDict(row) for row in session.execute(query).fetchall()]
    return response

# ------------------------------------------------------------------------------------------------------------------------- #
@view_config(route_name= prefix+'/id', renderer='json', request_method = 'GET')
def getIndiv(request):
    session = request.dbsession
    id = request.matchdict['id']
    curIndiv = session.query(Individual).get(id)
    curIndiv.LoadNowValues()

    # if Form value exists in request --> return data with schema else return only data
    if 'FormName' in request.params :
        ModuleName = request.params['FormName']
        try :
            DisplayMode = request.params['DisplayMode']
        except : 
            DisplayMode = 'display'
        Conf = session.query(FrontModules).filter(FrontModules.Name=='IndivForm').first()
        response = curIndiv.GetDTOWithSchema(Conf,DisplayMode)

    elif 'geo' in request.params :
        geoJson=[]
        joinTable = join(Individual_Location, Sensor, Individual_Location.FK_Sensor == Sensor.ID)
        stmt = select([Individual_Location,Sensor.UnicIdentifier]).select_from(joinTable
            ).where(Individual_Location.FK_Individual == id)
        dataResult = session.execute(stmt).fetchall()

        for row in dataResult:
            geoJson.append({'type':'Feature', 'properties':{'type':row['type_']
                , 'sensor':row['UnicIdentifier'],'date':row['Date'],'ID':row['ID']}
                , 'geometry':{'type':'Point', 'coordinates':[row['LAT'],row['LON']]}})
        result = {'type':'FeatureCollection', 'features':geoJson}
        response = result
    else : 
        response  = curIndiv.GetFlatObject()
    # if 'geoDynamic' in request.params :
    #     geoJson=[]
    #     joinTable = join(Individual_Location, Sensor, Individual_Location.FK_Sensor == Sensor.ID)
    #     stmt = select([Individual_Location,Sensor.UnicIdentifier]).select_from(joinTable
    #         ).where(Individual_Location.FK_Individual == id
    #         ).where(Individual_Location.type_ == 'GSM').order_by(asc(Individual_Location.Date))
    #     dataResult = session.execute(stmt).fetchall()
        
    #     df = pd.DataFrame.from_records(dataResult, columns=dataResult[0].keys(), coerce_float=True)
    #     X1 = df.iloc[:-1][['LAT', 'LON']].values
    #     X2 = df.iloc[1:][['LAT', 'LON']].values
    #     df['dist'] = np.append(haversine(X1, X2), 0).round(3)
    #     # Compute the speed
    #     df['speed'] = (df['dist'] / ((df['Date'] - df['Date'].shift(-1)).fillna(1) / np.timedelta64(1, 'h'))).round(3)
    #     df['Date'] = df['Date'].apply(lambda row: np.datetime64(row).astype(datetime)) 

    #     for i in range(df.shape[0]):
    #         geoJson.append({'type':'Feature', 'properties':{'type':df.loc[i,'type_']
    #             , 'sensor':df.loc[i,'UnicIdentifier'],'speed':df.loc[i,'speed'],'date':df.loc[i,'Date']}
    #             , 'geometry':{'type':'Point', 'coordinates':[df.loc[i,'LAT'],df.loc[i,'LON']]}})
    #     result = {'type':'FeatureCollection', 'features':geoJson}
    #     response = result
    # else : 
    #     response  = curIndiv.GetFlatObject()
    return response

# ------------------------------------------------------------------------------------------------------------------------- #
@view_config(route_name= prefix+'/id/history', renderer='json', request_method = 'GET')
def getIndivHistory(request):
    session = request.dbsession
    id = request.matchdict['id']

    tableJoin = join(IndividualDynPropValue,IndividualDynProp
        ,IndividualDynPropValue.FK_IndividualDynProp == IndividualDynProp.ID)
    query = select([IndividualDynPropValue,IndividualDynProp.Name]).select_from(tableJoin).where(
        IndividualDynPropValue.FK_Individual == id
        ).order_by(desc(IndividualDynPropValue.StartDate))

    result = session.execute(query).fetchall()
    response = []
    for row in result:
        curRow = OrderedDict(row)
        dictRow = {}
        for key in curRow :
            if curRow[key] is not None :
                if 'Value' in key :
                    dictRow['value'] = curRow[key] 
                elif 'FK' not in key :
                    dictRow[key] = curRow[key]
        dictRow['StartDate'] = curRow['StartDate'].strftime('%Y-%m-%d %H:%M:%S')
        response.append(dictRow)

    return response

# ------------------------------------------------------------------------------------------------------------------------- #
@view_config(route_name= prefix+'/id/equipment', renderer='json', request_method = 'GET')
def getIndivEquipment(request):
    session = request.dbsession
    id_indiv = request.matchdict['id']

    table = Base.metadata.tables['IndividualEquipment']
    joinTable = join(table,Sensor, table.c['FK_Sensor'] == Sensor.ID)
    joinTable = join(joinTable,SensorType, Sensor.FK_SensorType == SensorType.ID)
    query = select([table.c['StartDate'],table.c['EndDate'],Sensor.UnicIdentifier,table.c['FK_Individual'],SensorType.Name.label('Type')]
        ).select_from(joinTable
        ).where(table.c['FK_Individual'] == id_indiv
        ).order_by(desc(table.c['StartDate']))

    result = session.execute(query).fetchall()
    response = []
    for row in result:
        curRow = OrderedDict(row)
        curRow['StartDate'] = curRow['StartDate'].strftime('%Y-%m-%d %H:%M:%S')
        if curRow['EndDate'] is not None :
            curRow['EndDate'] = curRow['EndDate'].strftime('%Y-%m-%d %H:%M:%S') 
        else:
            curRow['EndDate'] = ''
        response.append(curRow)

    return response

# ------------------------------------------------------------------------------------------------------------------------- #
@view_config(route_name= prefix+'/id', renderer='json', request_method = 'DELETE',permission = NO_PERMISSION_REQUIRED)
def deleteIndiv(request):
    session = request.dbsession
    id_ = request.matchdict['id']
    curIndiv = session.query(Individual).get(id_)
    session.delete(curIndiv)

    return True

# ------------------------------------------------------------------------------------------------------------------------- #
@view_config(route_name= prefix+'/id', renderer='json', request_method = 'PUT')
def updateIndiv(request):
    session = request.dbsession
    data = request.json_body
    id = request.matchdict['id']
    curIndiv = session.query(Individual).get(id)
    curIndiv.LoadNowValues()
    curIndiv.UpdateFromJson(data)
    return {}

# ------------------------------------------------------------------------------------------------------------------------- #
@view_config(route_name= prefix  + '/insert', renderer='json', request_method = 'POST')
def insertIndiv(request):
    session = request.dbsession
    data = request.json_body
    if not isinstance(data,list):
        return insertOneNewIndiv(request)
    else :
        print('_______INsert LIST')
        #transaction.commit()
        #return insertListNewIndivs(request)

# ------------------------------------------------------------------------------------------------------------------------- #
def insertOneNewIndiv (request) :
    session = request.dbsession
    session.autoflush = False # if set True create automatically a new indiv  = not what we want 
    data = {}
    startDate = None 

    for items , value in request.json_body.items() :
        data[items] = value
    existingIndivID = None

    if 'stationID' in data:
        curSta = session.query(Station).get(data['stationID'])
        startDate=curSta.StationDate

    indivType = int(data['FK_IndividualType'])
    newIndiv = Individual(FK_IndividualType = indivType , creationDate = datetime.now(),Original_ID = '0')
    # newIndiv.IndividualType = session.execute(([IndividualType.ID]).where(IndividualType.ID==indivType)).fetchone()
    newIndiv.init_on_load()
    newIndiv.UpdateFromJson(data,startDate=startDate)

    if indivType == 2:
        existingIndivID = checkExisting(newIndiv)
        if existingIndivID is not None:
            session.rollback()
            session.close()
            indivID = existingIndivID

    if existingIndivID is None:
        session.add(newIndiv)
        session.flush()
        indivID = newIndiv.ID

    return {'ID': indivID}

def checkExisting(indiv):
    # session = threadlocal.get_current_registry().dbmaker.session_factory()
    session = threadlocal.get_current_registry().dbmaker()
    indivData = indiv.PropDynValuesOfNow

    # del indivData['creationDate']
    for key in indivData:
        if indivData[key] is None: 
            indivData[key] = 'null'
    
    searchInfo = {'criteria':[{'Column':key,'Operator':'is','Value':val} for key,val in indivData.items()],'order_by':['ID:asc']}
 
    ModuleType = 'IndivFilter'
    moduleFront  = session.query(FrontModules).filter(FrontModules.Name == ModuleType).one()

    listObj = IndividualList(moduleFront,typeObj = 2)
    dataResult = listObj.GetFlatDataList(searchInfo)

    if len(dataResult)>0:
        existingID = dataResult[0]['ID']
    else :
        existingID = None

    return existingID

# ------------------------------------------------------------------------------------------------------------------------- #
@view_config(route_name= prefix, renderer='json', request_method = 'GET', permission = NO_PERMISSION_REQUIRED)
@view_config(route_name= prefix, renderer='json', request_method = 'POST', permission = NO_PERMISSION_REQUIRED)
def searchIndiv(request):
    session = request.dbsession
    data = request.params.mixed()

    searchInfo = {}
    searchInfo['criteria'] = []
    if 'criteria' in data: 
        data['criteria'] = json.loads(data['criteria'])
        if data['criteria'] != {} :
            searchInfo['criteria'] = [obj for obj in data['criteria'] if obj['Value'] != str(-1) ]

    searchInfo['order_by'] = json.loads(data['order_by'])
    searchInfo['offset'] = json.loads(data['offset'])
    searchInfo['per_page'] = json.loads(data['per_page'])

    if 'typeObj' in request.params:
        typeObj = request.params['typeObj']
        searchInfo['criteria'].append({'Column':'FK_IndividualType','Operator': '=', 'Value':request.params['typeObj']})
    else:
        searchInfo['criteria'].append({'Column':'FK_IndividualType','Operator': '=', 'Value':1})
        typeObj = 1

    ModuleType = 'IndivFilter'
    moduleFront  = session.query(FrontModules).filter(FrontModules.Name == ModuleType).one()

    listObj = IndividualList(moduleFront,typeObj = typeObj)
    dataResult = listObj.GetFlatDataList(searchInfo)
    countResult = listObj.count(searchInfo)

    result = [{'total_entries':countResult}]
    result.append(dataResult)
    return result


@view_config(route_name= prefix+'/id/location/action', renderer='json', request_method = 'GET', permission = NO_PERMISSION_REQUIRED)
def actionOnIndividualsLoc(request):
    dictActionFunc = {
    'getFields': getFieldsLoc,
    'getFilters': getFiltersLoc,
    }
    actionName = request.matchdict['action']
    return dictActionFunc[actionName](request)

def getFieldsLoc(request) :
    session = request.dbsession

    gene = IndivLocationList('Individual_Location',session,None)
    return gene.get_col()
# ------------------------------------------------------------------------------------------------------------------------- #
@view_config(route_name= prefix+'/id/location', renderer='json', request_method = 'GET')
def getIndivLocation(request):

    id_ = request.matchdict['id']
    session = request.dbsession
    gene = IndivLocationList('Individual_Location',session,id_)
    response = None

    data = request.params.mixed()
    if 'criteria' in data: 
        criteria = json.loads(data['criteria'])
    else : 
        criteria = {}
    
    if 'per_page' in data:
        offset = json.loads(data['offset'])
        per_page = json.loads(data['per_page'])
        order_by = json.loads(data['order_by'])
    else :
        offset= None 
        per_page= None
        order_by= None

    if 'geo' in request.params :
        result = gene.get_geoJSON(criteria,['ID','Date','type_'])

    else:
        result = gene.search(criteria,offset=offset,per_page=per_page,order_by=['StationDate:desc'])
        for row in result : 
            row['Date'] = row['Date'].strftime('%Y-%m-%d %H:%M:%S')
            row['format'] = 'YYYY-MM-DD HH:mm:ss'


    # ************ POC Indiv location PLayer  **************** 

    # if 'geoDynamic' in request.params :
    #     geoJson=[]
    #     joinTable = join(Individual_Location, Sensor, Individual_Location.FK_Sensor == Sensor.ID)
    #     stmt = select([Ind ividual_Location,Sensor.UnicIdentifier]).select_from(joinTable
    #         ).where(Individual_Location.FK_Individual == id
    #         ).where(Individual_Location.type_ == 'GSM').order_by(asc(Individual_Location.Date))
    #     dataResult = session.execute(stmt).fetchall()
        
    #     df = pd.DataFrame.from_records(dataResult, columns=dataResult[0].keys(), coerce_float=True)
    #     X1 = df.iloc[:-1][['LAT', 'LON']].values
    #     X2 = df.iloc[1:][['LAT', 'LON']].values
    #     df['dist'] = np.append(haversine(X1, X2), 0).round(3)
    #     # Compute the speed
    #     df['speed'] = (df['dist'] / ((df['Date'] - df['Date'].shift(-1)).fillna(1) / np.timedelta64(1, 'h'))).round(3)
    #     df['Date'] = df['Date'].apply(lambda row: np.datetime64(row).astype(datetime)) 

    #     for i in range(df.shape[0]):
    #         geoJson.append({'type':'Feature', 'properties':{'type':df.loc[i,'type_']
    #             , 'sensor':df.loc[i,'UnicIdentifier'],'speed':df.loc[i,'speed'],'date':df.loc[i,'Date']}
    #             , 'geometry':{'type':'Point', 'coordinates':[df.loc[i,'LAT'],df.loc[i,'LON']]}})
    #     result = {'type':'FeatureCollection', 'features':geoJson}
    #     response = result
    # else : 
    #     response  = curIndiv.GetFlatObject()

    return result


@view_config(route_name= prefix+'/id/location', renderer='json', request_method = 'PUT')
def delIndivLocationList(request):
    session = request.dbsession

    IdList = json.loads(request.params['IDs'])
    session.query(Individual_Location).filter(Individual_Location.ID.in_(IdList)).delete(synchronize_session=False)


@view_config(route_name= prefix+'/id/location/id_loc', renderer='json', request_method = 'GET')
def delIndivLocation(request):
    session = request.dbsession
    Id = request.matchdict['id_loc']
    session.query(Individual_Location).filter(Individual_Location.ID == Id).delete(synchronize_session=False)


@view_config(route_name=prefix + '/export', renderer='json', request_method='GET')
def sensors_export(request):
    session = request.dbsession
    data = request.params.mixed()
    searchInfo = {}
    searchInfo['criteria'] = []
    if 'criteria' in data: 
        data['criteria'] = json.loads(data['criteria'])
        if data['criteria'] != {} :
            searchInfo['criteria'] = [obj for obj in data['criteria'] if obj['Value'] != str(-1) ]

    searchInfo['order_by'] = []

    ModuleType = 'IndivFilter'
    moduleFront  = session.query(FrontModules).filter(FrontModules.Name == ModuleType).one()

    listObj = IndividualList(moduleFront)
    dataResult = listObj.GetFlatDataList(searchInfo)

    df = pd.DataFrame.from_records(dataResult, columns=dataResult[0].keys(), coerce_float=True)

    fout = io.BytesIO()
    writer = pd.ExcelWriter(fout)
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    file = fout.getvalue()

    dt = datetime.now().strftime('%d-%m-%Y')
    return Response(file,content_disposition= "attachment; filename=individuals_export_"+dt+".xlsx",content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')







