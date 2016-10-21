#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python2.7
# encoding: utf-8

from numpy import *
#from Analys import *
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import ticker
from matplotlib.text import Text
from matplotlib import colors
import matplotlib.cm
import glob
import simplekml
import zipfile
import time
import os
import pyproj
import Log
from PIL import Image
from matplotlib.ticker import ScalarFormatter, LogLocator, MultipleLocator
import math

def frexp10(x): 
	exp = int(math.log10(x)) 
	return x / 10**exp, exp 

def CalcLogBase(min_value, max_value):
	min_frexp = frexp10(min_value)
	max_frexp = frexp10(max_value)
	exp_diff = abs(min_frexp[1] - max_frexp[1])
	
	if (exp_diff == 0):
		return 1.1
	elif (exp_diff == 1):
		return 1.2
	elif (exp_diff == 2):
		return 2.0
	else:
		return 4.0

def CalcUTMZone(lon, lat):
	ZoneNumber = int((lon + 180)/6) + 1;
	
	# Southern Norway
	if( lat >= 56.0 and lat < 64.0 and lon >= 3.0 and lon < 12.0):
		ZoneNumber = 32
	
	# Special zones for Svalbard
	if( lat >= 72.0 and lat < 84.0): 
		if ( lon >= 0.0  and lon <  9.0): 
			ZoneNumber = 31
		elif (lon >= 9.0  and lon < 21.0):
			ZoneNumber = 33
		elif (lon >= 21.0 and lon < 33.0):
			ZoneNumber = 35
		elif (lon >= 33.0 and lon < 42.0):
			ZoneNumber = 37
	return ZoneNumber

