#!/opt/local/bin/python2.7

import mapnik

import sys, os

# Set up projections
# spherical mercator (most common target map projection of osm data imported with osm2pgsql)
#merc = mapnik.Projection('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over')
#merc = mapnik.Projection('+proj=tmerc +lat_0=0 +lon_0=15.8082777778 +k=1 +x_0=1500000 +y_0=0 +ellps=bessel +towgs84=414.1,41.3,603.1,-0.855,2.141,-7.023,0 +units=m +no_defs') # RT-90
merc = mapnik.Projection('+proj=utm +zone=36 +to_meter=1')


# long/lat in degrees, aka ESPG:4326 and "WGS 84" 
# can also be constructed as:
#longlat = mapnik.Projection('+init=epsg:4326')

# ensure minimum mapnik version

def main():
	bounds = None
	target_coord = None
	scale = 1.0
	utm_zone = None
	height = 1000
	width = 1000
	outputFile = None
	try:
		for a in sys.argv:
			if (a.find("--bounds=") != -1):
				boundsPart = a.split("=")[1]
				corners = boundsPart.split(",")
				bounds = (float(corners[0]), float(corners[1]), float(corners[2]), float(corners[3]))
			elif (a.find("--utm_zone=") != -1):
				zonePart = a.split("=")[1]
				utm_zone = int(zonePart)
			elif (a.find("--output=") != -1):
				outputFile = a.split("=")[1]
			elif (a.find("--height=") != -1):
				height = int(a.split("=")[1])
			elif (a.find("--width=") != -1):
				width = int(a.split("=")[1])
			elif (a.find("--scale=") != -1):
				scale = float(a.split("=")[1])
			elif (a.find("--boundsCoordSys=") != -1):
				target_coord = a.split("=")[1]
				if (not (target_coord == "WGS84" or target_coord == "RT90" or target_coord == "UTM")):
					print "Incorrect coordinate system."
					exit(1)
	except:
		print "Incorrect argument."
		exit(1)
	if (bounds == None or target_coord == None or outputFile == None):
		print "Missing argument."
		exit(1)
	
	if (target_coord == "UTM" and utm_zone == None):
		print "Missing UTM zone."
		exit(1)
			
	if not hasattr(mapnik,'mapnik_version') and not mapnik.mapnik_version() >= 600:
		raise SystemExit('This script requires Mapnik >=0.6.0)')
	
	origin = mapnik.Projection("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
	target = None
	if (target_coord == "WGS84"):
		target = origin
	elif (target_coord == "RT90"):
		target = mapnik.Projection('+proj=tmerc +lat_0=0 +lon_0=15.8082777778 +k=1 +x_0=1500000 +y_0=0 +ellps=bessel +towgs84=414.1,41.3,603.1,-0.855,2.141,-7.023,0 +units=m +no_defs')
	elif (target_coord == "UTM"):
		target = mapnik.Projection("+proj=utm +zone=" + str(utm_zone) + " +to_meter=1")
	else:
		print "Unknown coordinate system."
		exit(1)
	try:
		mapfile = os.environ['MAPNIK_MAP_FILE']
	except KeyError:
		mapfile = "my_styling.xml"
	#---------------------------------------------------

	m = mapnik.Map(width, height)
	mapnik.load_map(m,mapfile)
	
	m.srs = target.params()

	if hasattr(mapnik,'Box2d'):
		bbox = mapnik.Box2d(*bounds)
	else:
		bbox = mapnik.Envelope(*bounds)

	#transform = mapnik.ProjTransform(origin,target)
	#target_bbox = transform.forward(bbox)
	target_bbox = bbox
	
	m.zoom_to_box(target_bbox)
	used_bbox = m.envelope()
	print "Used envelope:", used_bbox[0], used_bbox[1], used_bbox[2], used_bbox[3]
	
	# render the map to an image
	im = mapnik.Image(width, height)
	mapnik.render(m, im, 5.0)
	im.save(outputFile,'png')

def main2():
	print "Number of arguments:", len(sys.argv)
	print sys.argv

if __name__ == "__main__":
	main()
