#!/usr/bin/env python
# coding: utf-8

# DATA ARRANGEMENT FROM EXCEL TO NETCDF
# ----
# PART 1
# ---

# <h5> IMPORT PACKAGES <h5>

# In[1]:


import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt 
import collections


# <h5>OPEN ALL SHEETS <h5>
# 

# In[4]:


csv_files = pd.ExcelFile('Stacked_Rainfall_Data_Cumulative_Analysis_2019.xlsx')
stns=pd.read_excel('Stations.xlsx')['Stations'][:]
lats = pd.read_excel('Stations.xlsx')['Latitude'][:]
lons = pd.read_excel('Stations.xlsx')['Longitude'][:]
#csv_data = pd.read_excel('Stacked_Rainfall_Data_Cumulative_Analysis_2019.xlsx',sheet_name=stns)


# <h5> GROUPING THE DATA INTO DEKADS <h5>
# 

# In[7]:


all_stns=collections.defaultdict(list)

for stn_idx,stn in enumerate(stns):
    
    csv_data = pd.read_excel('Stacked_Rainfall_Data_Cumulative_Analysis_2019.xlsx',sheet_name=stn)
    ptn_1990=np.where(csv_data.columns==1990)[0][0]
    pp=[]
    
    
    for idx,df in enumerate(csv_data.columns[ptn_1990:ptn_1990+26]):
        
        nd =csv_data[df]
        time = pd.date_range('01-01-'+str(df),'12-31-'+str(df),freq='1D')
        app=pd.DataFrame([time,nd[0:len(time)]]).T.set_index(0)
        tp_app=[]
        
        
        for m_idx in np.arange(1,13,1):
            
            time = pd.date_range('01-01-'+str(df),'12-31-'+str(df),freq='1D')
            app=pd.DataFrame([time,nd[0:len(time)]]).T.set_index(0)
            app = app[app[str(df)].index.month==m_idx].resample('10D').sum()
            lo = [lons[stn_idx]]*len(app.index)
            la = [lats[stn_idx]]*len(app.index)
            app['lons']=lo;app['lats']=la
            tp_app.append(app)
        
        pp.append(pd.concat(tp_app))
    
    all_stns[stn].append(pd.concat(pp))


# <h5> RE-ARRANGING DATA INTO NETCDF FORMAT <h5>
# 

# In[8]:


dframe=[]
for i,frame in enumerate(list(all_stns.keys())):
    if i <=9:
        dframe.append(all_stns[frame])

df_keys=list(all_stns.keys())[:10]
d=[i[0] for a,i in  enumerate(dframe)]

DATA=pd.concat(d,keys=df_keys)
DATA=DATA.reset_index()
new_data = pd.DataFrame({'time': DATA[0],'precip':DATA[1],'lons':DATA['lons'],'lats':DATA['lats']})

GMET_precip=new_data.set_index(['time','lons','lats']).to_xarray()
GMET_precip.to_netcdf('North_GH_precip.nc')


# <h5> VISUALISING DATA <h5>
# 

# In[25]:


import cartopy.crs as ccrs
from cartopy import feature as cf

fig = plt.figure(figsize=(5,5))
ax = fig.add_subplot(111,projection=ccrs.PlateCarree())
ax.add_feature(cf.BORDERS)
GMET_precip.precip.T.mean('time').plot()


#  DATA ARRANGEMENT FROM GRIDS TO SPECIFIC LOCATIONS 
# ------
# PART 2
# ---

# <h5>LOAD DATASETS<h5>
# 
# 

# In[58]:


tamsat = xr.open_dataset(r'tamsat.GHA.RainfallSum.dekad.nc')
arc2=xr.open_dataset(r'arc2.GHA.RainfallSum.dekad.nc')
chirps=xr.open_dataset(r'chirps-v2.GHA.RainfallSum.dekad.nc')


# <h5>FUNCTION FOR SELECTING REGION<h5>
# 

# In[61]:


def reg_select(ds,ds_var,ds_time, lons,lats):
    app=[]
    for i in range(9):
        for j,a in enumerate(tamsat.time):
            res = ds[ds_var].sel(time=ds[ds_time][j].values.astype(str)[0:10],longitude=lons[i],latitude=lats[i],method='nearest').values
            app.append([res,lons[i],lats[i],a.values.astype(str)[0:10]])

    N_station=pd.DataFrame(app,columns=[ds_var,'lon','lat',ds_time])
    #N_station['lon']=N_station['lon'] #use this to shift longitude
    N_new=pd.DataFrame({ds_var : N_station[ds_var], ds_time : N_station[ds_time], 'latitude' : N_station['lat'] , 'longitude' : N_station['lon']})
    new_data=N_new.set_index(['longitude','latitude',ds_time]).to_xarray()
    return new_data


# <h5> RUNNING FXN ON DATA <h5>

# In[59]:


tamsat_new = reg_select(tamsat,'precipitation','time',lons,lats)
arc_new = reg_select(arc2,'precipitation','time',lons,lats)
chirps_new =  reg_select(chirps,'precipitation','time',lons,lats)


# <h5> CONVERT TO NETCDF <h5>

# In[60]:


tamsat_new.to_netcdf('North_GH_TAMSAT.nc')
arc_new.to_netcdf('North_GH_ARC2.nc')
chirps_new.to_netcdf('North_GH_CHIRPS.nc')


# <h5> VISUALISING CONVERTED FILES <h5>

# In[44]:


import cartopy.crs as ccrs
from cartopy import feature as cf

fig = plt.figure(figsize=(5,5))
ax = fig.add_subplot(111,projection=ccrs.PlateCarree())
ax.add_feature(cf.BORDERS)
New_Tamsat.tmp.T.mean('time').plot()