def getMapName(X, Y, map_type = "ROAD"):
	map_folder_loc = "/Users/jonas/GSD/"
	if os.name == "nt":
		map_folder_loc = "C:/GSD/"
	map_file_locs = [map_folder_loc + "Tatort/", map_folder_loc + "Terrang/", map_folder_loc + "Vag/", map_folder_loc + "Sverige/"]
	X = int(X)
	Y = int(Y)
	# x_temp = X;
	# X = Y;
	# Y = x_temp;
	if (X < 1200000 or X > 1900000 or Y < 6100000 or Y > 7700000):
		Log.error("getMapName(): Invalid coordinates. Exiting.")
		return ""
	
	if ("SWEDEN" == map_type):
		return map_file_locs[3] + "SVK1M.gif"
	# koord = ""
	# sy = ""
	# tot = ""
	# ix = 0
	# iy = 0
	# isq = 0
	
	Cha = ["INDEX_ERROR", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T"]
	subsq = ["INDEX_ERROR", "SV", "SO", "NV", "NO"]
	
	iy = ((Y - 6100000) / 50000)
	ix = ((X - 1200000) / 50000)
	isq = 1
	sy = str(iy + 1)
	if (len(sy) == 1):
		sy = "0" + sy
	if ("CITY" == map_type):
		iys = ((Y - (iy + 122) * 50000) / 5000)
		ixs = ((X - (ix + 24) * 50000) / 5000)
		
		sys = int(iys)
		
		return map_file_locs[0] + "to" + sy + Cha[ix + 1] + str(sys) + Cha[ixs + 1] + ".gif"
	elif ("ROAD" == map_type):
		return map_file_locs[2] + "V" + sy + Cha[ix + 1] + "HK.gif"
	
	if (Y - (iy + 122) * 50000 >= 25000):
		isq = isq + 2
	if (X - (ix + 24) * 50000 >= 25000):
		isq = isq + 1
		
	return map_file_locs[1] + "T" + sy + Cha[ix + 1] + subsq[isq] + "HK.gif"

def getMapPos(X, Y, map_type = "ROAD"):
	mapSize = 0
	if (map_type == "CITY"):
		mapSize = 5000
	elif (map_type == "ROAD"):
		mapSize = 50000
	elif (map_type == "TERRAIN"):
		mapSize = 25000
	elif (map_type == "SWEDEN"):
		return {"xmin":1200000.0, "xmax":1900000.0, "ymin":6100000.0, "ymax":7700000.0}
	ret_dict = {}
	ret_dict["xmin"] = float((int(X) / mapSize) * mapSize)
	ret_dict["xmax"] = float((int(X) / mapSize) * mapSize + mapSize)
	ret_dict["ymin"] = float((int(Y) / mapSize) * mapSize)
	ret_dict["ymax"] = float((int(Y) / mapSize) * mapSize + mapSize)
	return ret_dict

def add_lm_map(map_type, ax):
	current_limits = ax.axis()
	c_x = current_limits[0]
	c_x_m = current_limits[1]
	c_y = current_limits[2]
	c_y_m = current_limits[3]
	pixel_size = 100
	if (map_type == "SWEDEN"):
		map_name = getMapName(c_x, c_y, map_type)
		try:
			img_obj = Image.open(map_name)
		except IOError, e:
			Log.error("add_lm_map(): Unable to open image file. Error was: " + str(e))
			return
		arr_x_start = int((c_x - 1200000.0) / pixel_size)
		arr_x_width = int((c_x_m - c_x) / pixel_size)
		
		arr_y_start = int((c_y - 6105000.0) / pixel_size)
		arr_y_width = int((c_y_m - c_y) / pixel_size)
		
		img_x_min = float((int(c_x) / pixel_size) * pixel_size)
		img_x_max = float((int(c_x_m) / pixel_size) * pixel_size)
		img_y_min = float((int(c_y) / pixel_size) * pixel_size)
		img_y_max = float((int(c_y_m) / pixel_size) * pixel_size)
		
		crop_box = (arr_x_start, img_obj.size[1] - (arr_y_start + arr_y_width), arr_x_start + arr_x_width, img_obj.size[1] - arr_y_start)
		
		croped_image = img_obj.crop(box = crop_box)
		
		img_obj = croped_image.convert("RGB")
		img_arr = asarray(img_obj.getdata(), dtype = uint8).reshape([img_obj.size[0], img_obj.size[1], 3])
		
		#print "new img shape:", img_obj.size
		#print "Pixel coords:", crop_box
		ext = (img_x_min, img_x_max, img_y_min, img_y_max)
		#print "Img. coords:", ext
		ax.imshow(img_arr, extent=ext, zorder = 0)
		ax.axis(current_limits)
		return
	
	add_map_file = []
	map_coords = []
	while (c_y < current_limits[3]):
		c_map_name = getMapName(c_x, c_y, map_type)
		c_coords = getMapPos(c_x, c_y, map_type)
		add_map_file.append(c_map_name)
		map_coords.append(c_coords)
		c_y = c_coords["ymin"]
		c_x = c_coords["xmax"] + 1
		if (c_x > current_limits[1]):
			c_y = c_coords["ymax"] + 1
			c_x = current_limits[0] + 1
	# map_name_list = []
	for i in range(len(add_map_file)):
		c_fl_nm = add_map_file[i]
		c_coords = map_coords[i]
		try:
			img_obj = Image.open(c_fl_nm)
			img_obj = img_obj.convert("RGB")
			img_arr = asarray(img_obj.getdata(), dtype = uint8).reshape([img_obj.size[0], img_obj.size[1], 3])
			ax.imshow(img_arr, extent=(c_coords["xmin"], c_coords["xmax"], c_coords["ymin"], c_coords["ymax"]), zorder = 0)
			Log.info("CreatePNGMap(): Added file \"" + c_fl_nm + "\" to plot.")
		except IOError, e:
			if (map_type == "CITY"):
				Log.info("CreatePNGMap(): No city map file with name \"" + c_fl_nm + "\".")
			else:
				Log.error("CreatePNGMap(): Unable to open map file \"" + c_fl_nm + "\". Error message was: " + str(e))
				break
	ax.axis(current_limits)

def CreatePNGMap(lon, lat, value, title, label, max_value, min_value, file_name, outCoordSys, bkg, log_scale = False, stats = None):
	if (log_scale):
		if (min_value == None):
			if (value.min() <= 0):
				Log.info("CreatePNGMap(): Data contains negative and/or zero values which can not be plotted on log-scale. Plotting on linear scale.")
				log_scale = False
		else:
			if (min_value <= 0):
				Log.info("CreatePNGMap(): Minimum value set to negative or zero value which can not be plotted on log-scale. Plotting on linear scale.")
				log_scale = False
	sorted_indices = value.argsort()
	data = value[sorted_indices]
	lat = lat[sorted_indices]
	lon = lon[sorted_indices]
	
	fig = Figure(figsize=(12,8))
	canvas = FigureCanvas(fig)
	
	ax = fig.add_subplot(111)
	ax.set_title(title)
	#ax.axis("scaled")
	ax.set_aspect('equal', 'datalim')
	
	wgs84Proj = pyproj.Proj(proj="lonlat", ellps="WGS84", datum="WGS84")
	rt90Proj = pyproj.Proj("+proj=tmerc +lat_0=0 +lon_0=15.8082777778 +k=1 +x_0=1500000 +y_0=0 +ellps=bessel +towgs84=414.1,41.3,603.1,-0.855,2.141,-7.023,0 +units=m +no_defs")
	if (outCoordSys == "WGS84"):
		pass
	elif (outCoordSys == "RT90"):
		lon, lat = pyproj.transform(wgs84Proj, rt90Proj, lon, lat)
	elif (outCoordSys == "UTM"):
		used_utm_zone = CalcUTMZone(lon = lon[0], lat = lat[0])
		utmProj = pyproj.Proj("+proj=utm +zone=" + str(used_utm_zone) + " +to_meter=1")
		lon, lat = pyproj.transform(wgs84Proj, utmProj, lon, lat)
		Log.info("Creating map using UTM Zone " + str(used_utm_zone))
	else:
		Log.error("CreatePNGMap(): Unknown output coordinate system. Exiting.")
		return
	
	cmap = colors.ListedColormap(['blue', 'green', 'yellow', 'orange', 'red'])
	bounds = [0.0, 1.0 , 5.0, 10.0, 20.0, 1000.0]
	norm = colors.BoundaryNorm(bounds, cmap.N)
	
	if (log_scale):
		CS = ax.scatter(lon, lat, c = data, s = 40, cmap=matplotlib.cm.jet, vmin = min_value, vmax=max_value, lw = 0, zorder = 10, norm = matplotlib.colors.LogNorm())
	else:
		#CS = ax.scatter(lon, lat, c = data, s = 40, cmap=matplotlib.cm.jet, vmin = min_value, vmax=max_value, lw = 0, zorder = 10)
		CS = ax.scatter(lon, lat, c = data, s = 40, cmap=cmap, lw = 0, norm = norm, zorder = 10)
	#ax.axis([lon.min() * 0.9999, lon.max() * 1.0001, lat.min() * 0.9999, lat.max() * 1.0001])
	ticks_format = "%3.4f"
	if (outCoordSys == "RT90" or outCoordSys == "UTM"):
		ticks_format = "%i"
	axis_format = ticker.FormatStrFormatter(ticks_format)
	ax.yaxis.set_major_formatter(axis_format)
	ax.xaxis.set_major_formatter(axis_format)
	current_limits = ax.axis()
	#add maps
	if (outCoordSys == "RT90" and bkg.find("LM") == 0):
		map_type = ""
		if (bkg.find("City") != -1):
			map_type = "CITY"
		elif (bkg.find("Terrain") != -1):
			map_type = "TERRAIN"
		elif (bkg.find("Road") != -1):
			map_type = "ROAD"
		elif (bkg.find("Sweden") != -1):
			map_type = "SWEDEN"
		add_lm_map(map_type, ax)
	elif (bkg == "OSM"):
		bounds_string = "--bounds=" + str(current_limits[0]) + "," + str(current_limits[2]) + "," + str(current_limits[1]) + "," + str(current_limits[3])
		bounds_coord_string = "--boundsCoordSys=" + outCoordSys
		zone_string = "--utm_zone=33"
		if (outCoordSys == "UTM"):
			zone_string = "--utm_zone=" + str(used_utm_zone)
		output_string = "--output=tempMap.png"
		scale_string = "--scale=3.0"
		try:
			osmMapOut = sp.check_output(["/opt/local/bin/python2.7", "bkgMapGenerator.py", bounds_string, bounds_coord_string, zone_string, scale_string, output_string])
		except sp.CalledProcessError, e:
			print "Error when creating map file:", e
		partsFirst = osmMapOut.split(":")[1].strip()
		cornerParts = partsFirst.split(" ")
		try:
			img_obj = Image.open("tempMap.png")
		except IOError, e:
			Log.error("CreatePNGMap(): Unable to open map file \"" + "tempMap.png" + "\". Error message was: " + str(e))
			return
		img_obj = img_obj.convert("RGB")
		img_arr = asarray(img_obj.getdata(), dtype = uint8).reshape([img_obj.size[0], img_obj.size[1], 3])
		ax.imshow(img_arr, extent=(float(cornerParts[0]), float(cornerParts[2]), float(cornerParts[1]), float(cornerParts[3])), zorder = 0)
		ax.axis(current_limits)
	
	if (log_scale):
		if (min_value == None):
			min_value = value.min()
		if (max_value == None):
			max_value = value.max()
		#print min_value
		#print max_value
		used_formater = ScalarFormatter()
		used_locator = LogLocator(base = CalcLogBase(min_value, max_value))
		cb = fig.colorbar(CS, format = used_formater)
		cb.locator = used_locator
		cb.update_ticks()
	else:
		cb = fig.colorbar(CS, ticks = [0, 1, 5, 10, 20])
	
	cb.set_label(label)
	if (outCoordSys == "RT90" or outCoordSys == "UTM"):
		ax.set_xlabel("Easting")
		ax.set_ylabel("Northing")
	else:
		ax.set_xlabel("Longitude")
		ax.set_ylabel("Latitude")
	
	if (stats != None):
		ax.text(0, 0, stats, transform = fig.transFigure, horizontalalignment = "left", verticalalignment='bottom', fontsize = "xx-small")
	
	ax.grid()
	canvas.print_figure(file_name + ".png")

def overlay_point_plot(data, lat, lon, name, min_value, max_value, title, label, log_scale = False):
	if (log_scale):
		if (min_value == None):
			if (value.min() <= 0):
				Log.info("overlay_point_plot(): Data contains negative and/or zero values which can not be plotted on log-scale. Plotting on linear scale.")
				log_scale = False
		else:
			if (min_value <= 0):
				Log.info("overlay_point_plot(): Minimum value set to negative or zero value which can not be plotted on log-scale. Plotting on linear scale.")
				log_scale = False
	sorted_indices = data.argsort()
	data = data[sorted_indices]
	lat = lat[sorted_indices]
	lon = lon[sorted_indices]
	
	fig = Figure(figsize=(40, 40), frameon = False)
	canvas = FigureCanvas(fig)
	
	ax = fig.add_axes([0.00,0.00,1.0,1.0])
	#ax = fig.add_axes()
	
	fig.patch.set_alpha(0.0)
	ax.patch.set_alpha(0.0)
	
	# m = Basemap(llcrnrlon=lon.min() * 0.9999,llcrnrlat=lat.min() * 0.9999,urcrnrlon=lon.max() * 1.0001,urcrnrlat=lat.max() * 1.0001, projection="cyl", resolution ='i', ax=ax, fix_aspect=False)
	# 
	# x, y = m(lat, lon)
	# 
	# CS = m.scatter(y, x, c = data, s = 150, cmap=matplotlib.cm.jet, vmax=max_value)
	
	cmap = colors.ListedColormap(['blue', 'green', 'yellow', 'orange', 'red'])
	bounds = [0.0, 1.0 , 5.0, 10.0, 20.0, 1000.0]
	norm = colors.BoundaryNorm(bounds, cmap.N)
	
	if (log_scale):
		CS = ax.scatter(lon, lat, c = data, s = 150, cmap=matplotlib.cm.jet, vmin = min_value, vmax=max_value, lw = 0, zorder = 10, norm = matplotlib.colors.LogNorm())
	else:
		#CS = ax.scatter(lon, lat, c = data, s = 150, cmap=matplotlib.cm.jet, vmin = min_value, vmax=max_value, lw = 0, zorder = 10)
		CS = ax.scatter(lon, lat, c = data, s = 150, cmap=cmap, norm = norm, lw = 0, zorder = 10)
	ax.axis([lon.min() * 0.9999, lon.max() * 1.0001, lat.min() * 0.9999, lat.max() * 1.0001])
	canvas.print_figure(name)
	
	fig2 = Figure(figsize=(8,0.75), dpi = 600)
	canvas2 = FigureCanvas(fig2)
	ax1 = fig2.add_axes([0.05, 0.7, 0.90, 0.25])
	#fig2.patch.set_alpha(0.0)
	#ax1.patch.set_alpha(0.0)
	cmap = matplotlib.cm.jet
	
	if (log_scale):
		used_formater = ScalarFormatter()
		used_locator = LogLocator(base = CalcLogBase(min_value, max_value))
		cb1 = matplotlib.colorbar.Colorbar(ax = ax1, mappable=CS, orientation='horizontal', format = used_formater)
		cb1.locator = used_locator
		cb1.update_ticks()
	else:
		cb1 = matplotlib.colorbar.Colorbar(ax = ax1, mappable=CS, orientation='horizontal', ticks = [0, 1, 5, 10, 20])
	
	cb1.set_label(label)
	
	canvas2.print_figure("cbar" + name)

def ColorToString(colors):
	ret_str = "ff"
	red_val = int(colors[0] * 255.0)
	green_val = int(colors[1] * 255.0)
	blue_val = int(colors[2] * 255.0)
	red = "%0.2x" % red_val
	green = "%0.2x" % green_val
	blue = "%0.2x" % blue_val
	ret_str = ret_str + blue + green + red
	return ret_str

def ValueToStringColor(value):
	if (value < 1.0):
		return "fff42109"
	elif (value < 5.0):
		return "ff257f00"
	elif (value < 10.0):
		return "ff56fdfe"
	elif (value < 20.0):
		return "ff39a3ff"
	return "ff1900ff"

class KMZFile(object):
	def __init__(self, file_name):
		super(KMZFile, self).__init__()
		self.file_name = file_name
		self.line_data = []
		self.point_data = []
		self.native_point_data = []
		self.log_scale = False
	
	def addLinePlot(self, lon, lat, value, title, label, max_value = None, min_value = None):
		if (max_value == None):
			max_value = value.max()
		if (min_value == None):
			min_value = value.min()
		self.line_data.append({"lon":lon, "lat":lat, "value":value, "title":title, "min_value":min_value, "max_value":max_value, "label":label})
	
	def addPointPlot(self, lon, lat, value, title, label, max_value = None, min_value = None):
		if (max_value == None):
			max_value = value.max()
		if (min_value == None):
			min_value = value.min()
		self.point_data.append({"lon":lon, "lat":lat, "value":value, "title":title, "max_value":max_value, "min_value":min_value, "label":label})
	
	def addNativePointPlot(self, lon, lat, value, title, label, max_value = None, min_value = None):
		if (max_value == None):
			max_value = value.max()
		if (min_value == None):
			min_value = value.min()
		self.native_point_data.append({"lon":lon, "lat":lat, "value":value, "title":title, "max_value":max_value, "label":label, "min_value":min_value})
	
	def save(self):
		if (self.log_scale):
			for p in self.point_data:
				if (p["min_value"] <= 0):
					Log.info("KMZFile::save(): Minimum value set to negative or zero value which can not be plotted on log-scale. Plotting on linear scale.")
					self.log_scale = False
					break
		kml = simplekml.Kml()
		file_nr = 0
		for dt in self.line_data:
			overlay_line_plot(data = dt["value"], lat = dt["lat"], lon = dt["lon"], name = str(file_nr) + ".png", max_value = dt["max_value"], title = dt["title"])
			file_nr += 1
			ground = kml.newgroundoverlay(name=dt["title"])
			ground.icon.href = overlay_file_name
			ground.latlonbox.north = dt["lat"].max() * 1.0001
			ground.latlonbox.south = dt["lat"].min() * 0.9999
			ground.latlonbox.east =  dt["lon"].max() * 1.0001
			ground.latlonbox.west =  dt["lon"].min() * 0.9999
		
		zoom_levels = [{"minlod":2048, "maxlod":-1, "scale":1.0}, {"minlod":1024, "maxlod":2048, "scale":0.5}, {"minlod":0, "maxlod":1024, "scale":0.25}]
		
		for dt in self.native_point_data:
			sorted_indices = dt["value"].argsort()
			c_data = dt["value"][sorted_indices].copy()
			c_lon = dt["lon"][sorted_indices].copy()
			c_lat = dt["lat"][sorted_indices].copy()
			max_indices = where(c_data > dt["max_value"])
			min_indices = where(c_data < dt["min_value"])
			c_data[max_indices] = dt["max_value"]
			c_data[min_indices] = dt["min_value"]
			#c_map = matplotlib.cm.jet
			if (self.log_scale):
				c_data = log(c_data)
			# c_data = c_data + c_data.min()
			# c_data = c_data - c_data.min()
			# c_data = c_data / c_data.max()
			base_folder = kml.newfolder(name = dt["title"])
			for zm in zoom_levels:
				bounding_box = simplekml.LatLonBox(south = c_lat.min(), north = c_lat.max(), west = c_lon.min(), east = c_lon.max())
				c_lod = simplekml.Lod(minlodpixels=zm["minlod"], maxlodpixels=zm["maxlod"], minfadeextent=0, maxfadeextent=0)
				c_region = simplekml.Region(latlonaltbox = bounding_box, lod = c_lod)
				c_folder = base_folder.newfolder(name = dt["title"] + ", scale=" + str(zm["scale"]), region = c_region)
				for i in range(len(c_data)):
					pnt = c_folder.newpoint(coords=[(c_lon[i], c_lat[i]),], altitudemode = simplekml.AltitudeMode.clamptoground) #relativetoground
					#pnt.style.iconstyle.color = ColorToString(c_map(c_data[i]))
					pnt.style.iconstyle.color = ValueToStringColor(c_data[i])
					pnt.style.iconstyle.icon.href = 'icon18.png'
					pnt.style.iconstyle.scale = zm["scale"]
		
		for dt in self.point_data:
			overlay_file_name = str(file_nr) + ".png"
			overlay_point_plot(dt["value"], lat = dt["lat"], lon = dt["lon"], name = overlay_file_name, max_value = dt["max_value"], min_value = dt["min_value"], title = dt["title"], label = dt["label"], log_scale = self.log_scale)
			file_nr += 1
			ground = kml.newgroundoverlay(name=dt["title"])
			ground.icon.href = overlay_file_name
			ground.latlonbox.north = dt["lat"].max() * 1.0001
			ground.latlonbox.south = dt["lat"].min() * 0.9999
			ground.latlonbox.east =  dt["lon"].max() * 1.0001
			ground.latlonbox.west =  dt["lon"].min() * 0.9999
			
			ground_bar = kml.newscreenoverlay(name="Color bar " + dt["title"])
			ground_bar.icon.href = "cbar" + overlay_file_name
			ground_bar.overlayxy = simplekml.OverlayXY(x=0,y=1,xunits=simplekml.Units.fraction,
			                                       yunits=simplekml.Units.fraction)
			ground_bar.screenxy = simplekml.ScreenXY(x=15,y=15,xunits=simplekml.Units.pixel,
			                                     yunits=simplekml.Units.insetpixels)
			ground_bar.size.x = -1
			ground_bar.size.y = -1
			ground_bar.size.xunits = simplekml.Units.fraction
			ground_bar.size.yunits = simplekml.Units.fraction
			# ground_bar = kml.newgroundoverlay(name="Color bar " + dt["title"], altitudemode = simplekml.AltitudeMode.absolute)
# 			ground_bar.icon.href = "cbar" + overlay_file_name
# 			lat_diff = dt["lat"].max() - dt["lat"].min()
# 			lon_diff = dt["lon"].max() - dt["lon"].min()
# 			ground_bar.altitude = 2000
# 			ground_bar.latlonbox.north = dt["lat"].max()
# 			ground_bar.latlonbox.south = dt["lat"].max() - lat_diff * 0.05
# 			ground_bar.latlonbox.east =  dt["lon"].max() - lon_diff * 0.3
# 			ground_bar.latlonbox.west =  dt["lon"].min() + lon_diff * 0.3
		
		kml.save(self.file_name + ".kml")
		
		z_file = zipfile.ZipFile(self.file_name + ".kmz", "w")
		
		now_time = time.localtime(time.time())
		
		for i in range(file_nr):
			zip_fl_info = zipfile.ZipInfo(str(i) + ".png", [now_time.tm_year, now_time.tm_mon, now_time.tm_mday, now_time.tm_hour, now_time.tm_min, now_time.tm_sec])
			zip_fl_data_fl = open(str(i) + ".png", "rb")
			zip_fl_data = zip_fl_data_fl.read()
			zip_fl_data_fl.close()
			os.remove(str(i) + ".png")
			z_file.writestr(zip_fl_info, zip_fl_data)
			
			zip_fl_info = zipfile.ZipInfo("cbar" + str(i) + ".png", [now_time.tm_year, now_time.tm_mon, now_time.tm_mday, now_time.tm_hour, now_time.tm_min, now_time.tm_sec])
			zip_fl_data_fl = open("cbar" + str(i) + ".png", "rb")
			zip_fl_data = zip_fl_data_fl.read()
			zip_fl_data_fl.close()
			os.remove("cbar" + str(i) + ".png")
			z_file.writestr(zip_fl_info, zip_fl_data)
		
		zip_fl_info = zipfile.ZipInfo("main.kml", [now_time.tm_year, now_time.tm_mon, now_time.tm_mday, now_time.tm_hour, now_time.tm_min, now_time.tm_sec])
		zip_fl_data_fl = open(self.file_name + ".kml", "rb")
		zip_fl_data = zip_fl_data_fl.read()
		zip_fl_data_fl.close()
		os.remove(self.file_name + ".kml")
		z_file.writestr(zip_fl_info, zip_fl_data)
		
		zip_fl_info = zipfile.ZipInfo("icon18.png", [now_time.tm_year, now_time.tm_mon, now_time.tm_mday, now_time.tm_hour, now_time.tm_min, now_time.tm_sec])
		zip_fl_data_fl = open("icon18.png", "rb")
		zip_fl_data = zip_fl_data_fl.read()
		zip_fl_data_fl.close()
		z_file.writestr(zip_fl_info, zip_fl_data)
		
		z_file.close()

	
if __name__ == '__main__':
	lat = random.ranf(1000) + 56.0
	lon = random.ranf(1000) + 14.0
	val = random.ranf(1000) * 10
	CreatePNGMap(lon = lon, lat = lat, value = val, title = "No title", label = "No label", max_value = None, min_value = None, file_name = "Test_map", outCoordSys = "RT90", bkg = "WHITE", log_scale = True, stats = "Test stats")

