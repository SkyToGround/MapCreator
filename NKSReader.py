#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python2.7
# encoding: utf-8

import numpy as np
import re
from scipy.interpolate import interp1d
import pyproj
import Log
import os
import time

def OpenCSV(file_name):
	in_data = np.recfromcsv(file_name, usecols = (0,1), usemask = False, dtype = np.float)
	lat = np.empty((len(in_data), ))
	lon = np.empty((len(in_data), ))
	values = np.ones((len(in_data), ))
	for i in range(len(in_data)):
		lat[i] = in_data[i][0]
		lon[i] = in_data[i][1]
	return lat, lon, values

def OpenNKS(file_name, var_name, rt90 = True):
	if (file_name.find(".csv") != -1):
		return OpenCSV(file_name)
	Log.info("OpenNKS(): Extracting data from file: " + file_name)
	try:
		in_file = open(file_name, "r")
		in_lines = in_file.readlines()
		in_file.close()
	except IOError:
		Log.error("OpenNKS(): Unable to open or read from file: " + file_name)
	arr_len = len(in_lines)
	lon = []
	lat = []
	value = []
	
	lat_re = re.compile("Y_RT90 ([\-0-9]+) ")
	lon_re = re.compile("X_RT90 ([\-0-9]+) ")
	#dose_re = re.compile("SDI\_doserate\_uSv\/h ([0-9.]+E?-?[0-9]*)")
	#new_var_name = var_name.replace("_", "\_")
	dose_re = re.compile(var_name + " (-?[0-9.]+E?-?[0-9]*)")
	
	Log.info("OpenNKS(): Searching for the variable: " + var_name)
	
	rejected = 1
	
	wgs84Proj = pyproj.Proj(proj="lonlat", ellps="WGS84", datum="WGS84")
	rt90Proj = pyproj.Proj("+proj=tmerc +lat_0=0 +lon_0=15.8082777778 +k=1 +x_0=1500000 +y_0=0 +ellps=bessel +towgs84=414.1,41.3,603.1,-0.855,2.141,-7.023,0 +units=m +no_defs")
	
	for i in range(1, arr_len):
		c_line = in_lines[i]
		res_Y = re.search(lat_re, c_line)
		res_X = re.search(lon_re, c_line)
		res_val = re.search(dose_re, c_line)
		if (res_Y != None and res_X != None and res_val != None and res_Y.group(1) != "-1"):
			if (rt90):
				try:
					wgs84_coords = pyproj.transform(rt90Proj, wgs84Proj, float(res_X.group(1)), float(res_Y.group(1)))
					lat.append(wgs84_coords[1])
					lon.append(wgs84_coords[0])
					value.append(float(res_val.group(1)))
				except AttributeError, e:
					Log.warning("OpenNKS(): Error when searching for data on line " + str(i + 1) + ": " + str(e))
			else:
				try:
					lat.append(float(res_Y.group(1)) / 1e5)
					lon.append(float(res_X.group(1)) / 1e5)
					value.append(float(res_val.group(1)))
				except AttributeError, e:
					Log.warning("OpenNKS(): Error when searching for data on line " + str(i + 1) + ": " + str(e))
			
		else:
			rejected += 1
	lat = np.array(lat)
	lon = np.array(lon)
	value = np.array(value)
	indices = np.arange(len(lat))
	
	temp_lat = []
	temp_lon = []
	temp_indices = []
	for i in range(len(lat)):
		if (lon[i] > 1):
			temp_lat.append(lat[i])
			temp_lon.append(lon[i])
			temp_indices.append(indices[i])
	temp_lat = np.array(temp_lat)
	temp_lon = np.array(temp_lon)
	temp_indices = np.array(temp_indices)
	lat_func = interp1d(temp_indices, temp_lat, bounds_error = False)
	lon_func = interp1d(temp_indices, temp_lon, bounds_error = False)
	
	error_indices = np.where(lat < 0)
	for i in range(len(error_indices[0])):
		c_index = error_indices[0][i]
		lat[c_index] = lat_func(float(c_index))
		lon[c_index] = lon_func(float(c_index))
	Log.info("OpenNKS(): Returning " + str(len(value)) + " instances of the variable \"" + var_name + "\". " + str(rejected) + " instances were rejected.")
	
	return lat, lon, value

def GetVarsFromNKSFile(file_name):
	Log.info("GetVarsFromNKSFile(): Extracting variable names from file: " + file_name)
	
	if (file_name.find(".csv") != -1):
		return ["None", ]
	
	try:
		in_fl = open(file_name, "r")
		in_line = in_fl.readline()
		in_fl.close()
	except IOError:
		 Log.error("GetVarsFromNKSFile(): Unable to open or read from file: " + file_name)
	value_re = re.compile("([A-Z]+[A-Za-z0-9_\-\\\/]+) -?[0-9.]+E?-?[0-9]*")
	res = value_re.findall(in_line)
	Log.info("GetVarsFromNKSFile(): Found the following variables: " + str(res))
	try:
		res.remove("REC")
		res.remove("TIME_UTC")
		res.remove("X_RT90")
		res.remove("Y_RT90")
	except ValueError:
		Log.warning("GetVarsFromNKSFile(): Unable to remove some variable names.")
	return res

def GetFileTimeDateStr(file_name):
	ret_str = file_name[file_name.rfind("/") + 1:] + ": "
	try:
		in_fl = open(file_name, "r")
		in_lines = in_fl.readlines()
		in_fl.close()
	except IOError:
		Log.error("GetFileTimeDateStr(): Unable to open or read from file: " + file_name)
		return ""
	ret_str += "Created on %s" % time.strftime("%a %b %d, %Y", time.gmtime(os.path.getctime(file_name)))
	value_re = re.compile("TIME_UTC ([0-9]{2})([0-9]{2})([0-9]{2})")
	time_res_1 = value_re.search(in_lines[0])
	if (time_res_1 != None):
		time_res_2 = value_re.search(in_lines[len(in_lines) - 1])
		if (time_res_2 != None):
			ret_str += ". M.-time (UTC) " + time_res_1.group(1) + ":" + time_res_1.group(2) + ":" + time_res_1.group(3) + " to " + time_res_2.group(1) + ":" + time_res_2.group(2) + ":" + time_res_2.group(3)
	return ret_str
	
if __name__ == '__main__':
	Log.InitLogger()
	file = "Bug/PROMENAD1.NAI.NKS"
	
	test = GetVarsFromNKSFile(file)
	lat, lon, value = OpenNKS(file, test[0], rt90 = False)
	from CreateMap import KMZFile, CreatePNGMap
	#CreatePNGMap(lon = lon, lat = lat, value = value, title = "Hej", label = u"SDI Doserate (\u00B5Sv/h)", max_value = value.max(), min_value = value.min(), file_name = "test", outCoordSys = "WGS84", bkg = "None", utmZone = 0)
	#exit()
	gEarth_file = KMZFile("Mon_Fukushima-itate")
	#gEarth_file.addLinePlot(lon = lon, lat = lat, value = value, title = "SDI Line plot")
	gEarth_file.addPointPlot(lon = lon, lat = lat, value = value, title = "SDI Doserate (points)", label = "What label")
	gEarth_file.save()

